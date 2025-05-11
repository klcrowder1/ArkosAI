"""Base notification provider interface."""

import abc
import logging
from typing import Any, Dict, Optional

from arkos.notifications.types import NotificationData


logger = logging.getLogger(__name__)


class NotificationProvider(abc.ABC):
    """Base class for notification providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the notification provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        self.enabled = config.get("enabled", True)
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
        # Initialize the provider
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize the provider with configuration.
        
        This method should be overridden by subclasses to perform
        provider-specific initialization.
        """
        pass
    
    @abc.abstractmethod
    def send(self, notification: NotificationData) -> bool:
        """Send a notification.
        
        Args:
            notification: Notification data to send
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        pass
    
    def format_message(self, notification: NotificationData) -> str:
        """Format the notification message.
        
        Args:
            notification: Notification data to format
            
        Returns:
            Formatted message string
        """
        return notification.message
    
    def format_title(self, notification: NotificationData) -> str:
        """Format the notification title.
        
        Args:
            notification: Notification data to format
            
        Returns:
            Formatted title string
        """
        return notification.title
    
    def should_send(self, notification: NotificationData) -> bool:
        """Check if the notification should be sent.
        
        Args:
            notification: Notification data to check
            
        Returns:
            True if the notification should be sent, False otherwise
        """
        # Check if the provider is enabled
        if not self.enabled:
            return False
        
        # Check if this provider is in the notification's services list
        if notification.services and self.name.lower() not in [s.lower() for s in notification.services]:
            return False
        
        return True
    
    def cleanup(self) -> None:
        """Clean up resources used by the provider.
        
        This method should be overridden by subclasses to perform
        provider-specific cleanup.
        """
        pass
