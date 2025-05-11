"""Event configuration for a camera."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class EventCorrelationConfig(ArkosBaseModel):
    """Configuration for event correlation."""
    
    enabled: bool = Field(default=True, title="Enable event correlation")
    window: int = Field(default=30, title="Time window for correlation in seconds")
    spatial_threshold: float = Field(default=0.1, title="Spatial correlation threshold (IoU)")
    severity_upgrade: bool = Field(default=True, title="Upgrade severity of correlated events")
    cross_camera: bool = Field(default=False, title="Enable cross-camera correlation")
    
    # Correlation rules
    rules: Dict[str, Any] = Field(default_factory=dict, title="Custom correlation rules")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")


class EventFilterConfig(ArkosBaseModel):
    """Filter configuration for events."""

    min_score: float = Field(default=0.5, title="Minimum confidence score for events")
    max_score: Optional[float] = Field(default=None, title="Maximum confidence score for events")
    min_duration: Optional[float] = Field(default=None, title="Minimum duration for events in seconds")
    max_duration: Optional[float] = Field(default=None, title="Maximum duration for events in seconds")
    labels: Optional[List[str]] = Field(default=None, title="Labels to include in filtering")
    exclude_labels: Optional[List[str]] = Field(default=None, title="Labels to exclude from filtering")
    zones: Optional[List[str]] = Field(default=None, title="Zones to include in filtering")
    exclude_zones: Optional[List[str]] = Field(default=None, title="Zones to exclude from filtering")
    categories: Optional[List[str]] = Field(default=None, title="Categories to include in filtering")
    exclude_categories: Optional[List[str]] = Field(default=None, title="Categories to exclude from filtering")
    severities: Optional[List[str]] = Field(default=None, title="Severities to include in filtering")
    exclude_severities: Optional[List[str]] = Field(default=None, title="Severities to exclude from filtering")
    confidence_levels: Optional[List[str]] = Field(default=None, title="Confidence levels to include in filtering")
    exclude_confidence_levels: Optional[List[str]] = Field(default=None, title="Confidence levels to exclude from filtering")
    tags: Optional[List[str]] = Field(default=None, title="Tags to include in filtering")
    exclude_tags: Optional[List[str]] = Field(default=None, title="Tags to exclude from filtering")
    sources: Optional[List[str]] = Field(default=None, title="Sources to include in filtering")
    exclude_sources: Optional[List[str]] = Field(default=None, title="Sources to exclude from filtering")
    
    # Advanced filtering options
    custom_filters: Dict[str, Any] = Field(default_factory=dict, title="Custom filters for events")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")


class EventConfig(ArkosBaseModel):
    """Event configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable event processing")
    filters: Dict[str, EventFilterConfig] = Field(default_factory=dict, title="Event filters by type")
    
    # Global filter that applies to all event types
    global_filter: Optional[EventFilterConfig] = Field(default=None, title="Global filter for all event types")
    
    # Event correlation configuration
    correlation: EventCorrelationConfig = Field(
        default_factory=EventCorrelationConfig,
        title="Event correlation configuration"
    )
    
    # Retention configuration
    retention: Dict[str, Any] = Field(default_factory=dict, title="Event retention configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
