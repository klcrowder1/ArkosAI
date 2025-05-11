from typing import Dict, List, Optional, Tuple, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class FisheyeDewarperConfig(ArkosBaseModel):
    """Fisheye dewarping configuration."""

    enabled: bool = Field(default=True, title="Enable dewarping")
    method: str = Field(default="opencv", title="Dewarping method (opencv, ffmpeg)")
    
    # Camera parameters
    camera_matrix: Optional[List[List[float]]] = Field(default=None, title="Camera matrix for dewarping")
    distortion_coeffs: Optional[List[float]] = Field(default=None, title="Distortion coefficients for dewarping")
    
    # Manual calibration
    center: Tuple[float, float] = Field(default=(0.5, 0.5), title="Center point of fisheye lens (x, y in normalized coordinates)")
    radius: float = Field(default=1.0, title="Radius of fisheye lens (in normalized coordinates)")
    fov: float = Field(default=180.0, title="Field of view in degrees")
    
    # Output settings
    output_width: int = Field(default=1920, title="Output width after dewarping")
    output_height: int = Field(default=1080, title="Output height after dewarping")


class FisheyeViewConfig(ArkosBaseModel):
    """Fisheye view configuration."""

    name: str = Field(title="View name")
    enabled: bool = Field(default=True, title="Enable this view")
    
    # View parameters
    pan: float = Field(default=0.0, title="Pan angle in degrees")
    tilt: float = Field(default=0.0, title="Tilt angle in degrees")
    zoom: float = Field(default=1.0, title="Zoom factor")
    
    # Output settings
    width: int = Field(default=640, title="View width")
    height: int = Field(default=480, title="View height")
    
    # Advanced settings
    rotation: float = Field(default=0.0, title="Rotation angle in degrees")
    flip_horizontal: bool = Field(default=False, title="Flip view horizontally")
    flip_vertical: bool = Field(default=False, title="Flip view vertically")


class FisheyeConfig(ArkosBaseModel):
    """Fisheye camera configuration."""

    enabled: bool = Field(default=True, title="Enable fisheye functionality")
    
    # Dewarping settings
    dewarper: FisheyeDewarperConfig = Field(default_factory=FisheyeDewarperConfig, title="Dewarping configuration")
    
    # View settings
    views: Dict[str, FisheyeViewConfig] = Field(default_factory=dict, title="Virtual views from fisheye camera")
    
    # Panorama settings
    panorama: bool = Field(default=False, title="Enable panorama view")
    panorama_width: int = Field(default=1920, title="Panorama view width")
    panorama_height: int = Field(default=480, title="Panorama view height")
    panorama_start_angle: float = Field(default=0.0, title="Panorama start angle in degrees")
    panorama_end_angle: float = Field(default=360.0, title="Panorama end angle in degrees")
    
    # Multi-view settings
    quad_view: bool = Field(default=False, title="Enable quad view")
    quad_view_width: int = Field(default=1280, title="Quad view width")
    quad_view_height: int = Field(default=720, title="Quad view height")
    
    # Advanced settings
    lens_type: str = Field(default="equidistant", title="Lens type (equidistant, equisolid, orthographic, stereographic)")
    calibration_file: Optional[str] = Field(default=None, title="Path to calibration file")
    auto_calibration: bool = Field(default=False, title="Enable automatic calibration")
