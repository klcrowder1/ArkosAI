"""Event processor for Arkos AI."""

import logging
import threading
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MpEvent
from typing import Dict, Optional, Tuple, Any

from arkos.comms.events_updater import EventEndPublisher, EventUpdateSubscriber
from arkos.config import FrigateConfig
from arkos.events.correlation import EventCorrelator
from arkos.events.filter import EventFilter
from arkos.events.handlers.api import ApiEventHandler
from arkos.events.handlers.audio import AudioEventHandler
from arkos.events.handlers.object import TrackedObjectHandler
from arkos.events.types import EventData, EventStateEnum, EventTypeEnum
from arkos.models import Event
from arkos.notifications.manager import NotificationManager

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
        
        # Initialize event filter
        self.event_filter = EventFilter(config)
        
        # Initialize event correlator
        self.event_correlator = EventCorrelator(config)
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(config)

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

            # Convert event data to EventData object for filtering
            event_obj = None
            if source_type == EventTypeEnum.TRACKED_OBJECT:
                id = event_data["id"]
                
                # Check if this is a new event
                is_new_event = event_type == EventStateEnum.START or id not in self.events_in_process
                
                # Create event object for filtering
                if is_new_event:
                    event_obj = self.handlers[source_type].handle_event(
                        source_type,
                        event_type,
                        camera,
                        frame_name,
                        event_data,
                        None
                    )
                    
                    # Check if the event should be filtered out
                    if self.event_filter.should_filter_event(source_type, camera, event_obj):
                        logger.debug(f"Filtered out event: {source_type} {event_type} {camera} {id}")
                        continue
                
                # Add to timeline queue
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
                if is_new_event:
                    self.events_in_process[id] = event_data
                    continue

                self.handle_object_detection(event_type, camera, frame_name, event_data)
            elif source_type == EventTypeEnum.API:
                # Create event object for filtering
                if event_type == EventStateEnum.START:
                    event_obj = self.handlers[source_type].handle_event(
                        source_type,
                        event_type,
                        camera,
                        frame_name,
                        event_data,
                        None
                    )
                    
                    # Check if the event should be filtered out
                    if self.event_filter.should_filter_event(source_type, camera, event_obj):
                        logger.debug(f"Filtered out event: {source_type} {event_type} {camera} {event_data['id']}")
                        continue
                
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
                # Check if this is a new event
                is_new_event = event_type == EventStateEnum.START or event_data["id"] not in self.events_in_process
                
                # Create event object for filtering
                if is_new_event:
                    event_obj = self.handlers[source_type].handle_event(
                        source_type,
                        event_type,
                        camera,
                        frame_name,
                        event_data,
                        None
                    )
                    
                    # Check if the event should be filtered out
                    if self.event_filter.should_filter_event(source_type, camera, event_obj):
                        logger.debug(f"Filtered out event: {source_type} {event_type} {camera} {event_data['id']}")
                        continue
                
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
                if is_new_event:
                    self.events_in_process[event_data["id"]] = event_data
                    continue

                self.handle_audio_detection(event_type, camera, frame_name, event_data)

        # Clean up resources
        self.event_receiver.stop()
        self.event_end_publisher.stop()
        self.notification_manager.cleanup()
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
        
        # Add event to correlator
        camera_config = self.config.cameras.get(camera)
        if camera_config and camera_config.events.correlation.enabled:
            self.event_correlator.add_event(camera, EventTypeEnum.TRACKED_OBJECT, current_event)
        
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
        
        # Send notification if this is a new event (START)
        if event_type == EventStateEnum.START:
            # Check if notifications are enabled for this camera
            if camera_config and hasattr(camera_config, "notifications"):
                notification_config = camera_config.notifications
                
                # Check if notifications are enabled and if this object type should trigger a notification
                if (notification_config.enabled and 
                    (not notification_config.filtered_objects or 
                     current_event.label not in notification_config.filtered_objects) and
                    (not notification_config.required_objects or 
                     current_event.label in notification_config.required_objects)):
                    
                    # Check if this event is in any required zones
                    zones_match = True
                    if notification_config.required_zones:
                        zones_match = False
                        for zone in current_event.zones:
                            if zone in notification_config.required_zones:
                                zones_match = True
                                break
                    
                    # Check if this event is in any filtered zones
                    if zones_match and notification_config.filtered_zones:
                        for zone in current_event.zones:
                            if zone in notification_config.filtered_zones:
                                zones_match = False
                                break
                    
                    # If all conditions are met, send notification
                    if zones_match:
                        # Get snapshot path if available
                        snapshot_path = None
                        if hasattr(current_event, "has_snapshot") and current_event.has_snapshot:
                            snapshot_path = f"/clips/{camera}/{current_event.id}/snapshot.jpg"
                        
                        # Get clip path if available
                        clip_path = None
                        if hasattr(current_event, "has_clip") and current_event.has_clip:
                            clip_path = f"/clips/{camera}/{current_event.id}/clip.mp4"
                        
                        # Send notification
                        self.notification_manager.notify_event(
                            event=current_event,
                            snapshot_path=snapshot_path if notification_config.include_snapshot else None,
                            clip_path=clip_path if notification_config.include_clip else None,
                        )
        
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
        
        # Add event to correlator
        camera_config = self.config.cameras.get(camera)
        if camera_config and camera_config.events.correlation.enabled and event_type == EventStateEnum.START:
            self.event_correlator.add_event(camera, EventTypeEnum.API, current_event)
        
        # Prepare event data for database insertion
        db_event = handler.prepare_for_db(current_event, camera)
        
        # Insert or update the event in the database
        if event_type == EventStateEnum.START:
            Event.insert(db_event).execute()
            
            # Send notification if this is a new event (START)
            if camera_config and hasattr(camera_config, "notifications"):
                notification_config = camera_config.notifications
                
                # Check if notifications are enabled for API events
                if notification_config.enabled and "api" in notification_config.triggers:
                    # Get snapshot path if available
                    snapshot_path = None
                    if hasattr(current_event, "has_snapshot") and current_event.has_snapshot:
                        snapshot_path = f"/clips/{camera}/{current_event.id}/snapshot.jpg"
                    
                    # Send notification
                    self.notification_manager.notify_event(
                        event=current_event,
                        title=f"API Event: {current_event.label}",
                        message=f"API event triggered on {camera}: {current_event.label}",
                        snapshot_path=snapshot_path if notification_config.include_snapshot else None,
                    )
            
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
        
        # Add event to correlator
        camera_config = self.config.cameras.get(camera)
        if camera_config and camera_config.events.correlation.enabled:
            self.event_correlator.add_event(camera, EventTypeEnum.AUDIO, current_event)
        
        # Prepare event data for database insertion
        db_event = handler.prepare_for_db(current_event, camera)
        
        # Insert or update the event in the database
        if event_type == EventStateEnum.START:
            Event.insert(db_event).execute()
            
            # Send notification if this is a new event (START)
            if camera_config and hasattr(camera_config, "notifications"):
                notification_config = camera_config.notifications
                
                # Check if notifications are enabled for audio events
                if notification_config.enabled and "audio" in notification_config.triggers:
                    # Get snapshot path if available
                    snapshot_path = None
                    if hasattr(current_event, "has_snapshot") and current_event.has_snapshot:
                        snapshot_path = f"/clips/{camera}/{current_event.id}/snapshot.jpg"
                    
                    # Send notification
                    self.notification_manager.notify_event(
                        event=current_event,
                        title=f"Audio Event: {current_event.label}",
                        message=f"Audio detected on {camera}: {current_event.label}",
                        snapshot_path=snapshot_path if notification_config.include_snapshot else None,
                    )
            
        elif event_type == EventStateEnum.END:
            try:
                Event.update(db_event).where(Event.id == event_data["id"]).execute()
                # Remove from in-process list
                del self.events_in_process[event_data["id"]]
            except Exception:
                logger.warning(f"Failed to update audio event: {event_data['id']}")
