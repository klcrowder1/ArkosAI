from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class BirdseyeConfig(ArkosBaseModel):
    """Birdseye configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable birdseye view")
    width: int = Field(default=1280, title="Width of the birdseye view")
    height: int = Field(default=720, title="Height of the birdseye view")
    quality: int = Field(default=70, title="JPEG quality (0-100)")
    mode: str = Field(default="objects", title="Birdseye mode")
    
    # Layout configuration
    layout: Dict[str, Any] = Field(default_factory=dict, title="Layout configuration")
    
    # Object display
    label: bool = Field(default=True, title="Show object labels")
    timestamp: bool = Field(default=True, title="Show timestamps")
    zones: bool = Field(default=True, title="Show zones")
    mask: bool = Field(default=False, title="Show masks")
    
    # Advanced options
    background: Optional[Tuple[int, int, int]] = Field(default=None, title="Background color (RGB)")
    border: Optional[Tuple[int, int, int]] = Field(default=None, title="Border color (RGB)")
    border_width: int = Field(default=1, title="Border width")
    padding: int = Field(default=5, title="Padding between camera views")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: int) -> int:
        """Validate quality."""
        if v < 0 or v > 100:
            raise ValueError(f"Quality must be between 0 and 100, got {v}")
        return v
    
    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate mode."""
        valid_modes = ["objects", "motion", "cameras", "custom"]
        if v.lower() not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}, got {v}")
        return v.lower()
    
    @field_validator("background", "border")
    @classmethod
    def validate_color(cls, v: Optional[Tuple[int, int, int]]) -> Optional[Tuple[int, int, int]]:
        """Validate color."""
        if v is None:
            return None
        
        if len(v) != 3:
            raise ValueError(f"Color must have 3 components (RGB), got {len(v)}")
        
        for component in v:
            if component < 0 or component > 255:
                raise ValueError(f"Color components must be between 0 and 255, got {v}")
        
        return v
