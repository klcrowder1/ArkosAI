from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class SnapshotsConfig(ArkosBaseModel):
    """Snapshots configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable snapshots")
    clean_copy: bool = Field(default=False, title="Save clean copy without bounding boxes")
    timestamp: bool = Field(default=True, title="Add timestamp to snapshots")
    bounding_box: bool = Field(default=True, title="Add bounding box to snapshots")
    crop: bool = Field(default=False, title="Crop snapshots to object")
    height: Optional[int] = Field(default=None, title="Height of snapshots")
    width: Optional[int] = Field(default=None, title="Width of snapshots")
    quality: int = Field(default=70, title="JPEG quality (0-100)")
    retain: Dict[str, Any] = Field(default_factory=dict, title="Retention configuration")
    
    # Advanced options
    optimize: bool = Field(default=False, title="Optimize snapshots for size")
    format: str = Field(default="jpg", title="Snapshot format")
    
    # Enhancement options
    enhance: bool = Field(default=False, title="Enhance snapshots")
    enhance_method: str = Field(default="auto", title="Enhancement method")
    enhance_params: Dict[str, Any] = Field(default_factory=dict, title="Enhancement parameters")
    
    # Storage options
    storage: Dict[str, Any] = Field(default_factory=dict, title="Storage configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: int) -> int:
        """Validate quality."""
        if v < 0 or v > 100:
            raise ValueError(f"Quality must be between 0 and 100, got {v}")
        return v
    
    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate format."""
        valid_formats = ["jpg", "jpeg", "png", "webp"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Format must be one of {valid_formats}, got {v}")
        return v.lower()
    
    @field_validator("enhance_method")
    @classmethod
    def validate_enhance_method(cls, v: str) -> str:
        """Validate enhancement method."""
        valid_methods = ["auto", "clahe", "unsharp_mask", "super_resolution", "custom"]
        if v.lower() not in valid_methods:
            raise ValueError(f"Enhancement method must be one of {valid_methods}, got {v}")
        return v.lower()
