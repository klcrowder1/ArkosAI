"""Event filtering for Arkos AI."""

import logging
from typing import Dict, List, Optional, Any

from arkos.config import FrigateConfig
from arkos.events.types import (
    EventData,
    EventTypeEnum,
    TrackedObjectEventData,
    AudioEventData,
    ApiEventData,
)

logger = logging.getLogger(__name__)


class EventFilter:
    """Filter events based on configuration."""
    
    def __init__(self, config: FrigateConfig):
        """Initialize the event filter.
        
        Args:
            config: Arkos configuration
        """
        self.config = config
    
    def should_filter_event(
        self,
        event_type: EventTypeEnum,
        camera: str,
        event_data: EventData,
    ) -> bool:
        """Determine if an event should be filtered out.
        
        Args:
            event_type: Type of event
            camera: Camera name
            event_data: Event data
            
        Returns:
            bool: True if the event should be filtered out, False otherwise
        """
        # Get camera-specific event configuration
        camera_config = self.config.cameras.get(camera)
        if not camera_config:
            logger.warning(f"Camera {camera} not found in configuration")
            return False
        
        # Check if event filtering is enabled
        if not camera_config.events.enabled:
            return False
        
        # Apply global filter if it exists
        if camera_config.events.global_filter:
            if self._apply_filter(event_data, camera_config.events.global_filter):
                return True
        
        # Apply event type-specific filter if it exists
        event_filter = camera_config.events.filters.get(event_type)
        if event_filter:
            return self._apply_filter(event_data, event_filter)
        
        return False
    
    def _apply_filter(self, event_data: EventData, filter_config: Dict[str, Any]) -> bool:
        """Apply filter configuration to an event.
        
        Args:
            event_data: Event data
            filter_config: Filter configuration
            
        Returns:
            bool: True if the event should be filtered out, False otherwise
        """
        # Check score
        if hasattr(event_data, "score"):
            if filter_config.min_score is not None and event_data.score < filter_config.min_score:
                return True
            if filter_config.max_score is not None and event_data.score > filter_config.max_score:
                return True
        
        # Check duration
        if event_data.end_time is not None and filter_config.min_duration is not None:
            duration = event_data.end_time - event_data.start_time
            if duration < filter_config.min_duration:
                return True
        
        if event_data.end_time is not None and filter_config.max_duration is not None:
            duration = event_data.end_time - event_data.start_time
            if duration > filter_config.max_duration:
                return True
        
        # Check label
        if filter_config.labels is not None and event_data.label not in filter_config.labels:
            return True
        
        if filter_config.exclude_labels is not None and event_data.label in filter_config.exclude_labels:
            return True
        
        # Check zones
        if filter_config.zones is not None and not any(zone in event_data.zones for zone in filter_config.zones):
            return True
        
        if filter_config.exclude_zones is not None and any(zone in event_data.zones for zone in filter_config.exclude_zones):
            return True
        
        # Check category
        if filter_config.categories is not None and event_data.category not in filter_config.categories:
            return True
        
        if filter_config.exclude_categories is not None and event_data.category in filter_config.exclude_categories:
            return True
        
        # Check severity
        if filter_config.severities is not None and event_data.severity not in filter_config.severities:
            return True
        
        if filter_config.exclude_severities is not None and event_data.severity in filter_config.exclude_severities:
            return True
        
        # Check confidence level
        if filter_config.confidence_levels is not None and event_data.confidence not in filter_config.confidence_levels:
            return True
        
        if filter_config.exclude_confidence_levels is not None and event_data.confidence in filter_config.exclude_confidence_levels:
            return True
        
        # Check tags
        if filter_config.tags is not None and not any(tag in event_data.tags for tag in filter_config.tags):
            return True
        
        if filter_config.exclude_tags is not None and any(tag in event_data.tags for tag in filter_config.exclude_tags):
            return True
        
        # Check source
        if filter_config.sources is not None and event_data.source not in filter_config.sources:
            return True
        
        if filter_config.exclude_sources is not None and event_data.source in filter_config.exclude_sources:
            return True
        
        # Apply custom filters if any
        if filter_config.custom_filters:
            for key, value in filter_config.custom_filters.items():
                if key in event_data.data:
                    if isinstance(value, list) and event_data.data[key] not in value:
                        return True
                    elif not isinstance(value, list) and event_data.data[key] != value:
                        return True
        
        # Event passed all filters
        return False
