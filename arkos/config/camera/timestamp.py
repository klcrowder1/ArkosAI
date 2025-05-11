from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class TimestampStyleConfig(ArkosBaseModel):
    """Timestamp style configuration for a camera."""

    format: str = Field(default="%m/%d/%Y %H:%M:%S", title="Timestamp format")
    position: str = Field(default="tl", title="Timestamp position")
    font_size: float = Field(default=0.5, title="Font size")
    font_thickness: int = Field(default=1, title="Font thickness")
    color: Tuple[int, int, int] = Field(default=(255, 255, 255), title="Font color (RGB)")
    background: Optional[Tuple[int, int, int]] = Field(default=None, title="Background color (RGB)")
    
    # Advanced options
    font_face: str = Field(default="sans-serif", title="Font face")
    padding: int = Field(default=5, title="Padding around timestamp")
    shadow: bool = Field(default=False, title="Add shadow to timestamp")
    shadow_color: Tuple[int, int, int] = Field(default=(0, 0, 0), title="Shadow color (RGB)")
    shadow_offset: Tuple[int, int] = Field(default=(1, 1), title="Shadow offset (x, y)")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("position")
    @classmethod
    def validate_position(cls, v: str) -> str:
        """Validate position."""
        valid_positions = ["tl", "tr", "bl", "br", "tc", "bc", "custom"]
        if v.lower() not in valid_positions:
            raise ValueError(f"Position must be one of {valid_positions}, got {v}")
        return v.lower()
    
    @field_validator("font_size")
    @classmethod
    def validate_font_size(cls, v: float) -> float:
        """Validate font size."""
        if v <= 0:
            raise ValueError(f"Font size must be positive, got {v}")
        return v
    
    @field_validator("font_thickness")
    @classmethod
    def validate_font_thickness(cls, v: int) -> int:
        """Validate font thickness."""
        if v <= 0:
            raise ValueError(f"Font thickness must be positive, got {v}")
        return v
    
    @field_validator("color", "background", "shadow_color")
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
