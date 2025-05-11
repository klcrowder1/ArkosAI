from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class AudioConfig(ArkosBaseModel):
    """Audio configuration for a camera."""

    enabled: bool = Field(default=False, title="Enable audio processing")
    enabled_in_config: bool = Field(default=False, exclude=True)
    
    # Audio capture parameters
    sample_rate: int = Field(default=16000, title="Sample rate in Hz")
    channels: int = Field(default=1, title="Number of audio channels")
    
    # Audio detection parameters
    threshold: float = Field(default=0.5, title="Audio detection threshold")
    min_duration: float = Field(default=1.0, title="Minimum duration in seconds")
    max_duration: float = Field(default=30.0, title="Maximum duration in seconds")
    
    # Audio events
    events: Dict[str, Any] = Field(default_factory=dict, title="Audio events configuration")
    
    # Audio classification
    classification: Dict[str, Any] = Field(default_factory=dict, title="Audio classification configuration")
    
    # Audio storage
    storage: Dict[str, Any] = Field(default_factory=dict, title="Audio storage configuration")
    
    # Advanced options
    noise_reduction: bool = Field(default=False, title="Enable noise reduction")
    noise_reduction_params: Dict[str, Any] = Field(default_factory=dict, title="Noise reduction parameters")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: int) -> int:
        """Validate sample rate."""
        valid_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000]
        if v not in valid_rates:
            raise ValueError(f"Sample rate must be one of {valid_rates}, got {v}")
        return v
    
    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: int) -> int:
        """Validate channels."""
        if v < 1 or v > 2:
            raise ValueError(f"Channels must be 1 or 2, got {v}")
        return v
    
    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        """Validate threshold."""
        if v < 0 or v > 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {v}")
        return v
    
    @field_validator("min_duration", "max_duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate duration."""
        if v < 0:
            raise ValueError(f"Duration must be non-negative, got {v}")
        return v
