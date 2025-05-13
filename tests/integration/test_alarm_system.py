"""
Integration tests for the alarm system
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from arkos.events.event_manager import EventManager
from arkos.notifications.notification_manager import NotificationManager


@pytest.mark.integration
class TestAlarmSystem:
    """Integration tests for the alarm system"""
    
    @pytest.fixture
    def alarm_system(self, test_config, test_database, mock_mqtt_client):
        """Fixture to set up an alarm system for testing"""
        # Create notification manager with mock MQTT client
        notification_manager = NotificationManager(test_config)
        notification_manager.mqtt_client = mock_mqtt_client
        
        # Create event manager with mocks
        camera_manager = MagicMock()
        detection_manager = MagicMock()
        event_processor = MagicMock()
        
        event_manager = EventManager(
            test_config,
            camera_manager,
            detection_manager,
            event_processor,
            notification_manager,
            test_database
        )
        
        return {
            "event_manager": event_manager,
            "notification_manager": notification_manager,
            "database": test_database,
            "mqtt_client": mock_mqtt_client,
        }
    
    def test_alarm_trigger(self, alarm_system, sample_detection_event):
        """Test that alarms are triggered correctly"""
        # Extract components
        event_manager = alarm_system["event_manager"]
        notification_manager = alarm_system["notification_manager"]
        database = alarm_system["database"]
        mqtt_client = alarm_system["mqtt_client"]
        
        # Insert test event
        event_id = database.insert_event(sample_detection_event)
        
        # Trigger alarm
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that notification was sent
        mqtt_messages = mqtt_client.get_messages()
        assert len(mqtt_messages) > 0, "No MQTT messages were sent"
        
        # Find alarm message
        alarm_messages = [m for m in mqtt_messages if "events" in m["topic"]]
        assert len(alarm_messages) > 0, "No alarm messages were sent"
    
    def test_alarm_zones(self, alarm_system, sample_detection_event):
        """Test that alarms respect zone configurations"""
        # Extract components
        notification_manager = alarm_system["notification_manager"]
        mqtt_client = alarm_system["mqtt_client"]
        
        # Create events in different zones
        zone_event = dict(sample_detection_event)
        zone_event["current_zones"] = ["yard"]
        zone_event["entered_zones"] = ["yard"]
        
        no_zone_event = dict(sample_detection_event)
        no_zone_event["current_zones"] = []
        no_zone_event["entered_zones"] = []
        
        # Trigger alarms
        notification_manager.send_event_notification("new", None, zone_event)
        notification_manager.send_event_notification("new", None, no_zone_event)
        
        # Check that notifications were sent
        mqtt_messages = mqtt_client.get_messages()
        assert len(mqtt_messages) >= 2, "Not enough MQTT messages were sent"
    
    def test_alarm_cooldown(self, alarm_system, sample_detection_event):
        """Test that alarms respect cooldown periods"""
        # Extract components
        notification_manager = alarm_system["notification_manager"]
        mqtt_client = alarm_system["mqtt_client"]
        
        # Set cooldown period
        notification_manager.cooldown_period = 5  # seconds
        
        # Trigger first alarm
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that notification was sent
        mqtt_messages = mqtt_client.get_messages()
        assert len(mqtt_messages) > 0, "No MQTT messages were sent"
        
        # Clear messages
        mqtt_client.messages = []
        
        # Trigger second alarm immediately (should be ignored due to cooldown)
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that no new notification was sent
        assert len(mqtt_client.messages) == 0, "Notification was sent during cooldown period"
        
        # Wait for cooldown to expire
        time.sleep(6)
        
        # Trigger third alarm (should be sent)
        notification_manager.send_event_notification("new", None, sample_detection_event)
        
        # Check that notification was sent
        assert len(mqtt_client.messages) > 0, "No MQTT messages were sent after cooldown"
