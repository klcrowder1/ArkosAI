from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class FilterConfig(ArkosBaseModel):
    """Filter configuration for object detection."""

    min_area: Optional[Union[int, float]] = Field(default=None, title="Minimum area for object detection")
    max_area: Optional[Union[int, float]] = Field(default=None, title="Maximum area for object detection")
    min_score: float = Field(default=0.5, title="Minimum confidence score for object detection")
    min_ratio: Optional[float] = Field(default=None, title="Minimum aspect ratio for object detection")
    max_ratio: Optional[float] = Field(default=None, title="Maximum aspect ratio for object detection")
    threshold: Optional[float] = Field(default=None, title="Threshold for object detection")
    mask: Optional[Union[str, List[str]]] = Field(default=None, title="Mask for object detection")
    
    # Advanced filtering options
    min_height: Optional[int] = Field(default=None, title="Minimum height for object detection")
    max_height: Optional[int] = Field(default=None, title="Maximum height for object detection")
    min_width: Optional[int] = Field(default=None, title="Minimum width for object detection")
    max_width: Optional[int] = Field(default=None, title="Maximum width for object detection")
    
    # Temporal filtering
    min_frames: Optional[int] = Field(default=None, title="Minimum number of frames for object detection")
    max_frames: Optional[int] = Field(default=None, title="Maximum number of frames for object detection")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")


class ObjectConfig(ArkosBaseModel):
    """Object detection configuration for a camera."""

    track: Set[str] = Field(default_factory=set, title="Objects to track")
    filters: Dict[str, FilterConfig] = Field(default_factory=dict, title="Object filters")
    mask: Optional[Union[str, List[str]]] = Field(default=None, title="Global mask for object detection")
    
    # Object tracking parameters
    track_labels: bool = Field(default=True, title="Track object labels")
    track_boxes: bool = Field(default=True, title="Track object bounding boxes")
    
    # Advanced object tracking options
    tracking_mode: str = Field(default="centroid", title="Object tracking mode")
    tracking_config: Dict[str, Any] = Field(default_factory=dict, title="Object tracking configuration")
    
    # Object classification
    classification: Dict[str, Any] = Field(default_factory=dict, title="Object classification configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    # Runtime properties
    all_objects: Set[str] = Field(default_factory=set, exclude=True)
    
    @field_validator("tracking_mode")
    @classmethod
    def validate_tracking_mode(cls, v: str) -> str:
        """Validate the tracking mode."""
        valid_modes = ["centroid", "iou", "norfair", "deep_sort", "custom"]
        if v not in valid_modes:
            raise ValueError(f"Invalid tracking mode: {v}. Must be one of {valid_modes}")
        return v
    
    def parse_all_objects(self, cameras: Dict[str, Any]) -> None:
        """Parse all objects from cameras."""
        all_objects = set()
        
        # Add objects from this camera
        all_objects.update(self.track)
        
        # Add objects from all cameras
        for camera in cameras.values():
            all_objects.update(camera.objects.track)
            
            # Add objects from zones
            for zone in camera.zones.values():
                all_objects.update(zone.objects)
        
        self.all_objects = all_objects
