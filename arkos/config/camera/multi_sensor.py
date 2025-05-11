from typing import Dict, List, Optional, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class SensorConfig(ArkosBaseModel):
    """Individual sensor configuration for multi-sensor cameras."""

    name: str = Field(title="Sensor name")
    enabled: bool = Field(default=True, title="Enable this sensor")
    
    # Stream settings
    stream_url: str = Field(title="Stream URL for this sensor")
    input_args: Optional[str] = Field(default=None, title="Input arguments for FFmpeg")
    
    # Sensor position
    position: str = Field(default="unknown", title="Position of the sensor (front, back, left, right, top, bottom)")
    
    # Sensor capabilities
    has_ptz: bool = Field(default=False, title="Whether this sensor has PTZ capabilities")
    has_audio: bool = Field(default=False, title="Whether this sensor has audio capabilities")
    has_ir: bool = Field(default=False, title="Whether this sensor has IR capabilities")
    
    # Detection settings
    detect: bool = Field(default=True, title="Enable object detection for this sensor")
    detect_width: Optional[int] = Field(default=None, title="Detection width for this sensor")
    detect_height: Optional[int] = Field(default=None, title="Detection height for this sensor")
    detect_fps: Optional[int] = Field(default=None, title="Detection FPS for this sensor")
    
    # Recording settings
    record: bool = Field(default=True, title="Enable recording for this sensor")
    
    # Zones specific to this sensor
    zones: List[str] = Field(default_factory=list, title="Zones specific to this sensor")


class SensorGroupConfig(ArkosBaseModel):
    """Sensor group configuration for multi-sensor cameras."""

    name: str = Field(title="Group name")
    sensors: List[str] = Field(default_factory=list, title="List of sensors in this group")
    
    # Group settings
    stitching: bool = Field(default=False, title="Enable image stitching for this group")
    stitching_width: int = Field(default=1920, title="Width of stitched image")
    stitching_height: int = Field(default=1080, title="Height of stitched image")
    
    # Detection settings for the group
    unified_detection: bool = Field(default=False, title="Enable unified detection across sensors")
    
    # Recording settings for the group
    unified_recording: bool = Field(default=False, title="Enable unified recording across sensors")


class MultiSensorConfig(ArkosBaseModel):
    """Multi-sensor camera configuration."""

    enabled: bool = Field(default=True, title="Enable multi-sensor functionality")
    
    # Sensors
    sensors: Dict[str, SensorConfig] = Field(default_factory=dict, title="Individual sensors")
    
    # Sensor groups
    groups: Dict[str, SensorGroupConfig] = Field(default_factory=dict, title="Sensor groups")
    
    # Global settings
    default_group: Optional[str] = Field(default=None, title="Default sensor group")
    
    # Stitching settings
    stitching_method: str = Field(default="homography", title="Image stitching method (homography, cylindrical, spherical)")
    stitching_quality: int = Field(default=90, title="Stitching quality (0-100)")
    
    # Synchronization settings
    sync_detection: bool = Field(default=True, title="Synchronize detection across sensors")
    sync_recording: bool = Field(default=True, title="Synchronize recording across sensors")
    
    # Advanced settings
    sensor_overlap: float = Field(default=0.2, title="Overlap between sensors (0.0-1.0)")
    calibration_file: Optional[str] = Field(default=None, title="Path to calibration file")
    auto_calibration: bool = Field(default=False, title="Enable automatic calibration")
