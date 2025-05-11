from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class StationaryConfig(ArkosBaseModel):
    """Configuration for stationary object detection."""

    threshold: Optional[int] = Field(default=None, title="Threshold for stationary object detection")
    interval: Optional[int] = Field(default=None, title="Interval for stationary object detection")


class DetectConfig(ArkosBaseModel):
    """Detection configuration for a camera."""

    enabled: bool = Field(default=True, title="Enable object detection")
    width: Optional[int] = Field(default=None, title="Width of the detection frame")
    height: Optional[int] = Field(default=None, title="Height of the detection frame")
    fps: int = Field(default=5, title="Frames per second for detection")
    
    # Object tracking parameters
    max_disappeared: Optional[int] = Field(default=None, title="Maximum number of frames an object can disappear before being removed")
    min_initialized: Optional[int] = Field(default=None, title="Minimum number of frames an object must be detected before being tracked")
    stationary: StationaryConfig = Field(default_factory=StationaryConfig, title="Stationary object detection configuration")
    
    # Model configuration
    model_purposes: List[str] = Field(default_factory=lambda: ["general"], title="Model purposes to use for this camera")
    model_merge_strategy: str = Field(default="highest_confidence", title="Strategy for merging results from multiple models")
    
    # Advanced detection options
    crop_regions: List[Dict[str, Any]] = Field(default_factory=list, title="Regions to crop for detection")
    roi_strategy: str = Field(default="full_frame", title="Region of interest strategy")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    # Hardware acceleration
    acceleration: Dict[str, Any] = Field(default_factory=dict, title="Hardware acceleration settings")
    
    # Batch processing
    batch_size: int = Field(default=1, title="Batch size for detection")
    
    # Confidence thresholds
    min_confidence: float = Field(default=0.4, title="Minimum confidence for detection")
    dynamic_threshold: bool = Field(default=False, title="Enable dynamic confidence thresholding")
    
    # Detection frequency
    detect_pattern: Optional[List[int]] = Field(default=None, title="Pattern for detection frequency")
    
    @field_validator("model_merge_strategy")
    @classmethod
    def validate_merge_strategy(cls, v: str) -> str:
        """Validate the model merge strategy."""
        valid_strategies = ["highest_confidence", "specialized_first", "all"]
        if v not in valid_strategies:
            raise ValueError(f"Invalid merge strategy: {v}. Must be one of {valid_strategies}")
        return v
    
    @field_validator("roi_strategy")
    @classmethod
    def validate_roi_strategy(cls, v: str) -> str:
        """Validate the ROI strategy."""
        valid_strategies = ["full_frame", "motion", "zones", "custom"]
        if v not in valid_strategies:
            raise ValueError(f"Invalid ROI strategy: {v}. Must be one of {valid_strategies}")
        return v
