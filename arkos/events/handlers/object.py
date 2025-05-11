"""Handler for tracked object events."""

import logging
from typing import Any, Dict, List, Optional

from arkos.config import FrigateConfig
from arkos.events.handlers import EventHandler
from arkos.events.types import (
    EventData,
    EventStateEnum,
    EventTypeEnum,
    TrackedObjectEventData,
    create_event_data,
)
from arkos.models import Event
from arkos.util.builtin import to_relative_box

logger = logging.getLogger(__name__)


class TrackedObjectHandler(EventHandler):
    """Handler for tracked object events."""
    
    def __init__(self, config: FrigateConfig):
        """Initialize the tracked object handler.
        
        Args:
            config: Frigate configuration
        """
        self.config = config
    
    def handle_event(
        self,
        event_type: EventTypeEnum,
        event_state: EventStateEnum,
        camera: str,
        frame_name: str,
        event_data: Dict[str, Any],
        prev_event_data: Optional[Dict[str, Any]] = None,
    ) -> TrackedObjectEventData:
        """Handle a tracked object event.
        
        Args:
            event_type: Type of event
            event_state: State of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
            prev_event_data: Previous event data
            
        Returns:
            TrackedObjectEventData: Processed event data
        """
        # Convert to TrackedObjectEventData
        current_event = TrackedObjectEventData.from_dict(event_data)
        
        # If this is the first message, just return it
        if event_state == EventStateEnum.START or prev_event_data is None:
            return current_event
        
        # Convert previous event data to TrackedObjectEventData
        prev_event = TrackedObjectEventData.from_dict(prev_event_data)
        
        # Keep these from being set back to false because the event
        # may have started while recordings/snapshots/alerts/detections were enabled
        # this would be an issue for long running events
        if prev_event.has_clip:
            current_event.has_clip = True
        if prev_event.has_snapshot:
            current_event.has_snapshot = True
        
        return current_event
    
    def should_update_db(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event should be updated in the database.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event should be updated in the database
        """
        # Cast to TrackedObjectEventData
        prev = prev_event
        current = current_event
        
        if current.has_clip or current.has_snapshot:
            # if this is the first time has_clip or has_snapshot turned true
            if not prev.has_clip and not prev.has_snapshot:
                return True
            # or if any of the following values changed
            if (
                prev.top_score != current.top_score
                or prev.zones != current.zones
                or prev.end_time != current.end_time
                or prev.data.get("average_estimated_speed")
                != current.data.get("average_estimated_speed")
                or prev.data.get("velocity_angle") != current.data.get("velocity_angle")
                or prev.data.get("recognized_license_plate")
                != current.data.get("recognized_license_plate")
                or prev.data.get("path_data") != current.data.get("path_data")
            ):
                return True
        return False
    
    def should_update_state(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event state should be updated.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event state should be updated
        """
        # Cast to TrackedObjectEventData
        prev = prev_event
        current = current_event
        
        if isinstance(prev, TrackedObjectEventData) and isinstance(current, TrackedObjectEventData):
            if prev.stationary != current.stationary:
                return True

            if prev.attributes != current.attributes:
                return True

            if prev.sub_label != current.sub_label:
                return True

            if len(prev.current_zones) < len(current.current_zones):
                return True

        return False
    
    def prepare_for_db(self, event: TrackedObjectEventData, camera: str) -> Dict[str, Any]:
        """Prepare event data for database insertion.
        
        Args:
            event: Event data
            camera: Camera name
            
        Returns:
            Dict[str, Any]: Event data prepared for database insertion
        """
        camera_config = self.config.cameras[camera]
        width = camera_config.detect.width
        height = camera_config.detect.height
        first_detector = list(self.config.detectors.values())[0]

        start_time = event.start_time
        end_time = event.end_time
        
        # score of the snapshot
        score = (
            None
            if event.data.get("snapshot") is None
            else event.data["snapshot"]["score"]
        )
        
        # detection region in the snapshot
        region = (
            None
            if event.data.get("snapshot") is None
            else to_relative_box(
                width,
                height,
                event.data["snapshot"]["region"],
            )
        )
        
        # bounding box for the snapshot
        box = (
            None
            if event.data.get("snapshot") is None
            else to_relative_box(
                width,
                height,
                event.data["snapshot"]["box"],
            )
        )

        attributes = (
            None
            if event.data.get("snapshot") is None
            else [
                {
                    "box": to_relative_box(
                        width,
                        height,
                        a["box"],
                    ),
                    "label": a["label"],
                    "score": a["score"],
                }
                for a in event.data["snapshot"]["attributes"]
            ]
        )

        db_event = {
            Event.id: event.id,
            Event.label: event.label,
            Event.camera: camera,
            Event.start_time: start_time,
            Event.end_time: end_time,
            Event.zones: event.zones,
            Event.thumbnail: event.thumbnail,
            Event.has_clip: event.has_clip,
            Event.has_snapshot: event.has_snapshot,
            Event.model_hash: first_detector.model.model_hash,
            Event.model_type: first_detector.model.model_type,
            Event.detector_type: first_detector.type,
            Event.data: {
                "box": box,
                "region": region,
                "score": score,
                "top_score": event.top_score,
                "attributes": attributes,
                "average_estimated_speed": event.data.get("average_estimated_speed"),
                "velocity_angle": event.data.get("velocity_angle"),
                "type": "object",
                "max_severity": event.severity,
                "path_data": event.data.get("path_data"),
                "detection_time": event.data.get("detection_time"),
                "duration": event.data.get("duration"),
                "category": event.category,
                "confidence": event.confidence,
                "tags": event.tags,
                "description": event.description,
                "source": event.source,
                "related_events": event.related_events,
                "retention_days": event.retention_days,
                "metadata": event.metadata,
            },
        }

        # only overwrite the sub_label in the database if it's set
        if event.sub_label is not None:
            db_event[Event.sub_label] = event.sub_label[0]
            db_event[Event.data]["sub_label_score"] = event.sub_label[1]

        # only overwrite the recognized_license_plate in the database if it's set
        if event.data.get("recognized_license_plate") is not None:
            db_event[Event.data]["recognized_license_plate"] = event.data[
                "recognized_license_plate"
            ][0]
            db_event[Event.data]["recognized_license_plate_score"] = event.data[
                "recognized_license_plate"
            ][1]

        return db_event
