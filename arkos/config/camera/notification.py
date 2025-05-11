from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class NotificationConfig(ArkosBaseModel):
    """Notification configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable notifications")
    enabled_in_config: bool = Field(default=True, exclude=True)
    
    # Notification triggers
    triggers: Set[str] = Field(default_factory=set, title="Notification triggers")
    
    # Object filters
    required_objects: Set[str] = Field(default_factory=set, title="Required objects for notification")
    filtered_objects: Set[str] = Field(default_factory=set, title="Objects to filter out from notifications")
    
    # Zone filters
    required_zones: List[str] = Field(default_factory=list, title="Required zones for notification")
    filtered_zones: List[str] = Field(default_factory=list, title="Zones to filter out from notifications")
    
    # Cooldown
    cooldown: int = Field(default=60, title="Cooldown period in seconds")
    
    # Notification content
    include_snapshot: bool = Field(default=True, title="Include snapshot in notification")
    include_preview: bool = Field(default=False, title="Include preview in notification")
    include_clip: bool = Field(default=False, title="Include clip in notification")
    
    # Notification services
    services: Dict[str, Any] = Field(default_factory=dict, title="Notification services configuration")
    
    # Advanced options
    throttle: Dict[str, Any] = Field(default_factory=dict, title="Throttling configuration")
    scheduling: Dict[str, Any] = Field(default_factory=dict, title="Scheduling configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("cooldown")
    @classmethod
    def validate_cooldown(cls, v: int) -> int:
        """Validate cooldown."""
        if v < 0:
            raise ValueError(f"Cooldown must be non-negative, got {v}")
        return v
