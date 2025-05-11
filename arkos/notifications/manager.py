"""Notification manager for Arkos AI."""

import logging
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Type, Union

from arkos.config import FrigateConfig
from arkos.events.types import EventData, EventTypeEnum
from arkos.notifications.providers import (
    ConsoleNotificationProvider,
    MqttNotificationProvider,
    NotificationProvider,
    WebhookNotificationProvider,
)
from arkos.notifications.types import (
    AlertNotificationData,
    EventNotificationData,
    NotificationData,
    NotificationPriorityEnum,
    NotificationTypeEnum,
    SystemNotificationData,
)


logger = logging.getLogger(__name__)


class NotificationManager:
    """Manager for handling notifications."""

    def __init__(self, config: FrigateConfig):
        """Initialize the notification manager.
        
        Args:
            config: Arkos configuration
        """
        self.config = config
        self.providers: Dict[str, NotificationProvider] = {}
        self.cooldowns: Dict[str, Dict[str, float]] = {}  # camera -> label -> last notification time
        self.lock = threading.RLock()
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize notification providers based on configuration."""
        # Get global notification configuration
        notification_config = getattr(self.config, "notifications", {})
        
        # Initialize console provider (always enabled for debugging)
        console_config = notification_config.get("console", {"enabled": True})
        self.providers["console"] = ConsoleNotificationProvider(console_config)
        
        # Initialize MQTT provider if configured
        mqtt_config = notification_config.get("mqtt", {})
        if mqtt_config.get("enabled", False):
            self.providers["mqtt"] = MqttNotificationProvider(mqtt_config)
        
        # Initialize webhook provider if configured
        webhook_config = notification_config.get("webhook", {})
        if webhook_config.get("enabled", False):
            self.providers["webhook"] = WebhookNotificationProvider(webhook_config)
        
        # Log initialized providers
        enabled_providers = [name for name, provider in self.providers.items() if provider.enabled]
        logger.info(f"Notification providers initialized: {', '.join(enabled_providers)}")
    
    def send_notification(self, notification: NotificationData) -> bool:
        """Send a notification using all enabled providers.
        
        Args:
            notification: Notification data to send
            
        Returns:
            True if the notification was sent successfully by at least one provider, False otherwise
        """
        if not self.providers:
            logger.warning("No notification providers available")
            return False
        
        # Check if we should send this notification (cooldown)
        if not self._should_send_notification(notification):
            return False
        
        # Send notification to all enabled providers
        success = False
        for name, provider in self.providers.items():
            if provider.enabled and provider.should_send(notification):
                try:
                    if provider.send(notification):
                        success = True
                except Exception as e:
                    logger.error(f"Error sending notification with provider {name}: {e}")
        
        return success
    
    def _should_send_notification(self, notification: NotificationData) -> bool:
        """Check if a notification should be sent based on cooldown settings.
        
        Args:
            notification: Notification data to check
            
        Returns:
            True if the notification should be sent, False otherwise
        """
        # System notifications are not subject to cooldown
        if notification.notification_type == NotificationTypeEnum.SYSTEM:
            return True
        
        # If no camera or no cooldown settings, always send
        if not notification.camera:
            return True
        
        with self.lock:
            # Get camera-specific notification config
            camera_config = self.config.cameras.get(notification.camera, {})
            notification_config = getattr(camera_config, "notifications", None)
            
            # If no notification config, use default cooldown
            if not notification_config:
                return True
            
            # Get cooldown period
            cooldown = notification_config.cooldown
            
            # If cooldown is 0, always send
            if cooldown <= 0:
                return True
            
            # Check if we're in cooldown period
            camera_cooldowns = self.cooldowns.setdefault(notification.camera, {})
            
            # For event notifications, use label as key
            if hasattr(notification, "label"):
                key = getattr(notification, "label")
            else:
                key = notification.notification_type
            
            # Check if we're in cooldown period
            last_time = camera_cooldowns.get(key, 0)
            current_time = time.time()
            
            if current_time - last_time < cooldown:
                logger.debug(f"Notification for {notification.camera}/{key} in cooldown period")
                return False
            
            # Update last notification time
            camera_cooldowns[key] = current_time
            
            return True
    
    def notify_event(
        self,
        event: EventData,
        title: Optional[str] = None,
        message: Optional[str] = None,
        priority: str = NotificationPriorityEnum.MEDIUM,
        snapshot_path: Optional[str] = None,
        clip_path: Optional[str] = None,
        preview_path: Optional[str] = None,
    ) -> bool:
        """Send a notification for an event.
        
        Args:
            event: Event data
            title: Notification title (defaults to event label)
            message: Notification message (defaults to auto-generated message)
            priority: Notification priority
            snapshot_path: Path to snapshot image
            clip_path: Path to video clip
            preview_path: Path to preview image
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        # Generate notification ID
        notification_id = f"event_{event.id}_{int(time.time())}"
        
        # Generate default title if not provided
        if not title:
            if hasattr(event, "label"):
                title = f"{event.label.capitalize()} detected"
            else:
                title = f"Event detected"
        
        # Generate default message if not provided
        if not message:
            if hasattr(event, "label") and event.camera:
                message = f"{event.label.capitalize()} detected on {event.camera}"
            elif event.camera:
                message = f"Event detected on {event.camera}"
            else:
                message = "Event detected"
        
        # Create notification data
        if hasattr(event, "event_type") and hasattr(event, "label") and hasattr(event, "score"):
            # Create event-specific notification
            notification = EventNotificationData(
                id=notification_id,
                title=title,
                message=message,
                timestamp=event.start_time,
                event_id=event.id,
                event_type=getattr(event, "event_type", "unknown"),
                camera=event.camera,
                label=getattr(event, "label", "unknown"),
                score=getattr(event, "score", 0.0),
                priority=priority,
                snapshot_path=snapshot_path or getattr(event, "snapshot_path", None),
                clip_path=clip_path or getattr(event, "clip_path", None),
                preview_path=preview_path or getattr(event, "preview_path", None),
                zones=getattr(event, "zones", []),
            )
        else:
            # Create generic notification
            notification = NotificationData(
                id=notification_id,
                title=title,
                message=message,
                timestamp=event.start_time,
                notification_type=NotificationTypeEnum.EVENT,
                priority=priority,
                camera=event.camera,
                event_id=event.id,
                snapshot_path=snapshot_path,
                clip_path=clip_path,
                preview_path=preview_path,
            )
        
        # Send notification
        return self.send_notification(notification)
    
    def notify_alert(
        self,
        alert_type: str,
        severity: str,
        source: str,
        title: str,
        message: str,
        camera: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        priority: str = NotificationPriorityEnum.HIGH,
    ) -> bool:
        """Send an alert notification.
        
        Args:
            alert_type: Type of alert
            severity: Severity of the alert
            source: Source of the alert
            title: Alert title
            message: Alert message
            camera: Camera name if applicable
            snapshot_path: Path to snapshot image if available
            priority: Notification priority
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        # Generate notification ID
        notification_id = f"alert_{alert_type}_{int(time.time())}"
        
        # Create notification data
        notification = AlertNotificationData(
            id=notification_id,
            title=title,
            message=message,
            timestamp=time.time(),
            alert_type=alert_type,
            severity=severity,
            source=source,
            priority=priority,
            camera=camera,
            snapshot_path=snapshot_path,
        )
        
        # Send notification
        return self.send_notification(notification)
    
    def notify_system(
        self,
        system_type: str,
        component: str,
        title: str,
        message: str,
        priority: str = NotificationPriorityEnum.MEDIUM,
    ) -> bool:
        """Send a system notification.
        
        Args:
            system_type: Type of system notification
            component: System component
            title: Notification title
            message: Notification message
            priority: Notification priority
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        # Generate notification ID
        notification_id = f"system_{system_type}_{int(time.time())}"
        
        # Create notification data
        notification = SystemNotificationData(
            id=notification_id,
            title=title,
            message=message,
            timestamp=time.time(),
            system_type=system_type,
            component=component,
            priority=priority,
        )
        
        # Send notification
        return self.send_notification(notification)
    
    def cleanup(self) -> None:
        """Clean up resources used by notification providers."""
        for name, provider in self.providers.items():
            try:
                provider.cleanup()
                logger.debug(f"Cleaned up notification provider: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up notification provider {name}: {e}")
