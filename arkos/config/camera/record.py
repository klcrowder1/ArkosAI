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


class RetentionPriorityEnum(str, Enum):
    """Retention priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StorageTierTypeEnum(str, Enum):
    """Storage tier type enumeration."""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class StorageTierConfig(ArkosBaseModel):
    """Storage tier configuration."""

    name: str = Field(default="", title="Name of the storage tier")
    path: str = Field(default="", title="Path to the storage location")
    type: StorageTierTypeEnum = Field(
        default=StorageTierTypeEnum.WARM, title="Type of storage tier")
    priority: int = Field(
        default=100, title="Priority of the tier (lower is higher priority)")
    min_age_days: int = Field(
        default=7, title="Minimum age of recordings in days to be stored in this tier")
    max_age_days: Optional[int] = Field(
        default=None, title="Maximum age of recordings in days to be stored in this tier")
    min_free_space_mb: int = Field(
        default=1000, title="Minimum free space in MB to maintain on this tier")
    readonly: bool = Field(
        default=False, title="Whether this tier is read-only")
    events_only: bool = Field(
        default=False, title="Whether this tier should only store event recordings")
    min_priority: RetentionPriorityEnum = Field(
        default=RetentionPriorityEnum.LOW, 
        title="Minimum priority level for recordings to be stored in this tier"
    )
    objects: Set[str] = Field(
        default_factory=set, 
        title="Object types to store in this tier (empty means all objects)"
    )
    zones: Set[str] = Field(
        default_factory=set, 
        title="Zones to store in this tier (empty means all zones)"
    )
    time_ranges: List[TimeRangeConfig] = Field(
        default_factory=list, 
        title="Time ranges for this tier (if empty, tier applies to all times)"
    )


class TimeRangeConfig(ArkosBaseModel):
    """Time range configuration for retention policies."""

    start_time: str = Field(default="00:00", title="Start time in HH:MM format")
    end_time: str = Field(default="23:59", title="End time in HH:MM format")
    days: List[str] = Field(
        default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        title="Days of the week this time range applies to",
    )


class TieredStorageConfig(ArkosBaseModel):
    """Tiered storage configuration."""

    enabled: bool = Field(default=False, title="Enable tiered storage")
    check_interval: int = Field(
        default=3600, title="Interval in seconds to check for recordings to move")
    tiers: List[StorageTierConfig] = Field(
        default_factory=list, title="Storage tiers")


class ObjectRetentionConfig(ArkosBaseModel):
    """Object-specific retention configuration."""

    days: int = Field(default=7, title="Number of days to retain recordings for this object type")
    mode: RetainModeEnum = Field(default=RetainModeEnum.ALL, title="Retention mode for this object type")
    min_score: float = Field(default=0.0, title="Minimum score for retention")
    min_area: int = Field(default=0, title="Minimum area for retention")
    priority: RetentionPriorityEnum = Field(
        default=RetentionPriorityEnum.MEDIUM, 
        title="Priority for this object type (higher priority objects are retained longer when storage is limited)"
    )


class ZoneRetentionConfig(ArkosBaseModel):
    """Zone-specific retention configuration."""

    days: int = Field(default=7, title="Number of days to retain recordings for this zone")
    mode: RetainModeEnum = Field(default=RetainModeEnum.ALL, title="Retention mode for this zone")
    priority: RetentionPriorityEnum = Field(
        default=RetentionPriorityEnum.MEDIUM, 
        title="Priority for this zone (higher priority zones are retained longer when storage is limited)"
    )


class RetainConfig(ArkosBaseModel):
    """Retention configuration for recordings."""

    days: int = Field(default=7, title="Number of days to retain recordings")
    mode: RetainModeEnum = Field(
        default=RetainModeEnum.ALL, title="Retention mode")
    priority: RetentionPriorityEnum = Field(
        default=RetentionPriorityEnum.MEDIUM, 
        title="Priority for retention (higher priority recordings are retained longer when storage is limited)"
    )
    objects: Dict[str, ObjectRetentionConfig] = Field(
        default_factory=dict, 
        title="Object-specific retention configuration"
    )
    zones: Dict[str, ZoneRetentionConfig] = Field(
        default_factory=dict, 
        title="Zone-specific retention configuration"
    )
    time_ranges: List[TimeRangeConfig] = Field(
        default_factory=list, 
        title="Time ranges for retention (if empty, retention applies to all times)"
    )


class RecordSegmentConfig(ArkosBaseModel):
    """Recording segment configuration."""

    enabled: bool = Field(default=True, title="Enable recording segments")
    time: int = Field(default=10, title="Segment time in seconds")
    format: str = Field(default="mp4", title="Segment format")
    retain: RetainConfig = Field(
        default_factory=RetainConfig, title="Retention configuration")


class RecordEventConfig(ArkosBaseModel):
    """Recording event configuration."""

    enabled: bool = Field(default=True, title="Enable event recording")
    pre_capture: int = Field(default=5, title="Pre-capture time in seconds")
    post_capture: int = Field(default=5, title="Post-capture time in seconds")
    objects: Set[str] = Field(
        default_factory=set, title="Objects to trigger recording")
    retain: RetainConfig = Field(
        default_factory=RetainConfig, title="Retention configuration")


class CompressionConfig(ArkosBaseModel):
    """Compression configuration for recordings."""

    enabled: bool = Field(default=False, title="Enable compression")
    codec: str = Field(default="h264", title="Codec to use for compression")
    quality: int = Field(
        default=23, title="Quality setting for compression (lower is better)")
    preset: str = Field(
        default="medium", title="Preset for compression (slower presets give better quality)")
    tune: Optional[str] = Field(
        default=None, title="Tune setting for compression")
    max_bitrate: Optional[int] = Field(
        default=None, title="Maximum bitrate in kbps")


class RecordConfig(ArkosBaseModel):
    """Recording configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable recording")
    enabled_in_config: bool = Field(default=True, exclude=True)
    retain: RetainConfig = Field(
        default_factory=RetainConfig, title="Retention configuration")

    # Recording segments
    segments: RecordSegmentConfig = Field(
        default_factory=RecordSegmentConfig, title="Segment configuration")

    # Event recording
    events: RecordEventConfig = Field(
        default_factory=RecordEventConfig, title="Event configuration")

    # Alert recording
    alerts: RecordEventConfig = Field(
        default_factory=RecordEventConfig, title="Alert configuration")

    # Detection recording
    detections: RecordEventConfig = Field(
        default_factory=RecordEventConfig, title="Detection configuration")

    # Storage configuration
    storage: Dict[str, Any] = Field(
        default_factory=dict, title="Storage configuration")

    # Tiered storage
    tiered_storage: TieredStorageConfig = Field(
        default_factory=TieredStorageConfig, title="Tiered storage configuration")

    # Compression
    compression: CompressionConfig = Field(
        default_factory=CompressionConfig, title="Compression configuration")

    # Experimental features
    experimental: Dict[str, Any] = Field(
        default_factory=dict, title="Experimental features")

    @field_validator("segments")
    @classmethod
    def validate_segments(cls, v: RecordSegmentConfig) -> RecordSegmentConfig:
        """Validate segment configuration."""
        if v.time > 60:
            raise ValueError(
                f"Segment time must be 60 seconds or less, got {v.time}")
        return v
