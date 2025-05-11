from typing import Dict, List, Optional, Union

from pydantic import Field

from arkos.config.base import ArkosBaseModel


class DoorbellEventConfig(ArkosBaseModel):
    """Doorbell event configuration."""

    name: str = Field(title="Event name")
    enabled: bool = Field(default=True, title="Enable this event")
    
    # Trigger settings
    trigger_type: str = Field(default="button", title="Trigger type (button, motion, object, audio)")
    trigger_objects: List[str] = Field(default_factory=lambda: ["person"], title="Objects that trigger this event")
    trigger_zones: List[str] = Field(default_factory=list, title="Zones that trigger this event")
    trigger_audio_threshold: float = Field(default=50.0, title="Audio threshold for triggering (dB)")
    
    # Notification settings
    notify: bool = Field(default=True, title="Send notification for this event")
    notification_title: str = Field(default="Doorbell Event", title="Notification title")
    notification_message: str = Field(default="{event_name} detected", title="Notification message")
    include_snapshot: bool = Field(default=True, title="Include snapshot in notification")
    
    # Recording settings
    record: bool = Field(default=True, title="Record this event")
    pre_capture: int = Field(default=5, title="Pre-capture time in seconds")
    post_capture: int = Field(default=10, title="Post-capture time in seconds")
    
    # Cooldown settings
    cooldown: int = Field(default=60, title="Cooldown period in seconds")


class DoorbellResponseConfig(ArkosBaseModel):
    """Doorbell response configuration."""

    name: str = Field(title="Response name")
    enabled: bool = Field(default=True, title="Enable this response")
    
    # Trigger settings
    trigger_events: List[str] = Field(default_factory=list, title="Events that trigger this response")
    
    # Audio response
    audio_file: Optional[str] = Field(default=None, title="Audio file to play")
    audio_text: Optional[str] = Field(default=None, title="Text to speak")
    audio_volume: int = Field(default=80, title="Audio volume (0-100)")
    
    # Visual response
    light_control: bool = Field(default=False, title="Control lights")
    light_color: str = Field(default="#FFFFFF", title="Light color (hex)")
    light_pattern: str = Field(default="solid", title="Light pattern (solid, blink, pulse)")
    light_duration: int = Field(default=10, title="Light duration in seconds")
    
    # Integration response
    run_script: Optional[str] = Field(default=None, title="Script to run")
    mqtt_message: Optional[Dict[str, str]] = Field(default=None, title="MQTT message to send")
    http_request: Optional[Dict[str, str]] = Field(default=None, title="HTTP request to send")


class DoorbellConfig(ArkosBaseModel):
    """Doorbell camera configuration."""

    enabled: bool = Field(default=True, title="Enable doorbell functionality")
    
    # Button settings
    button_enabled: bool = Field(default=True, title="Enable doorbell button detection")
    button_detection_method: str = Field(default="api", title="Button detection method (api, gpio, mqtt, webhook)")
    button_gpio_pin: Optional[int] = Field(default=None, title="GPIO pin for button detection")
    button_mqtt_topic: Optional[str] = Field(default=None, title="MQTT topic for button detection")
    button_webhook_path: Optional[str] = Field(default=None, title="Webhook path for button detection")
    
    # Audio settings
    audio_enabled: bool = Field(default=True, title="Enable doorbell audio")
    audio_input_device: Optional[str] = Field(default=None, title="Audio input device")
    audio_output_device: Optional[str] = Field(default=None, title="Audio output device")
    audio_detection_threshold: float = Field(default=50.0, title="Audio detection threshold (dB)")
    audio_detection_duration: float = Field(default=0.5, title="Audio detection duration (seconds)")
    
    # Two-way audio
    two_way_audio: bool = Field(default=False, title="Enable two-way audio")
    two_way_audio_quality: int = Field(default=8, title="Two-way audio quality (0-10)")
    two_way_audio_codec: str = Field(default="opus", title="Two-way audio codec")
    
    # Events
    events: Dict[str, DoorbellEventConfig] = Field(default_factory=dict, title="Doorbell events")
    
    # Responses
    responses: Dict[str, DoorbellResponseConfig] = Field(default_factory=dict, title="Doorbell responses")
    
    # Integration settings
    mqtt_enabled: bool = Field(default=False, title="Enable MQTT integration")
    mqtt_topic_prefix: str = Field(default="arkos/doorbell", title="MQTT topic prefix")
    
    # Advanced settings
    button_debounce_time: int = Field(default=1000, title="Button debounce time in milliseconds")
    event_timeout: int = Field(default=30, title="Event timeout in seconds")
    visitor_snapshot_quality: int = Field(default=90, title="Visitor snapshot quality (0-100)")
