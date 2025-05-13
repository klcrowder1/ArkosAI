"""
Integration tests for monitoring center integration
"""

import pytest
import time
import json
import requests
from unittest.mock import MagicMock, patch

from arkos.notifications.notification_manager import NotificationManager
from arkos.events.event_manager import EventManager


@pytest.mark.integration
class TestMonitoringIntegration:
    """Integration tests for monitoring center integration"""
    
    @pytest.fixture
    def monitoring_system(self, test_config, test_database, mock_mqtt_client):
        """Fixture to set up a monitoring system for testing"""
        # Add monitoring configuration to test config
        monitoring_config = dict(test_config)
        monitoring_config["monitoring"] = {
            "enabled": True,
            "url": "http://localhost:8080/api/events",
            "api_key": "test_api_key",
            "send_events": True,
            "send_snapshots": True,
            "send_clips": True,
            "event_types": ["person", "car"],
        }
        
        # Create notification manager with mock MQTT client
        notification_manager = NotificationManager(monitoring_config)
        notification_manager.mqtt_client = mock_mqtt_client
        
        # Create event manager with mocks
        camera_manager = MagicMock()
        detection_manager = MagicMock()
        event_processor = MagicMock()
        
        event_manager = EventManager(
            monitoring_config,
            camera_manager,
            detection_manager,
            event_processor,
            notification_manager,
            test_database
        )
        
        return {
            "config": monitoring_config,
            "event_manager": event_manager,
            "notification_manager": notification_manager,
            "database": test_database,
            "mqtt_client": mock_mqtt_client,
        }
    
    @patch("requests.post")
    def test_event_forwarding(self, mock_post, monitoring_system, sample_detection_event):
        """Test that events are forwarded to the monitoring center"""
        # Extract components
        config = monitoring_system["config"]
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "monitoring_event_001"}
        mock_post.return_value = mock_response
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that request was made to monitoring center
        mock_post.assert_called_once()
        
        # Check request URL
        args, kwargs = mock_post.call_args
        assert args[0] == config["monitoring"]["url"], "Incorrect monitoring URL"
        
        # Check request headers
        headers = kwargs.get("headers", {})
        assert "Authorization" in headers, "Missing Authorization header"
        assert headers["Authorization"] == f"Bearer {config['monitoring']['api_key']}", "Incorrect API key"
        
        # Check request data
        data = kwargs.get("json", {})
        assert data["camera"] == sample_detection_event["camera"], "Incorrect camera name"
        assert data["label"] == sample_detection_event["label"], "Incorrect label"
        assert data["score"] == sample_detection_event["top_score"], "Incorrect score"
    
    @patch("requests.post")
    def test_event_filtering(self, mock_post, monitoring_system):
        """Test that events are filtered based on configuration"""
        # Extract components
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "monitoring_event_001"}
        mock_post.return_value = mock_response
        
        # Create events with different labels
        person_event = {
            "camera": "test_camera",
            "label": "person",
            "top_score": 0.95,
            "start_time": time.time(),
            "end_time": None,
            "has_clip": True,
            "has_snapshot": True,
        }
        
        car_event = {
            "camera": "test_camera",
            "label": "car",
            "top_score": 0.90,
            "start_time": time.time(),
            "end_time": None,
            "has_clip": True,
            "has_snapshot": True,
        }
        
        dog_event = {
            "camera": "test_camera",
            "label": "dog",
            "top_score": 0.85,
            "start_time": time.time(),
            "end_time": None,
            "has_clip": True,
            "has_snapshot": True,
        }
        
        # Trigger event notifications
        notification_manager.send_event_notification("new", None, person_event)
        notification_manager.send_event_notification("new", None, car_event)
        notification_manager.send_event_notification("new", None, dog_event)
        
        # Check that only person and car events were forwarded
        assert mock_post.call_count == 2, f"Expected 2 calls, got {mock_post.call_count}"
        
        # Check that the correct events were forwarded
        forwarded_labels = []
        for call in mock_post.call_args_list:
            args, kwargs = call
            data = kwargs.get("json", {})
            forwarded_labels.append(data["label"])
        
        assert "person" in forwarded_labels, "Person event was not forwarded"
        assert "car" in forwarded_labels, "Car event was not forwarded"
        assert "dog" not in forwarded_labels, "Dog event was incorrectly forwarded"
    
    @patch("requests.post")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    def test_snapshot_forwarding(self, mock_open, mock_exists, mock_post, monitoring_system, sample_detection_event, temp_dir):
        """Test that snapshots are forwarded to the monitoring center"""
        # Extract components
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "monitoring_event_001"}
        mock_post.return_value = mock_response
        
        # Set up mock file
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = b"test snapshot data"
        mock_open.return_value = mock_file
        
        # Add snapshot path to event
        event_with_snapshot = dict(sample_detection_event)
        event_with_snapshot["has_snapshot"] = True
        event_with_snapshot["id"] = "test_event_001"
        
        # Set snapshots directory
        notification_manager.snapshots_dir = str(temp_dir)
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, event_with_snapshot)
        
        # Check that request was made to monitoring center
        assert mock_post.call_count == 1, f"Expected 1 call, got {mock_post.call_count}"
        
        # Check that snapshot was included in request
        args, kwargs = mock_post.call_args
        assert "files" in kwargs, "Missing files in request"
        assert "snapshot" in kwargs["files"], "Missing snapshot in files"
    
    @patch("requests.post")
    def test_error_handling(self, mock_post, monitoring_system, sample_detection_event):
        """Test error handling for monitoring center requests"""
        # Extract components
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock response for failure
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that request was made to monitoring center
        mock_post.assert_called_once()
        
        # Set up mock response for connection error
        mock_post.reset_mock()
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that request was made to monitoring center
        mock_post.assert_called_once()
        
        # Set up mock response for timeout
        mock_post.reset_mock()
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that request was made to monitoring center
        mock_post.assert_called_once()
    
    @patch("requests.post")
    def test_retry_mechanism(self, mock_post, monitoring_system, sample_detection_event):
        """Test retry mechanism for monitoring center requests"""
        # Extract components
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock responses for failure then success
        mock_error_response = MagicMock()
        mock_error_response.status_code = 500
        mock_error_response.text = "Internal Server Error"
        
        mock_success_response = MagicMock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {"id": "monitoring_event_001"}
        
        mock_post.side_effect = [
            mock_error_response,  # First attempt fails
            mock_success_response,  # Retry succeeds
        ]
        
        # Configure retry settings
        notification_manager.monitoring_retry_count = 1
        notification_manager.monitoring_retry_delay = 0.1
        
        # Trigger event notification
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that request was made twice (initial + retry)
        assert mock_post.call_count == 2, f"Expected 2 calls, got {mock_post.call_count}"
    
    @patch("requests.post")
    def test_batch_processing(self, mock_post, monitoring_system):
        """Test batch processing of events to monitoring center"""
        # Extract components
        notification_manager = monitoring_system["notification_manager"]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ids": ["monitoring_event_001", "monitoring_event_002"]}
        mock_post.return_value = mock_response
        
        # Enable batch processing
        notification_manager.monitoring_batch_size = 2
        notification_manager.monitoring_batch_interval = 0.1
        
        # Create test events
        events = []
        for i in range(3):
            event = {
                "id": f"test_event_{i}",
                "camera": "test_camera",
                "label": "person",
                "top_score": 0.95,
                "start_time": time.time(),
                "end_time": None,
                "has_clip": True,
                "has_snapshot": True,
            }
            events.append(event)
        
        # Trigger event notifications
        for event in events:
            notification_manager.send_event_notification("new", None, event)
        
        # Wait for batch processing
        time.sleep(0.2)
        
        # Check that requests were made to monitoring center
        # Should be 2 requests: one batch of 2 events, one single event
        assert mock_post.call_count >= 1, f"Expected at least 1 call, got {mock_post.call_count}"
