from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from arkos.config.base import ArkosBaseModel
from arkos.util.builtin import deep_merge

logger = logging.getLogger(__name__)


class CameraTypeEnum(str, Enum):
    """Camera type enumeration."""

    DEFAULT = "default"
    LPR = "lpr"
    FACE = "face"
    SPECIALIZED = "specialized"


class CameraLiveConfig(ArkosBaseModel):
    """Live view configuration for a camera."""

    quality: int = Field(default=8, ge=1, le=31, title="JPEG quality (1-31, lower is higher quality)")
    height: Optional[int] = Field(default=None, title="Height of the live view")
    width: Optional[int] = Field(default=None, title="Width of the live view")
    streams: Dict[str, str] = Field(default_factory=dict, title="Stream configurations")


class ZoneConfig(ArkosBaseModel):
    """Zone configuration for a camera."""

    coordinates: Union[str, List[str]] = Field(title="Coordinates of the zone")
    objects: Set[str] = Field(default_factory=set, title="Objects to track in this zone")
    inertia: int = Field(default=3, title="Inertia for object tracking in this zone")
    contour: Optional[np.ndarray] = Field(default=None, exclude=True)

    def generate_contour(self, frame_shape: Tuple[int, int]) -> None:
        """Generate contour for the zone."""
        from arkos.util.config import get_relative_coordinates
        from arkos.util.image import create_mask

        coordinates = get_relative_coordinates(self.coordinates, frame_shape)
        if coordinates:
            mask = create_mask(frame_shape, coordinates)
            import cv2
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.contour = contours[0]

    @field_serializer("contour", when_used="json")
    def serialize_contour(self, value: Any, info):
        return None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OnvifConfig(ArkosBaseModel):
    """ONVIF configuration for a camera."""

    host: Optional[str] = Field(default=None, title="ONVIF host")
    port: int = Field(default=80, title="ONVIF port")
    username: Optional[str] = Field(default=None, title="ONVIF username")
    password: Optional[str] = Field(default=None, title="ONVIF password")
    autotracking: "OnvifAutotrackingConfig" = Field(default_factory=lambda: OnvifAutotrackingConfig(), title="Autotracking configuration")


class OnvifAutotrackingConfig(ArkosBaseModel):
    """ONVIF autotracking configuration."""

    enabled: bool = Field(default=False, title="Enable autotracking")
    enabled_in_config: bool = Field(default=False, exclude=True)
    required_zones: List[str] = Field(default_factory=list, title="Zones required for autotracking")
    calibration_points: List[Dict[str, Any]] = Field(default_factory=list, title="Calibration points for autotracking")
    zoom_factor: float = Field(default=1.0, title="Zoom factor for autotracking")
    track_timeout: int = Field(default=10, title="Tracking timeout in seconds")
    cooldown: int = Field(default=30, title="Cooldown period in seconds")


