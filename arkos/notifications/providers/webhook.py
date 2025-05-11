"""Webhook notification provider."""

import json
import logging
import time
from typing import Any, Dict, Optional
import urllib.parse

import requests

from arkos.notifications.providers.base import NotificationProvider
from arkos.notifications.types import NotificationData


logger = logging.getLogger(__name__)


class WebhookNotificationProvider(NotificationProvider):
    """Webhook notification provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the webhook notification provider.
        
        Args:
            config: Provider-specific configuration
        """
        super().__init__(config)
        self.urls = self.config.get("urls", [])
        self.timeout = self.config.get("timeout", 10)
        self.headers = self.config.get("headers", {})
        self.method = self.config.get("method", "POST").upper()
        self.include_snapshot = self.config.get("include_snapshot", False)
        self.include_clip = self.config.get("include_clip", False)
        self.verify_ssl = self.config.get("verify_ssl", True)
    
    def initialize(self) -> None:
        """Initialize the webhook provider."""
        if not self.enabled:
            return
        
        # Validate configuration
        if not self.urls:
            self.logger.error("No webhook URLs configured")
            self.enabled = False
            return
        
        # Convert single URL to list
        if isinstance(self.urls, str):
            self.urls = [self.urls]
        
        # Validate method
        valid_methods = ["GET", "POST", "PUT"]
        if self.method not in valid_methods:
            self.logger.error(f"Invalid webhook method: {self.method}. Must be one of {valid_methods}")
            self.method = "POST"
        
        self.logger.info(f"Webhook provider initialized with {len(self.urls)} URLs")
    
    def send(self, notification: NotificationData) -> bool:
        """Send a notification via webhook.
        
        Args:
            notification: Notification data to send
            
        Returns:
            True if the notification was sent successfully to at least one URL, False otherwise
        """
        if not self.should_send(notification):
            return False
        
        # Convert notification to payload
        payload = notification.to_dict()
        
        # Add URLs for media if requested
        if self.include_snapshot and notification.snapshot_path:
            payload["snapshot_url"] = self._get_media_url(notification.snapshot_path)
        
        if self.include_clip and notification.clip_path:
            payload["clip_url"] = self._get_media_url(notification.clip_path)
        
        # Send to all configured URLs
        success = False
        for url in self.urls:
            try:
                if self.method == "GET":
                    # For GET requests, add parameters to URL
                    params = {k: json.dumps(v) if isinstance(v, (dict, list)) else v 
                             for k, v in payload.items()}
                    response = requests.get(
                        url, 
                        params=params,
                        headers=self.headers,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                else:
                    # For POST/PUT requests, send JSON payload
                    response = requests.request(
                        self.method,
                        url,
                        json=payload,
                        headers=self.headers,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                
                if response.status_code < 400:
                    self.logger.debug(f"Webhook notification sent to {url} with status {response.status_code}")
                    success = True
                else:
                    self.logger.error(f"Failed to send webhook notification to {url}: {response.status_code} {response.text}")
            
            except Exception as e:
                self.logger.error(f"Error sending webhook notification to {url}: {e}")
        
        return success
    
    def _get_media_url(self, path: str) -> str:
        """Convert a local media path to a URL.
        
        Args:
            path: Local path to media file
            
        Returns:
            URL to access the media file
        """
        # If path is already a URL, return it
        if path.startswith(("http://", "https://")):
            return path
        
        # Otherwise, construct URL based on configuration
        base_url = self.config.get("base_url", "")
        if not base_url:
            return path
        
        # Ensure base URL ends with slash
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Remove leading slash from path if present
        if path.startswith("/"):
            path = path[1:]
        
        return urllib.parse.urljoin(base_url, path)
