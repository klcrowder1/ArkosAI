from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class MotionConfig(ArkosBaseModel):
    """Motion detection configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable motion detection")
    enabled_in_config: bool = Field(default=True, exclude=True)
    
    # Motion detection parameters
    threshold: int = Field(default=25, title="Threshold for motion detection")
    contour_area: int = Field(default=30, title="Minimum contour area for motion detection")
    delta_alpha: float = Field(default=0.2, title="Alpha value for delta frame calculation")
    frame_alpha: float = Field(default=0.2, title="Alpha value for average frame calculation")
    frame_height: Optional[int] = Field(default=None, title="Height of the frame for motion detection")
    frame_width: Optional[int] = Field(default=None, title="Width of the frame for motion detection")
    
    # Mask configuration
    mask: Optional[Union[str, List[str]]] = Field(default=None, title="Mask for motion detection")
    
    # Advanced motion detection options
    improve_contrast: bool = Field(default=True, title="Improve contrast for motion detection")
    gaussian_blur: Optional[int] = Field(default=None, title="Gaussian blur kernel size")
    
    # Adaptive motion detection
    adaptive: bool = Field(default=False, title="Enable adaptive motion detection")
    adaptive_steps: int = Field(default=3, title="Number of steps for adaptive motion detection")
    adaptive_learning_rate: float = Field(default=0.01, title="Learning rate for adaptive motion detection")
    
    # Temporal filtering
    temporal_filter: bool = Field(default=False, title="Enable temporal filtering")
    temporal_filter_size: int = Field(default=3, title="Size of the temporal filter")
    
    # Spatial filtering
    spatial_filter: bool = Field(default=False, title="Enable spatial filtering")
    spatial_filter_size: int = Field(default=3, title="Size of the spatial filter")
    
    # Motion history
    history_size: int = Field(default=5, title="Size of the motion history")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v: int) -> int:
        """Validate the threshold."""
        if v < 1 or v > 255:
            raise ValueError(f"Threshold must be between 1 and 255, got {v}")
        return v
    
    @field_validator("delta_alpha", "frame_alpha")
    @classmethod
    def validate_alpha(cls, v: float) -> float:
        """Validate alpha values."""
        if v < 0 or v > 1:
            raise ValueError(f"Alpha value must be between 0 and 1, got {v}")
        return v
    
    @field_validator("gaussian_blur")
    @classmethod
    def validate_gaussian_blur(cls, v: Optional[int]) -> Optional[int]:
        """Validate gaussian blur kernel size."""
        if v is not None and (v < 1 or v % 2 == 0):
            raise ValueError(f"Gaussian blur kernel size must be a positive odd number, got {v}")
        return v
