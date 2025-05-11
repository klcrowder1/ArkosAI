from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class RetainModeEnum(str, Enum):
    """Retention mode enumeration."""

    ALL = "all"
    MOTION = "motion"
    ACTIVE_OBJECTS = "active_objects"


class RetainConfig(ArkosBaseModel):
    """Retention configuration for recordings."""

    days: int = Field(default=7, title="Number of days to retain recordings")
    mode: RetainModeEnum = Field(default=RetainModeEnum.ALL, title="Retention mode")


class RecordSegmentConfig(ArkosBaseModel):
    """Recording segment configuration."""

    enabled: bool = Field(default=True, title="Enable recording segments")
    time: int = Field(default=10, title="Segment time in seconds")
    format: str = Field(default="mp4", title="Segment format")
    retain: RetainConfig = Field(default_factory=RetainConfig, title="Retention configuration")


class RecordEventConfig(ArkosBaseModel):
    """Recording event configuration."""

    enabled: bool = Field(default=True, title="Enable event recording")
    pre_capture: int = Field(default=5, title="Pre-capture time in seconds")
    post_capture: int = Field(default=5, title="Post-capture time in seconds")
    objects: Set[str] = Field(default_factory=set, title="Objects to trigger recording")
    retain: RetainConfig = Field(default_factory=RetainConfig, title="Retention configuration")


class RecordConfig(ArkosBaseModel):
    """Recording configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable recording")
    enabled_in_config: bool = Field(default=True, exclude=True)
    retain: RetainConfig = Field(default_factory=RetainConfig, title="Retention configuration")
    
    # Recording segments
    segments: RecordSegmentConfig = Field(default_factory=RecordSegmentConfig, title="Segment configuration")
    
    # Event recording
    events: RecordEventConfig = Field(default_factory=RecordEventConfig, title="Event configuration")
    
    # Alert recording
    alerts: RecordEventConfig = Field(default_factory=RecordEventConfig, title="Alert configuration")
    
    # Detection recording
    detections: RecordEventConfig = Field(default_factory=RecordEventConfig, title="Detection configuration")
    
    # Storage configuration
    storage: Dict[str, Any] = Field(default_factory=dict, title="Storage configuration")
    
    # Tiered storage
    tiered_storage: Dict[str, Any] = Field(default_factory=dict, title="Tiered storage configuration")
    
    # Compression
    compression: Dict[str, Any] = Field(default_factory=dict, title="Compression configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("segments")
    @classmethod
    def validate_segments(cls, v: RecordSegmentConfig) -> RecordSegmentConfig:
        """Validate segment configuration."""
        if v.time > 60:
            raise ValueError(f"Segment time must be 60 seconds or less, got {v.time}")
        return v
