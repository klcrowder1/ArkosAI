"""Timeline processor for Arkos AI."""

import logging
import queue
import threading
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MpEvent
from typing import Dict, List, Any, Optional

from arkos.config import FrigateConfig
from arkos.events.types import (
    EventData,
    EventStateEnum,
    EventTypeEnum,
    TrackedObjectEventData,
)
from arkos.models import Timeline
from arkos.util.builtin import to_relative_box

logger = logging.getLogger(__name__)


class TimelineProcessor(threading.Thread):
    """Process timeline events and update the database."""
    
    def __init__(
        self,
        config: FrigateConfig,
        queue: Queue,
        stop_event: MpEvent,
    ) -> None:
        """Initialize the timeline processor.
        
        Args:
            config: Arkos configuration
            queue: Queue for timeline events
            stop_event: Event to signal thread to stop
        """
        super().__init__(name="timeline_processor")
        self.config = config
        self.queue = queue
        self.stop_event = stop_event
        self.pre_event_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def run(self) -> None:
        """Run the timeline processor thread."""
        while not self.stop_event.is_set():
            try:
                (
                    camera,
                    input_type,
                    event_type,
                    prev_event_data,
                    event_data,
                ) = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            if input_type == EventTypeEnum.TRACKED_OBJECT:
                # None prev_event_data is only allowed for the start of an event
                if event_type != EventStateEnum.START and prev_event_data is None:
                    continue

                self.handle_object_detection(
                    camera, event_type, prev_event_data, event_data
                )
            elif input_type == EventTypeEnum.API:
                self.handle_api_entry(camera, event_type, event_data)
            elif input_type == EventTypeEnum.AUDIO:
                self.handle_audio_entry(camera, event_type, event_data)
    
    def insert_or_save(
        self,
        entry: Dict[str, Any],
        prev_event_data: Optional[Dict[str, Any]],
        event_data: Dict[str, Any],
    ) -> None:
        """Insert into db or cache.
        
        Args:
            entry: Timeline entry
            prev_event_data: Previous event data
            event_data: Current event data
        """
        id = entry[Timeline.source_id]
        if not event_data.get("has_clip", False) and not event_data.get("has_snapshot", False):
            # the related event has not been saved yet, should be added to cache
            if id in self.pre_event_cache.keys():
                self.pre_event_cache[id].append(entry)
            else:
                self.pre_event_cache[id] = [entry]
        else:
            # the event is saved, insert to db and insert cached into db
            if id in self.pre_event_cache.keys():
                for e in self.pre_event_cache[id]:
                    Timeline.insert(e).execute()

                self.pre_event_cache.pop(id)

            Timeline.insert(entry).execute()
    
    def handle_object_detection(
        self,
        camera: str,
        event_type: str,
        prev_event_data: Dict[str, Any],
        event_data: Dict[str, Any],
    ) -> bool:
        """Handle object detection timeline events.
        
        Args:
            camera: Camera name
            event_type: Event type
            prev_event_data: Previous event data
            event_data: Current event data
            
        Returns:
            bool: True if the event was handled
        """
        save = False
        camera_config = self.config.cameras[camera]
        event_id = event_data["id"]

        # Convert to EventData objects
        current_event = TrackedObjectEventData.from_dict(event_data)
        prev_event = None if prev_event_data is None else TrackedObjectEventData.from_dict(prev_event_data)

        timeline_entry = {
            Timeline.timestamp: current_event.data.get("frame_time", current_event.start_time),
            Timeline.camera: camera,
            Timeline.source: "tracked_object",
            Timeline.source_id: event_id,
            Timeline.data: {
                "box": to_relative_box(
                    camera_config.detect.width,
                    camera_config.detect.height,
                    current_event.box,
                ),
                "label": current_event.label,
                "sub_label": current_event.sub_label,
                "region": to_relative_box(
                    camera_config.detect.width,
                    camera_config.detect.height,
                    current_event.region,
                ),
                "attribute": "",
            },
        }

        # update sub labels for existing entries that haven't been added yet
        if (
            prev_event is not None
            and prev_event.sub_label != current_event.sub_label
            and event_id in self.pre_event_cache.keys()
        ):
            for e in self.pre_event_cache[event_id]:
                e[Timeline.data]["sub_label"] = current_event.sub_label

        if event_type == EventStateEnum.START:
            timeline_entry[Timeline.class_type] = "visible"
            save = True
        elif event_type == EventStateEnum.UPDATE:
            if (
                prev_event is not None
                and len(prev_event.current_zones) < len(current_event.current_zones)
                and not current_event.stationary
            ):
                timeline_entry[Timeline.class_type] = "entered_zone"
                timeline_entry[Timeline.data]["zones"] = current_event.current_zones
                save = True
            elif prev_event is not None and prev_event.stationary != current_event.stationary:
                timeline_entry[Timeline.class_type] = (
                    "stationary" if current_event.stationary else "active"
                )
                save = True
            elif (
                prev_event is not None
                and (not prev_event.attributes or prev_event.attributes == {})
                and current_event.attributes
                and current_event.attributes != {}
            ):
                timeline_entry[Timeline.class_type] = "attribute"
                timeline_entry[Timeline.data]["attribute"] = list(
                    current_event.attributes.keys()
                )[0]
                save = True
        elif event_type == EventStateEnum.END:
            timeline_entry[Timeline.class_type] = "gone"
            save = True

        if save:
            self.insert_or_save(timeline_entry, prev_event_data, event_data)
            return True

        return False
    
    def handle_api_entry(
        self,
        camera: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> bool:
        """Handle API timeline events.
        
        Args:
            camera: Camera name
            event_type: Event type
            event_data: Event data
            
        Returns:
            bool: True if the event was handled
        """
        if event_type != EventStateEnum.START:
            return False

        if event_data.get("type", "api") == "audio":
            timeline_entry = {
                Timeline.class_type: "heard",
                Timeline.timestamp: event_data["start_time"],
                Timeline.camera: camera,
                Timeline.source: "audio",
                Timeline.source_id: event_data["id"],
                Timeline.data: {
                    "label": event_data["label"],
                    "sub_label": event_data.get("sub_label"),
                },
            }
        else:
            timeline_entry = {
                Timeline.class_type: "external",
                Timeline.timestamp: event_data["start_time"],
                Timeline.camera: camera,
                Timeline.source: "api",
                Timeline.source_id: event_data["id"],
                Timeline.data: {
                    "label": event_data["label"],
                    "sub_label": event_data.get("sub_label"),
                },
            }

        Timeline.insert(timeline_entry).execute()
        return True
    
    def handle_audio_entry(
        self,
        camera: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> bool:
        """Handle audio timeline events.
        
        Args:
            camera: Camera name
            event_type: Event type
            event_data: Event data
            
        Returns:
            bool: True if the event was handled
        """
        if event_type != EventStateEnum.START:
            return False

        timeline_entry = {
            Timeline.class_type: "heard",
            Timeline.timestamp: event_data["start_time"],
            Timeline.camera: camera,
            Timeline.source: "audio",
            Timeline.source_id: event_data["id"],
            Timeline.data: {
                "label": event_data["label"],
                "sub_label": event_data.get("sub_label"),
                "dBFS": event_data.get("dBFS", 0),
            },
        }

        Timeline.insert(timeline_entry).execute()
        return True
