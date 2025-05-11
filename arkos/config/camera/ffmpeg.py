from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class FfmpegInputConfig(ArkosBaseModel):
    """FFmpeg input configuration."""

    path: str = Field(title="Path to the input stream")
    roles: Set[str] = Field(default_factory=set, title="Roles for this input")
    input_args: Optional[str] = Field(default=None, title="Input arguments for FFmpeg")
    global_args: Optional[str] = Field(default=None, title="Global arguments for FFmpeg")


class FfmpegOutputArgsConfig(ArkosBaseModel):
    """FFmpeg output arguments configuration."""

    detect: Optional[str] = Field(default=None, title="Output arguments for detect role")
    record: Optional[str] = Field(default="-f segment -segment_time 10 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy", title="Output arguments for record role")
    rtmp: Optional[str] = Field(default="-c copy -f flv", title="Output arguments for RTMP role")
    clips: Optional[str] = Field(default="-f mp4 -c copy", title="Output arguments for clips role")
    audio: Optional[str] = Field(default="-f wav -ar 16000 -ac 1", title="Output arguments for audio role")
    snapshots: Optional[str] = Field(default="-frames:v 1 -q:v 2", title="Output arguments for snapshots role")


class FfmpegConfig(ArkosBaseModel):
    """FFmpeg configuration for a camera."""

    inputs: List[FfmpegInputConfig] = Field(default_factory=list, title="Input configurations")
    output_args: FfmpegOutputArgsConfig = Field(default_factory=FfmpegOutputArgsConfig, title="Output arguments")
    hwaccel_args: Optional[str] = Field(default=None, title="Hardware acceleration arguments")
    
    # Advanced options
    global_args: Optional[str] = Field(default=None, title="Global arguments for all FFmpeg commands")
    input_args: Optional[str] = Field(default=None, title="Input arguments for all inputs")
    
    # Streaming options
    stream_quality: Dict[str, Any] = Field(default_factory=dict, title="Stream quality settings")
    stream_profiles: Dict[str, Any] = Field(default_factory=dict, title="Stream profile settings")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
