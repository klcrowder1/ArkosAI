from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class GenAIConfig(ArkosBaseModel):
    """Generative AI configuration for a camera."""

    enabled: bool = Field(default=False, title="Enable generative AI")
    
    # Model configuration
    model: str = Field(default="default", title="Generative AI model")
    model_params: Dict[str, Any] = Field(default_factory=dict, title="Model parameters")
    
    # Event description
    event_description: bool = Field(default=True, title="Generate event descriptions")
    event_description_prompt: Optional[str] = Field(default=None, title="Event description prompt")
    
    # Image enhancement
    image_enhancement: bool = Field(default=False, title="Enable image enhancement")
    image_enhancement_params: Dict[str, Any] = Field(default_factory=dict, title="Image enhancement parameters")
    
    # Object detection assistance
    object_detection_assist: bool = Field(default=False, title="Enable object detection assistance")
    object_detection_assist_params: Dict[str, Any] = Field(default_factory=dict, title="Object detection assistance parameters")
    
    # Scene understanding
    scene_understanding: bool = Field(default=False, title="Enable scene understanding")
    scene_understanding_params: Dict[str, Any] = Field(default_factory=dict, title="Scene understanding parameters")
    
    # API configuration
    api_config: Dict[str, Any] = Field(default_factory=dict, title="API configuration")
    
    # Rate limiting
    rate_limit: Dict[str, Any] = Field(default_factory=dict, title="Rate limiting configuration")
    
    # Experimental features
    experimental: Dict[str, Any] = Field(default_factory=dict, title="Experimental features")
    
    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model."""
        valid_models = ["default", "gpt-4", "gpt-3.5-turbo", "claude", "llama", "custom"]
        if v.lower() not in valid_models:
            raise ValueError(f"Model must be one of {valid_models}, got {v}")
        return v.lower()
