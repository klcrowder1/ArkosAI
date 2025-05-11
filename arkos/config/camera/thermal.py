from typing import Dict, List, Optional, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class ThermalPaletteConfig(ArkosBaseModel):
    """Thermal palette configuration."""

    name: str = Field(title="Palette name")
    colors: List[str] = Field(default_factory=list, title="List of colors in the palette")
    min_temp: float = Field(default=0.0, title="Minimum temperature for the palette (°C)")
    max_temp: float = Field(default=100.0, title="Maximum temperature for the palette (°C)")


class ThermalAlarmConfig(ArkosBaseModel):
    """Thermal alarm configuration."""

    enabled: bool = Field(default=False, title="Enable thermal alarm")
    threshold_high: float = Field(default=50.0, title="High temperature threshold (°C)")
    threshold_low: Optional[float] = Field(default=None, title="Low temperature threshold (°C)")
    duration: int = Field(default=5, title="Duration threshold must be exceeded (seconds)")
    cooldown: int = Field(default=60, title="Cooldown period after alarm (seconds)")
    zones: List[str] = Field(default_factory=list, title="Zones to monitor for temperature alarms")


class ThermalConfig(ArkosBaseModel):
    """Thermal camera configuration."""

    enabled: bool = Field(default=True, title="Enable thermal functionality")
    
    # Temperature settings
    unit: str = Field(default="celsius", title="Temperature unit (celsius, fahrenheit)")
    min_temp: float = Field(default=0.0, title="Minimum detectable temperature (°C)")
    max_temp: float = Field(default=100.0, title="Maximum detectable temperature (°C)")
    
    # Display settings
    palette: str = Field(default="iron", title="Default color palette")
    palettes: Dict[str, ThermalPaletteConfig] = Field(
        default_factory=lambda: {
            "iron": ThermalPaletteConfig(
                name="Iron",
                colors=["black", "purple", "red", "yellow", "white"],
                min_temp=0.0,
                max_temp=100.0,
            ),
            "rainbow": ThermalPaletteConfig(
                name="Rainbow",
                colors=["blue", "cyan", "green", "yellow", "red"],
                min_temp=0.0,
                max_temp=100.0,
            ),
        },
        title="Available color palettes",
    )
    
    # Overlay settings
    show_temp: bool = Field(default=True, title="Show temperature values in overlay")
    show_hotspot: bool = Field(default=True, title="Show hottest spot in overlay")
    show_coldspot: bool = Field(default=False, title="Show coldest spot in overlay")
    
    # Alarm settings
    alarms: Dict[str, ThermalAlarmConfig] = Field(default_factory=dict, title="Temperature alarms")
    
    # Advanced settings
    emissivity: float = Field(default=0.95, title="Emissivity value (0.0-1.0)")
    reflection_temp: float = Field(default=20.0, title="Reflection temperature (°C)")
    atmospheric_temp: float = Field(default=20.0, title="Atmospheric temperature (°C)")
    relative_humidity: float = Field(default=50.0, title="Relative humidity (%)")
    distance: float = Field(default=1.0, title="Distance to object (meters)")
    
    # Calibration
    calibration_points: List[Dict[str, float]] = Field(default_factory=list, title="Calibration points")
    auto_calibration: bool = Field(default=False, title="Enable automatic calibration")
    calibration_interval: int = Field(default=3600, title="Calibration interval (seconds)")
