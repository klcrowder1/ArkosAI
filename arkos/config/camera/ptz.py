from typing import Dict, List, Optional, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class PTZPresetConfig(ArkosBaseModel):
    """PTZ preset configuration."""

    name: str = Field(title="Preset name")
    position: Optional[Dict[str, float]] = Field(default=None, title="Preset position (pan, tilt, zoom)")
    home: bool = Field(default=False, title="Whether this is the home position")


class PTZPatrolConfig(ArkosBaseModel):
    """PTZ patrol configuration."""

    name: str = Field(title="Patrol name")
    presets: List[str] = Field(default_factory=list, title="List of preset names to patrol")
    dwell_time: int = Field(default=10, title="Time to dwell at each preset in seconds")
    speed: float = Field(default=1.0, title="Speed of movement between presets")


class PTZConfig(ArkosBaseModel):
    """PTZ camera configuration."""

    enabled: bool = Field(default=True, title="Enable PTZ functionality")
    protocol: str = Field(default="onvif", title="PTZ protocol (onvif, pelco-d, pelco-p, etc.)")
    
    # Movement settings
    default_speed: float = Field(default=0.5, title="Default movement speed (0.0-1.0)")
    invert_pan: bool = Field(default=False, title="Invert pan direction")
    invert_tilt: bool = Field(default=False, title="Invert tilt direction")
    
    # Presets
    presets: Dict[str, PTZPresetConfig] = Field(default_factory=dict, title="PTZ presets")
    home_preset: Optional[str] = Field(default=None, title="Home preset name")
    return_to_home: bool = Field(default=False, title="Return to home position after timeout")
    return_timeout: int = Field(default=300, title="Timeout before returning to home position (seconds)")
    
    # Patrols
    patrols: Dict[str, PTZPatrolConfig] = Field(default_factory=dict, title="PTZ patrols")
    default_patrol: Optional[str] = Field(default=None, title="Default patrol name")
    
    # Auto-tracking
    autotracking: bool = Field(default=False, title="Enable auto-tracking")
    tracking_sensitivity: float = Field(default=0.5, title="Tracking sensitivity (0.0-1.0)")
    tracking_objects: List[str] = Field(default_factory=lambda: ["person"], title="Objects to track")
    tracking_timeout: int = Field(default=30, title="Tracking timeout in seconds")
    tracking_cooldown: int = Field(default=60, title="Tracking cooldown in seconds")
    
    # Advanced settings
    limits: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "pan": {"min": -180.0, "max": 180.0},
            "tilt": {"min": -90.0, "max": 90.0},
            "zoom": {"min": 1.0, "max": 10.0},
        },
        title="Movement limits",
    )
    continuous_move_timeout: int = Field(default=5, title="Timeout for continuous move commands (seconds)")
