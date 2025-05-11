"""Event correlation for Arkos AI."""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any

from arkos.config import FrigateConfig
from arkos.events.types import (
    EventData,
    EventTypeEnum,
    TrackedObjectEventData,
    AudioEventData,
    ApiEventData,
    EventCategoryEnum,
    EventSeverityEnum,
    EventConfidenceEnum,
)

logger = logging.getLogger(__name__)


class EventCorrelator:
    """Correlate events from different sources and types."""
    
    def __init__(self, config: FrigateConfig):
        """Initialize the event correlator.
        
        Args:
            config: Arkos configuration
        """
        self.config = config
        self.recent_events: Dict[str, Dict[str, List[EventData]]] = defaultdict(lambda: defaultdict(list))
        self.correlated_events: Dict[str, Set[str]] = defaultdict(set)
        self.correlation_window = 30  # Default correlation window in seconds
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load correlation configuration from the config file."""
        # Get global correlation settings if they exist
        if hasattr(self.config, "events") and hasattr(self.config.events, "correlation"):
            correlation_config = self.config.events.correlation
            if hasattr(correlation_config, "window"):
                self.correlation_window = correlation_config.window
    
    def add_event(self, camera: str, event_type: EventTypeEnum, event_data: EventData) -> None:
        """Add an event to the correlation engine.
        
        Args:
            camera: Camera name
            event_type: Type of event
            event_data: Event data
        """
        # Add event to recent events
        self.recent_events[camera][event_type].append(event_data)
        
        # Clean up old events
        self._cleanup_old_events(camera)
        
        # Correlate events
        self._correlate_events(camera, event_data)
    
    def _cleanup_old_events(self, camera: str) -> None:
        """Clean up events older than the correlation window.
        
        Args:
            camera: Camera name
        """
        current_time = time.time()
        for event_type in list(self.recent_events[camera].keys()):
            self.recent_events[camera][event_type] = [
                event for event in self.recent_events[camera][event_type]
                if current_time - event.start_time <= self.correlation_window
            ]
    
    def _correlate_events(self, camera: str, new_event: EventData) -> None:
        """Correlate a new event with existing events.
        
        Args:
            camera: Camera name
            new_event: New event data
        """
        # Skip if this event is already correlated
        if new_event.id in self.correlated_events[camera]:
            return
        
        # Check for temporal correlation with other events
        for event_type, events in self.recent_events[camera].items():
            for event in events:
                # Skip self-correlation
                if event.id == new_event.id:
                    continue
                
                # Skip if this event is already correlated with the new event
                if event.id in new_event.related_events or new_event.id in event.related_events:
                    continue
                
                # Check if events are temporally correlated
                if self._are_events_correlated(new_event, event):
                    # Add correlation
                    self._add_correlation(new_event, event)
    
    def _are_events_correlated(self, event1: EventData, event2: EventData) -> bool:
        """Determine if two events are correlated.
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            bool: True if events are correlated, False otherwise
        """
        # Check temporal correlation
        if not self._are_events_temporally_correlated(event1, event2):
            return False
        
        # Check spatial correlation for tracked objects
        if isinstance(event1, TrackedObjectEventData) and isinstance(event2, TrackedObjectEventData):
            return self._are_objects_spatially_correlated(event1, event2)
        
        # Check label correlation for audio and tracked objects
        if (isinstance(event1, AudioEventData) and isinstance(event2, TrackedObjectEventData)) or \
           (isinstance(event1, TrackedObjectEventData) and isinstance(event2, AudioEventData)):
            return self._are_audio_object_correlated(
                event1 if isinstance(event1, AudioEventData) else event2,
                event1 if isinstance(event1, TrackedObjectEventData) else event2
            )
        
        # Default to temporal correlation only
        return True
    
    def _are_events_temporally_correlated(self, event1: EventData, event2: EventData) -> bool:
        """Determine if two events are temporally correlated.
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            bool: True if events are temporally correlated, False otherwise
        """
        # Get event time ranges
        event1_start = event1.start_time
        event1_end = event1.end_time if event1.end_time is not None else event1_start + 1
        
        event2_start = event2.start_time
        event2_end = event2.end_time if event2.end_time is not None else event2_start + 1
        
        # Check if events overlap in time
        return (event1_start <= event2_end) and (event2_start <= event1_end)
    
    def _are_objects_spatially_correlated(
        self, object1: TrackedObjectEventData, object2: TrackedObjectEventData
    ) -> bool:
        """Determine if two tracked objects are spatially correlated.
        
        Args:
            object1: First tracked object
            object2: Second tracked object
            
        Returns:
            bool: True if objects are spatially correlated, False otherwise
        """
        # Check if objects share any zones
        if set(object1.current_zones).intersection(set(object2.current_zones)):
            return True
        
        # Check if bounding boxes overlap
        box1 = object1.box
        box2 = object2.box
        
        # Calculate intersection over union (IoU)
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[0] + box1[2], box2[0] + box2[2])
        y2 = min(box1[1] + box1[3], box2[1] + box2[3])
        
        if x2 < x1 or y2 < y1:
            return False
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = box1[2] * box1[3]
        area2 = box2[2] * box2[3]
        union = area1 + area2 - intersection
        
        iou = intersection / union if union > 0 else 0
        
        # Consider objects correlated if IoU is above threshold
        return iou > 0.1
    
    def _are_audio_object_correlated(
        self, audio_event: AudioEventData, object_event: TrackedObjectEventData
    ) -> bool:
        """Determine if an audio event and a tracked object event are correlated.
        
        Args:
            audio_event: Audio event
            object_event: Tracked object event
            
        Returns:
            bool: True if events are correlated, False otherwise
        """
        # Check for specific audio-object correlations
        if audio_event.label == "speech" and object_event.label == "person":
            return True
        
        if audio_event.label == "bark" and object_event.label == "dog":
            return True
        
        if audio_event.label == "meow" and object_event.label == "cat":
            return True
        
        if audio_event.label == "engine" and object_event.label in ["car", "truck", "motorcycle"]:
            return True
        
        # Default to not correlated for audio-object pairs
        return False
    
    def _add_correlation(self, event1: EventData, event2: EventData) -> None:
        """Add correlation between two events.
        
        Args:
            event1: First event
            event2: Second event
        """
        # Add related event IDs
        event1.add_related_event(event2.id)
        event2.add_related_event(event1.id)
        
        # Add to correlated events set
        self.correlated_events[event1.camera].add(event1.id)
        self.correlated_events[event2.camera].add(event2.id)
        
        # Update metadata
        event1.update_metadata("correlated_at", datetime.now().isoformat())
        event2.update_metadata("correlated_at", datetime.now().isoformat())
        
        # Update event severity based on correlation
        self._update_event_severity(event1, event2)
        
        # Log correlation
        logger.debug(f"Correlated events: {event1.id} and {event2.id}")
    
    def _update_event_severity(self, event1: EventData, event2: EventData) -> None:
        """Update event severity based on correlation.
        
        Args:
            event1: First event
            event2: Second event
        """
        # If either event has alert severity, upgrade both to alert
        if event1.severity == EventSeverityEnum.ALERT or event2.severity == EventSeverityEnum.ALERT:
            event1.severity = EventSeverityEnum.ALERT
            event2.severity = EventSeverityEnum.ALERT
        # If both events have detection severity, upgrade to alert
        elif event1.severity == EventSeverityEnum.DETECTION and event2.severity == EventSeverityEnum.DETECTION:
            event1.severity = EventSeverityEnum.ALERT
            event2.severity = EventSeverityEnum.ALERT
        # Otherwise, upgrade to detection if either is detection
        elif event1.severity == EventSeverityEnum.DETECTION or event2.severity == EventSeverityEnum.DETECTION:
            event1.severity = EventSeverityEnum.DETECTION
            event2.severity = EventSeverityEnum.DETECTION
    
    def get_correlated_events(self, camera: str, event_id: str) -> List[EventData]:
        """Get all events correlated with a specific event.
        
        Args:
            camera: Camera name
            event_id: Event ID
            
        Returns:
            List[EventData]: List of correlated events
        """
        correlated_events = []
        
        # Find the event
        for event_type, events in self.recent_events[camera].items():
            for event in events:
                if event.id == event_id:
                    # Get all related events
                    for related_id in event.related_events:
                        for related_type, related_events in self.recent_events[camera].items():
                            for related_event in related_events:
                                if related_event.id == related_id:
                                    correlated_events.append(related_event)
        
        return correlated_events
    
    def get_correlation_groups(self, camera: str) -> List[List[EventData]]:
        """Get groups of correlated events for a camera.
        
        Args:
            camera: Camera name
            
        Returns:
            List[List[EventData]]: List of correlated event groups
        """
        # Build a graph of event correlations
        correlation_graph: Dict[str, Set[str]] = defaultdict(set)
        event_map: Dict[str, EventData] = {}
        
        # Populate the graph and event map
        for event_type, events in self.recent_events[camera].items():
            for event in events:
                event_map[event.id] = event
                for related_id in event.related_events:
                    correlation_graph[event.id].add(related_id)
                    correlation_graph[related_id].add(event.id)
        
        # Find connected components (correlation groups)
        visited = set()
        correlation_groups = []
        
        for event_id in correlation_graph:
            if event_id not in visited:
                # Start a new group
                group = []
                queue = [event_id]
                visited.add(event_id)
                
                # BFS to find all connected events
                while queue:
                    current_id = queue.pop(0)
                    if current_id in event_map:
                        group.append(event_map[current_id])
                    
                    for neighbor_id in correlation_graph[current_id]:
                        if neighbor_id not in visited:
                            visited.add(neighbor_id)
                            queue.append(neighbor_id)
                
                if group:
                    correlation_groups.append(group)
        
        return correlation_groups
