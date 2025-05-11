"""Handler for audio events."""

import logging
from typing import Any, Dict, Optional

from arkos.config import FrigateConfig
from arkos.events.handlers import EventHandler
from arkos.events.types import (
    AudioEventData,
    EventData,
    EventStateEnum,
    EventTypeEnum,
)
from arkos.models import Event

logger = logging.getLogger(__name__)


class AudioEventHandler(EventHandler):
    """Handler for audio events."""
    
    def __init__(self, config: FrigateConfig):
        """Initialize the audio event handler.
        
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
    ) -> AudioEventData:
        """Handle an audio event.
        
        Args:
            event_type: Type of event
            event_state: State of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
            prev_event_data: Previous event data
            
        Returns:
            AudioEventData: Processed event data
        """
        # Convert to AudioEventData
        current_event = AudioEventData.from_dict(event_data)
        
        # If this is the first message, just return it
        if event_state == EventStateEnum.START or prev_event_data is None:
            return current_event
        
        # Convert previous event data to AudioEventData
        prev_event = AudioEventData.from_dict(prev_event_data)
        
        # For audio events, we just update the end time
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
        # For audio events, we always update the database
        return True
    
    def should_update_state(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event state should be updated.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event state should be updated
        """
        # For audio events, we always update the state
        return True
    
    def prepare_for_db(self, event: AudioEventData, camera: str) -> Dict[str, Any]:
        """Prepare event data for database insertion.
        
        Args:
            event: Event data
            camera: Camera name
            
        Returns:
            Dict[str, Any]: Event data prepared for database insertion
        """
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
                "type": "audio",
                "score": event.score,
                "top_score": event.score,
                "dBFS": event.dBFS,
                "detection_time": event.data.get("detection_time"),
                "duration": event.data.get("duration"),
                "audio_type": event.data.get("audio_type"),
                "frequency_range": event.data.get("frequency_range"),
                "audio_source": event.data.get("audio_source"),
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
        
        return db_event