class CameraConfig(ArkosBaseModel):
    """Camera configuration."""

    name: str = Field(title="Camera name")
    enabled: bool = Field(default=True, title="Enable camera")
    enabled_in_config: bool = Field(default=True, exclude=True)
    type: CameraTypeEnum = Field(default=CameraTypeEnum.DEFAULT, title="Camera type")
    
    # Camera components
    ffmpeg: "FfmpegConfig" = Field(title="FFmpeg configuration")
    detect: "DetectConfig" = Field(default_factory=lambda: DetectConfig(), title="Detection configuration")
    motion: Optional["MotionConfig"] = Field(default=None, title="Motion detection configuration")
    objects: "ObjectConfig" = Field(default_factory=lambda: ObjectConfig(), title="Object detection configuration")
    record: "RecordConfig" = Field(default_factory=lambda: RecordConfig(), title="Recording configuration")
    snapshots: "SnapshotsConfig" = Field(default_factory=lambda: SnapshotsConfig(), title="Snapshots configuration")
    live: CameraLiveConfig = Field(default_factory=CameraLiveConfig, title="Live view configuration")
    audio: "AudioConfig" = Field(default_factory=lambda: AudioConfig(), title="Audio configuration")
    onvif: OnvifConfig = Field(default_factory=OnvifConfig, title="ONVIF configuration")
    zones: Dict[str, ZoneConfig] = Field(default_factory=dict, title="Zone configurations")
    timestamp_style: "TimestampStyleConfig" = Field(default_factory=lambda: TimestampStyleConfig(), title="Timestamp style configuration")
    notifications: "NotificationConfig" = Field(default_factory=lambda: NotificationConfig(), title="Notification configuration")
    review: "ReviewConfig" = Field(default_factory=lambda: ReviewConfig(), title="Review configuration")
    birdseye: "BirdseyeConfig" = Field(default_factory=lambda: BirdseyeConfig(), title="Birdseye configuration")
    genai: "GenAIConfig" = Field(default_factory=lambda: GenAIConfig(), title="Generative AI configuration")
    face_recognition: "FaceRecognitionConfig" = Field(default_factory=lambda: FaceRecognitionConfig(), title="Face recognition configuration")
    lpr: "LicensePlateRecognitionConfig" = Field(default_factory=lambda: LicensePlateRecognitionConfig(), title="License plate recognition configuration")
    
    # Advanced configuration options
    rtmp: Dict[str, Any] = Field(default_factory=dict, title="RTMP configuration")
    mqtt: Dict[str, Any] = Field(default_factory=dict, title="MQTT configuration")
    
    # Camera capabilities
    capabilities: Dict[str, Any] = Field(default_factory=dict, title="Camera capabilities")
    
    # Runtime properties
    frame_shape: Tuple[int, int] = Field(default=(1, 1), exclude=True)
    ffmpeg_cmds: Dict[str, List[str]] = Field(default_factory=dict, exclude=True)

    @property
    def best_image_dimensions(self) -> Tuple[int, int]:
        """Get the best dimensions for snapshots."""
        return (self.detect.width, self.detect.height)

    def create_ffmpeg_cmds(self) -> None:
        """Create FFmpeg commands for the camera."""
        from arkos.ffmpeg_presets import presets

        self.ffmpeg_cmds = {}
        
        # Set frame shape based on detect dimensions
        if self.detect.height and self.detect.width:
            self.frame_shape = (self.detect.height, self.detect.width)

        # Create FFmpeg commands for each role
        for input_config in self.ffmpeg.inputs:
            for role in input_config.roles:
                if role in self.ffmpeg_cmds:
                    continue
                
                # Get preset for the role
                preset = presets.get(role, {})
                
                # Create command
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "warning",
                    "-avoid_negative_ts",
                    "make_zero",
                    "-fflags",
                    "+genpts+discardcorrupt",
                    "-rtsp_transport",
                    "tcp",
                    "-stimeout",
                    "5000000",
                    "-use_wallclock_as_timestamps",
                    "1",
                ]
                
                # Add hwaccel args if specified
                if self.ffmpeg.hwaccel_args:
                    ffmpeg_cmd.extend(self.ffmpeg.hwaccel_args.split(" "))
                
                # Add input args
                if input_config.input_args:
                    ffmpeg_cmd.extend(input_config.input_args.split(" "))
                
                # Add input path
                ffmpeg_cmd.extend(["-i", input_config.path])
                
                # Add output args
                output_args = getattr(self.ffmpeg.output_args, role, None)
                if output_args:
                    ffmpeg_cmd.extend(output_args.split(" "))
                elif preset.get("output_args"):
                    ffmpeg_cmd.extend(preset["output_args"].split(" "))
                
                # Add role-specific args
                if role == "detect":
                    ffmpeg_cmd.extend([
                        "-vf",
                        f"fps={self.detect.fps},scale={self.detect.width}:{self.detect.height}",
                    ])
                
                # Add output format
                if preset.get("output_format"):
                    ffmpeg_cmd.extend(["-f", preset["output_format"]])
                
                # Add output path placeholder
                ffmpeg_cmd.append("pipe:")
                
                # Store command
                self.ffmpeg_cmds[role] = ffmpeg_cmd

    @model_validator(mode="after")
    def post_validation(self, info) -> Self:
        """Validate camera configuration after initialization."""
        # Set frame shape based on detect dimensions
        if self.detect.height and self.detect.width:
            self.frame_shape = (self.detect.height, self.detect.width)
        
        return self
