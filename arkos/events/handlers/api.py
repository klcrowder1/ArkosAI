"""Handler for API-triggered events."""

import logging
from typing import Any, Dict, Optional

from arkos.config import FrigateConfig
from arkos.events.handlers import EventHandler
from arkos.events.types import (
    ApiEventData,
    EventData,
    EventStateEnum,
    EventTypeEnum,
)
from arkos.models import Event

logger = logging.getLogger(__name__)


class ApiEventHandler(EventHandler):
    """Handler for API-triggered events."""
    
    def __init__(self, config: FrigateConfig):
        """Initialize the API event handler.
        
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
    ) -> ApiEventData:
        """Handle an API event.
        
        Args:
            event_type: Type of event
            event_state: State of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
            prev_event_data: Previous event data
            
        Returns:
            ApiEventData: Processed event data
        """
        # Convert to ApiEventData
        current_event = ApiEventData.from_dict(event_data)
        
        # If this is the first message, just return it
        if event_state == EventStateEnum.START or prev_event_data is None:
            return current_event
        
        # Convert previous event data to ApiEventData
        prev_event = ApiEventData.from_dict(prev_event_data)
        
        # For API events, we just update the end time
        if event_state == EventStateEnum.END:
            current_event.end_time = event_data.get("end_time")
        
        return current_event
    
    def should_update_db(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event should be updated in the database.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event should be updated in the database
        """
        # For API events, we always update the database
        return True
    
    def should_update_state(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event state should be updated.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event state should be updated
        """
        # For API events, we always update the state
        return True
    
    def prepare_for_db(self, event: ApiEventData, camera: str) -> Dict[str, Any]:
        """Prepare event data for database insertion.
        
        Args:
            event: Event data
            camera: Camera name
            
        Returns:
            Dict[str, Any]: Event data prepared for database insertion
        """
        if event.event_type == "api":
            db_event = {
                Event.id: event.id,
                Event.label: event.label,
                Event.sub_label: event.sub_label[0] if event.sub_label else None,
                Event.camera: event.camera,
                Event.start_time: event.start_time,
                Event.end_time: event.end_time,
                Event.thumbnail: event.thumbnail,
                Event.has_clip: event.has_clip,
                Event.has_snapshot: event.has_snapshot,
                Event.zones: [],
                Event.data: {
                    "type": event.event_type,
                    "score": event.score,
                    "top_score": event.score,
                    "detection_time": event.data.get("detection_time"),
                    "duration": event.data.get("duration"),
                    "api_source": event.data.get("api_source"),
                    "user_id": event.data.get("user_id"),
                    "request_id": event.data.get("request_id"),
                    "trigger_type": event.data.get("trigger_type"),
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
            
            if event.data.get("recognized_license_plate") is not None:
                db_event[Event.data]["recognized_license_plate"] = event.data[
                    "recognized_license_plate"
                ]
                db_event[Event.data]["recognized_license_plate_score"] = event.score
                
            return db_event
        else:
            # For other API event types (e.g., end events), just update the end time
            return {
                Event.id: event.id,
                Event.end_time: event.end_time,
            }
