"""
Unit tests for MQTT client module
"""

import json
import pytest
import time
from unittest.mock import MagicMock, patch, call

from arkos.comms.mqtt_client import MQTTClient


class TestMQTTClient:
    """Tests for the MQTTClient class"""

    def test_init(self):
        """Test initialization of MQTTClient"""
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
                "stats_interval": 60,
                "user": "test_user",
                "password": "test_password",
            }
        }
        
        client = MQTTClient(config)
        
        assert client.host == "localhost"
        assert client.port == 1883
        assert client.topic_prefix == "arkos"
        assert client.client_id == "arkos_test"
        assert client.stats_interval == 60
        assert client.user == "test_user"
        assert client.password == "test_password"
        assert client.connected is False

    def test_init_with_defaults(self):
        """Test initialization of MQTTClient with default values"""
        config = {
            "mqtt": {
                "host": "localhost",
            }
        }
        
        client = MQTTClient(config)
        
        assert client.host == "localhost"
        assert client.port == 1883  # Default
        assert client.topic_prefix == "arkos"  # Default
        assert client.client_id is not None  # Generated
        assert client.stats_interval == 60  # Default
        assert client.user is None  # Default
        assert client.password is None  # Default
        assert client.connected is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_connect(self, mock_client_class):
        """Test connecting to MQTT broker"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and loop_start methods
        mock_client.connect.return_value = 0
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        result = client.connect()
        
        # Check that client was created and connected
        mock_client_class.assert_called_once()
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        mock_client.loop_start.assert_called_once()
        
        # Check result
        assert result is True
        assert client.connected is True

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_connect_with_auth(self, mock_client_class):
        """Test connecting to MQTT broker with authentication"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and loop_start methods
        mock_client.connect.return_value = 0
        
        # Create client with auth
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
                "user": "test_user",
                "password": "test_password",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        result = client.connect()
        
        # Check that client was created and connected with auth
        mock_client.username_pw_set.assert_called_once_with("test_user", "test_password")
        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        
        # Check result
        assert result is True
        assert client.connected is True

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_connect_failure(self, mock_client_class):
        """Test handling connection failure"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect to fail
        mock_client.connect.side_effect = Exception("Connection failed")
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        result = client.connect()
        
        # Check result
        assert result is False
        assert client.connected is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_disconnect(self, mock_client_class):
        """Test disconnecting from MQTT broker"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and disconnect methods
        mock_client.connect.return_value = 0
        mock_client.disconnect.return_value = 0
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Disconnect
        client.disconnect()
        
        # Check that client was disconnected
        mock_client.disconnect.assert_called_once()
        mock_client.loop_stop.assert_called_once()
        
        # Check state
        assert client.connected is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_publish(self, mock_client_class):
        """Test publishing a message"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and publish methods
        mock_client.connect.return_value = 0
        mock_client.publish.return_value.rc = 0
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Publish message
        result = client.publish("test/topic", "test message")
        
        # Check that message was published
        mock_client.publish.assert_called_once_with("arkos/test/topic", "test message", 0, False)
        
        # Check result
        assert result is True

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_publish_json(self, mock_client_class):
        """Test publishing a JSON message"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and publish methods
        mock_client.connect.return_value = 0
        mock_client.publish.return_value.rc = 0
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Publish JSON message
        data = {"key": "value", "number": 42}
        result = client.publish_json("test/topic", data)
        
        # Check that message was published
        mock_client.publish.assert_called_once_with(
            "arkos/test/topic", 
            json.dumps(data), 
            0, 
            False
        )
        
        # Check result
        assert result is True

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_publish_not_connected(self, mock_client_class):
        """Test publishing when not connected"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Publish message without connecting
        result = client.publish("test/topic", "test message")
        
        # Check that message was not published
        mock_client.publish.assert_not_called()
        
        # Check result
        assert result is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_subscribe(self, mock_client_class):
        """Test subscribing to a topic"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and subscribe methods
        mock_client.connect.return_value = 0
        mock_client.subscribe.return_value = (0, 1)
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Subscribe to topic
        result = client.subscribe("test/topic")
        
        # Check that subscription was made
        mock_client.subscribe.assert_called_once_with("arkos/test/topic")
        
        # Check result
        assert result is True

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_subscribe_not_connected(self, mock_client_class):
        """Test subscribing when not connected"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Subscribe without connecting
        result = client.subscribe("test/topic")
        
        # Check that subscription was not made
        mock_client.subscribe.assert_not_called()
        
        # Check result
        assert result is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_on_connect(self, mock_client_class):
        """Test on_connect callback"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Get on_connect callback
        on_connect = mock_client.on_connect
        
        # Call on_connect with success
        on_connect(mock_client, None, None, 0)
        
        # Check that connected flag is set
        assert client.connected is True
        
        # Call on_connect with failure
        on_connect(mock_client, None, None, 1)
        
        # Check that connected flag is not set
        assert client.connected is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_on_disconnect(self, mock_client_class):
        """Test on_disconnect callback"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        client.connected = True
        
        # Get on_disconnect callback
        on_disconnect = mock_client.on_disconnect
        
        # Call on_disconnect
        on_disconnect(mock_client, None, 0)
        
        # Check that connected flag is cleared
        assert client.connected is False

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_on_message(self, mock_client_class):
        """Test on_message callback"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Create message handler
        message_handler = MagicMock()
        client.message_handlers["test/topic"] = message_handler
        
        # Get on_message callback
        on_message = mock_client.on_message
        
        # Create mock message
        mock_message = MagicMock()
        mock_message.topic = "arkos/test/topic"
        mock_message.payload = b"test message"
        
        # Call on_message
        on_message(mock_client, None, mock_message)
        
        # Check that message handler was called
        message_handler.assert_called_once_with("test message")

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_on_message_json(self, mock_client_class):
        """Test on_message callback with JSON payload"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Create message handler
        message_handler = MagicMock()
        client.message_handlers["test/topic"] = message_handler
        
        # Get on_message callback
        on_message = mock_client.on_message
        
        # Create mock message with JSON payload
        mock_message = MagicMock()
        mock_message.topic = "arkos/test/topic"
        mock_message.payload = json.dumps({"key": "value", "number": 42}).encode()
        
        # Call on_message
        on_message(mock_client, None, mock_message)
        
        # Check that message handler was called with parsed JSON
        message_handler.assert_called_once_with({"key": "value", "number": 42})

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_on_message_no_handler(self, mock_client_class):
        """Test on_message callback with no handler"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Get on_message callback
        on_message = mock_client.on_message
        
        # Create mock message
        mock_message = MagicMock()
        mock_message.topic = "arkos/test/topic"
        mock_message.payload = b"test message"
        
        # Call on_message
        on_message(mock_client, None, mock_message)
        
        # No assertion needed, just checking that it doesn't raise an exception

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_add_message_handler(self, mock_client_class):
        """Test adding a message handler"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and subscribe methods
        mock_client.connect.return_value = 0
        mock_client.subscribe.return_value = (0, 1)
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Add message handler
        handler = MagicMock()
        client.add_message_handler("test/topic", handler)
        
        # Check that handler was added and topic was subscribed
        assert client.message_handlers["test/topic"] == handler
        mock_client.subscribe.assert_called_once_with("arkos/test/topic")

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    def test_remove_message_handler(self, mock_client_class):
        """Test removing a message handler"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and unsubscribe methods
        mock_client.connect.return_value = 0
        mock_client.unsubscribe.return_value = (0, 1)
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Add message handler
        handler = MagicMock()
        client.message_handlers["test/topic"] = handler
        
        # Remove message handler
        client.remove_message_handler("test/topic")
        
        # Check that handler was removed and topic was unsubscribed
        assert "test/topic" not in client.message_handlers
        mock_client.unsubscribe.assert_called_once_with("arkos/test/topic")

    @patch("arkos.comms.mqtt_client.paho.mqtt.client.Client")
    @patch("arkos.comms.mqtt_client.time.time")
    def test_publish_stats(self, mock_time, mock_client_class):
        """Test publishing stats"""
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock connect and publish methods
        mock_client.connect.return_value = 0
        mock_client.publish.return_value.rc = 0
        
        # Mock time
        mock_time.return_value = 1000
        
        # Create client
        config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "topic_prefix": "arkos",
                "client_id": "arkos_test",
                "stats_interval": 60,
            }
        }
        
        client = MQTTClient(config)
        
        # Connect
        client.connect()
        
        # Publish stats
        stats = {
            "cpu": 10.5,
            "memory": 25.3,
            "disk": 50.0,
        }
        client.publish_stats(stats)
        
        # Check that stats were published
        mock_client.publish.assert_called_once_with(
            "arkos/stats", 
            json.dumps(stats), 
            0, 
            True
        )
        
        # Check last stats time
        assert client.last_stats_time == 1000
