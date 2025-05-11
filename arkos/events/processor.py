"""Event processor for Arkos AI."""

import logging
import threading
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MpEvent
from typing import Dict, Optional, Tuple, Any

from arkos.comms.events_updater import EventEndPublisher, EventUpdateSubscriber
from arkos.config import FrigateConfig
from arkos.events.handlers.api import ApiEventHandler
from arkos.events.handlers.audio import AudioEventHandler
from arkos.events.handlers.object import TrackedObjectHandler
from arkos.events.types import EventData, EventStateEnum, EventTypeEnum
from arkos.models import Event

logger = logging.getLogger(__name__)


class EventProcessor(threading.Thread):
    """Process events from various sources and update the database."""
    
    def __init__(
        self,
        config: FrigateConfig,
        timeline_queue: Queue,
        stop_event: MpEvent,
    ):
        """Initialize the event processor.
        
        Args:
            config: Arkos configuration
            timeline_queue: Queue for timeline events
            stop_event: Event to signal thread to stop
        """
        super().__init__(name="event_processor")
        self.config = config
        self.timeline_queue = timeline_queue
        self.events_in_process: Dict[str, EventData] = {}
        self.stop_event = stop_event

        # Initialize event handlers
        self.handlers = {
            EventTypeEnum.TRACKED_OBJECT: TrackedObjectHandler(config),
            EventTypeEnum.API: ApiEventHandler(config),
            EventTypeEnum.AUDIO: AudioEventHandler(config),
        }

        # Initialize communication channels
        self.event_receiver = EventUpdateSubscriber()
        self.event_end_publisher = EventEndPublisher()
    
    def run(self) -> None:
        """Run the event processor thread."""
        # Set an end_time on events without an end_time on startup
        Event.update(end_time=Event.start_time + 30).where(
            Event.end_time == None
        ).execute()

        while not self.stop_event.is_set():
            update = self.event_receiver.check_for_update(timeout=1)

            if update is None:
                continue

            source_type, event_type, camera, frame_name, event_data = update

            logger.debug(
                f"Event received: {source_type} {event_type} {camera} {event_data['id']}"
            )

            if source_type == EventTypeEnum.TRACKED_OBJECT:
                id = event_data["id"]
                self.timeline_queue.put(
                    (
                        camera,
                        source_type,
                        event_type,
                        self.events_in_process.get(id),
                        event_data,
                    )
                )

                # If this is the first message, just store it and continue
                if event_type == EventStateEnum.START or id not in self.events_in_process:
                    self.events_in_process[id] = event_data
                    continue

                self.handle_object_detection(event_type, camera, frame_name, event_data)
            elif source_type == EventTypeEnum.API:
                self.timeline_queue.put(
                    (
                        camera,
                        source_type,
                        event_type,
                        {},
                        event_data,
                    )
                )

                self.handle_external_detection(event_type, camera, frame_name, event_data)
            elif source_type == EventTypeEnum.AUDIO:
                self.timeline_queue.put(
                    (
                        camera,
                        source_type,
                        event_type,
                        self.events_in_process.get(event_data["id"]),
                        event_data,
                    )
                )

                # If this is the first message, just store it and continue
                if event_type == EventStateEnum.START or event_data["id"] not in self.events_in_process:
                    self.events_in_process[event_data["id"]] = event_data
                    continue

                self.handle_audio_detection(event_type, camera, frame_name, event_data)

        self.event_receiver.stop()
        self.event_end_publisher.stop()
        logger.info("Exiting event processor...")
    
    def handle_object_detection(
        self,
        event_type: str,
        camera: str,
        frame_name: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Handle tracked object event updates.
        
        Args:
            event_type: Type of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
        """
        updated_db = False
        handler = self.handlers[EventTypeEnum.TRACKED_OBJECT]
        
        # Process the event
        current_event = handler.handle_event(
            EventTypeEnum.TRACKED_OBJECT,
            event_type,
            camera,
            frame_name,
            event_data,
            self.events_in_process[event_data["id"]],
        )
        
        # Check if we should update the database
        if handler.should_update_db(
            EventData.from_dict(self.events_in_process[event_data["id"]]),
            current_event,
        ):
            updated_db = True
            
            # Prepare event data for database insertion
            db_event = handler.prepare_for_db(current_event, camera)
            
            # Insert or update the event in the database
            (
                Event.insert(db_event)
                .on_conflict(
                    conflict_target=[Event.id],
                    update=db_event,
                )
                .execute()
            )
        
        # Check if we should update the state
        if updated_db or handler.should_update_state(
            EventData.from_dict(self.events_in_process[event_data["id"]]),
            current_event,
        ):
            # Update the stored copy for comparison on future update messages
            self.events_in_process[event_data["id"]] = current_event.to_dict()
        
        # If this is the end of the event, remove it from the in-process list
        if event_type == EventStateEnum.END:
            del self.events_in_process[event_data["id"]]
            self.event_end_publisher.publish((event_data["id"], camera, updated_db))
    
    def handle_external_detection(
        self,
        event_type: str,
        camera: str,
        frame_name: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Handle external (API) event updates.
        
        Args:
            event_type: Type of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
        """
        handler = self.handlers[EventTypeEnum.API]
        
        # Process the event
        current_event = handler.handle_event(
            EventTypeEnum.API,
            event_type,
            camera,
            frame_name,
            event_data,
            None,
        )
        
        # Prepare event data for database insertion
        db_event = handler.prepare_for_db(current_event, camera)
        
        # Insert or update the event in the database
        if event_type == EventStateEnum.START:
            Event.insert(db_event).execute()
        elif event_type == EventStateEnum.END:
            try:
                Event.update(db_event).where(Event.id == event_data["id"]).execute()
            except Exception:
                logger.warning(f"Failed to update manual event: {event_data['id']}")
    
    def handle_audio_detection(
        self,
        event_type: str,
        camera: str,
        frame_name: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Handle audio event updates.
        
        Args:
            event_type: Type of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
        """
        handler = self.handlers[EventTypeEnum.AUDIO]
        
        # Process the event
        current_event = handler.handle_event(
            EventTypeEnum.AUDIO,
            event_type,
            camera,
            frame_name,
            event_data,
            self.events_in_process.get(event_data["id"]),
        )
        
        # Prepare event data for database insertion
        db_event = handler.prepare_for_db(current_event, camera)
        
        # Insert or update the event in the database
        if event_type == EventStateEnum.START:
            Event.insert(db_event).execute()
        elif event_type == EventStateEnum.END:
            try:
                Event.update(db_event).where(Event.id == event_data["id"]).execute()
                # Remove from in-process list
                del self.events_in_process[event_data["id"]]
            except Exception:
                logger.warning(f"Failed to update audio event: {event_data['id']}")
