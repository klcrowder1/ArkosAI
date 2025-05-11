"""Event handlers for different event types."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from arkos.events.types import EventData, EventStateEnum, EventTypeEnum


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    def handle_event(
        self,
        event_type: EventTypeEnum,
        event_state: EventStateEnum,
        camera: str,
        frame_name: str,
        event_data: Dict[str, Any],
        prev_event_data: Optional[Dict[str, Any]] = None,
    ) -> EventData:
        """Handle an event.
        
        Args:
            event_type: Type of event
            event_state: State of event
            camera: Camera name
            frame_name: Frame name
            event_data: Event data
            prev_event_data: Previous event data
            
        Returns:
            EventData: Processed event data
        """
        pass
    
    @abstractmethod
    def should_update_db(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event should be updated in the database.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event should be updated in the database
        """
        pass
    
    @abstractmethod
    def should_update_state(self, prev_event: EventData, current_event: EventData) -> bool:
        """Determine if the event state should be updated.
        
        Args:
            prev_event: Previous event data
            current_event: Current event data
            
        Returns:
            bool: True if the event state should be updated
        """
        pass
