from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class ReviewItemConfig(ArkosBaseModel):
    """Review item configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable review")
    enabled_in_config: bool = Field(default=True, exclude=True)
    
    # Object filters
    required_objects: Set[str] = Field(default_factory=set, title="Required objects for review")
    filtered_objects: Set[str] = Field(default_factory=set, title="Objects to filter out from review")
    
    # Zone filters
    required_zones: List[str] = Field(default_factory=list, title="Required zones for review")
    filtered_zones: List[str] = Field(default_factory=list, title="Zones to filter out from review")
    
    # Retention
    retain: Dict[str, Any] = Field(default_factory=dict, title="Retention configuration")
    
    # Advanced options
    min_score: float = Field(default=0.5, title="Minimum score for review")
    min_area: Optional[Union[int, float]] = Field(default=None, title="Minimum area for review")
    max_area: Optional[Union[int, float]] = Field(default=None, title="Maximum area for review")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("min_score")
    @classmethod
    def validate_min_score(cls, v: float) -> float:
        """Validate minimum score."""
        if v < 0 or v > 1:
            raise ValueError(f"Minimum score must be between 0 and 1, got {v}")
        return v


class ReviewConfig(ArkosBaseModel):
    """Review configuration for a camera."""

    # Review items
    alerts: ReviewItemConfig = Field(default_factory=ReviewItemConfig, title="Alerts configuration")
    detections: ReviewItemConfig = Field(default_factory=ReviewItemConfig, title="Detections configuration")
    
    # Thumbnail configuration
    thumbnail: Dict[str, Any] = Field(default_factory=dict, title="Thumbnail configuration")
    
    # Preview configuration
    preview: Dict[str, Any] = Field(default_factory=dict, title="Preview configuration")
    
    # Clip configuration
    clip: Dict[str, Any] = Field(default_factory=dict, title="Clip configuration")
    
    # Advanced options
    storage: Dict[str, Any] = Field(default_factory=dict, title="Storage configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
