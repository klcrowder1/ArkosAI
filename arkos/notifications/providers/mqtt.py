"""MQTT notification provider."""

import json
import logging
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from arkos.notifications.providers.base import NotificationProvider
from arkos.notifications.types import NotificationData


logger = logging.getLogger(__name__)


class MqttNotificationProvider(NotificationProvider):
    """MQTT notification provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the MQTT notification provider.
        
        Args:
            config: Provider-specific configuration
        """
        super().__init__(config)
        self.client = None
        self.connected = False
        self.topic_prefix = self.config.get("topic_prefix", "arkos/notifications")
    
    def initialize(self) -> None:
        """Initialize the MQTT client."""
        if not self.enabled:
            return
        
        # Get MQTT configuration
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 1883)
        username = self.config.get("username")
        password = self.config.get("password")
        client_id = self.config.get("client_id", f"arkos-notifications-{int(time.time())}")
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=client_id)
        
        # Set up authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        # Connect to MQTT broker
        try:
            self.client.connect(host, port)
            self.client.loop_start()
            self.logger.info(f"Connected to MQTT broker at {host}:{port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            self.enabled = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.connected = True
            self.logger.info("Connected to MQTT broker")
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection from MQTT broker with code {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def send(self, notification: NotificationData) -> bool:
        """Send a notification via MQTT.
        
        Args:
            notification: Notification data to send
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        if not self.should_send(notification) or not self.connected:
            return False
        
        try:
            # Determine the topic based on notification type and camera
            topic_parts = [self.topic_prefix]
            
            if notification.notification_type:
                topic_parts.append(notification.notification_type)
            
            if notification.camera:
                topic_parts.append(notification.camera)
            
            topic = "/".join(topic_parts)
            
            # Convert notification to JSON
            payload = json.dumps(notification.to_dict())
            
            # Publish the message
            result = self.client.publish(topic, payload, qos=1)
            
            # Check if the message was published successfully
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish MQTT message: {mqtt.error_string(result.rc)}")
                return False
            
            self.logger.debug(f"Published notification to {topic}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending MQTT notification: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up MQTT client resources."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                self.logger.info("Disconnected from MQTT broker")
            except Exception as e:
                self.logger.error(f"Error disconnecting from MQTT broker: {e}")
