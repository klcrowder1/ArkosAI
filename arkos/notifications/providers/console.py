"""Console notification provider for debugging."""

import json
import logging
from typing import Any, Dict, Optional

from arkos.notifications.providers.base import NotificationProvider
from arkos.notifications.types import NotificationData


logger = logging.getLogger(__name__)


class ConsoleNotificationProvider(NotificationProvider):
    """Console notification provider for debugging."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the console notification provider.
        
        Args:
            config: Provider-specific configuration
        """
        super().__init__(config)
        self.pretty_print = self.config.get("pretty_print", True)
        self.include_data = self.config.get("include_data", False)
        self.log_level = self.config.get("log_level", "INFO").upper()
    
    def initialize(self) -> None:
        """Initialize the console provider."""
        if not self.enabled:
            return
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            self.logger.warning(f"Invalid log level: {self.log_level}. Using INFO.")
            self.log_level = "INFO"
        
        self.logger.info("Console notification provider initialized")
    
    def send(self, notification: NotificationData) -> bool:
        """Send a notification to the console.
        
        Args:
            notification: Notification data to send
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        if not self.should_send(notification):
            return False
        
        try:
            # Format the notification
            title = self.format_title(notification)
            message = self.format_message(notification)
            
            # Create the log message
            log_message = f"[{notification.notification_type}] {title}: {message}"
            
            # Add additional data if requested
            if self.include_data:
                data = notification.to_dict()
                if self.pretty_print:
                    data_str = json.dumps(data, indent=2)
                else:
                    data_str = json.dumps(data)
                log_message += f"\nData: {data_str}"
            
            # Log the message at the configured level
            log_func = getattr(self.logger, self.log_level.lower())
            log_func(log_message)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending console notification: {e}")
            return False
    
    def format_title(self, notification: NotificationData) -> str:
        """Format the notification title.
        
        Args:
            notification: Notification data to format
            
        Returns:
            Formatted title string
        """
        title = super().format_title(notification)
        
        # Add camera name if available
        if notification.camera:
            title = f"[{notification.camera}] {title}"
        
        return title
    
    def format_message(self, notification: NotificationData) -> str:
        """Format the notification message.
        
        Args:
            notification: Notification data to format
            
        Returns:
            Formatted message string
        """
        message = super().format_message(notification)
        
        # Add priority if not medium
        if notification.priority and notification.priority != "medium":
            message = f"({notification.priority.upper()}) {message}"
        
        return message
