"""
End-to-end tests for event flow in Arkos AI.

This module tests the complete event flow from detection to alarm in Arkos AI.
"""

import os
import time
import json
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

# Import the modules to test
from arkos.camera.rtsp_stream import RTSPStream
from arkos.camera.camera import Camera
from arkos.object_detection.video_analytics import VideoAnalytics
from arkos.events.event_processor import EventProcessor
from arkos.events.event_manager import EventManager
from arkos.notifications.notification_manager import NotificationManager
from arkos.db.database import Database


class TestEventFlow:
    """Test suite for end-to-end event flow."""

    @pytest.fixture
    def event_flow_setup(self, rtsp_simulator, default_config, mock_detector, mock_tracker, temp_dir, mqtt_client):
        """Set up the complete event flow for testing."""
        # Create a database
        db_path = temp_dir / "test.db"
        database = Database(str(db_path))
        
        # Create a camera
        camera_name = "test_camera"
        camera_config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["standard_url"],
            config=camera_config,
        )
        
        camera = Camera(
            name=camera_name,
            config=camera_config,
            stream=stream,
        )
        
        # Create video analytics
        analytics = VideoAnalytics(
            camera_name=camera_name,
            config=camera_config,
            detector=mock_detector,
            tracker=mock_tracker,
        )
        
        # Create event processor
        event_processor = EventProcessor(
            camera_name=camera_name,
            config=camera_config,
            database=database,
        )
        
        # Create event manager
        event_manager = EventManager(
            config=default_config,
            database=database,
        )
        
        # Create notification manager
        notification_manager = NotificationManager(
            config=default_config,
            database=database,
            mqtt_client=mqtt_client,
        )
        
        # Connect event manager to notification manager
        event_manager.add_listener(notification_manager.on_event)
        
        # Start the camera
        camera.start()
        
        # Wait for the camera to connect
        for _ in range(10):
            if camera.is_connected():
                break
            time.sleep(0.5)
        
        assert camera.is_connected(), "Camera failed to connect"
        
        # Return the setup
        yield {
            "camera": camera,
            "analytics": analytics,
            "event_processor": event_processor,
            "event_manager": event_manager,
            "notification_manager": notification_manager,
            "database": database,
        }
        
        # Clean up
        camera.stop()
        database.close()

    def test_complete_event_flow(self, event_flow_setup, sample_frame, sample_detection_event, wait_for_condition):
        """Test the complete event flow from detection to notification."""
        # Get components from setup
        camera = event_flow_setup["camera"]
        analytics = event_flow_setup["analytics"]
        event_processor = event_flow_setup["event_processor"]
        event_manager = event_flow_setup["event_manager"]
        notification_manager = event_flow_setup["notification_manager"]
        database = event_flow_setup["database"]
        
        # Set up notification tracking
        notifications_received = []
        
        def notification_listener(event):
            notifications_received.append(event)
        
        notification_manager.add_listener(notification_listener)
        
        # Configure mock detector to return a detection
        mock_detector = analytics._detector
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
            }
        ]
        
        # Configure mock tracker to return a tracked object
        mock_tracker = analytics._tracker
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            }
        ]
        
        # Process a frame through the complete flow
        frame = camera.get_frame()
        assert frame is not None, "Failed to get frame from camera"
        
        # Step 1: Process frame with video analytics
        detections = analytics.process_frame(frame, time.time())
        assert len(detections) == 1, "Expected 1 detection"
        assert detections[0]["label"] == "person"
        
        # Step 2: Process detections with event processor
        events = []
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                events.append(event)
        
        assert len(events) == 1, "Expected 1 event"
        assert events[0]["label"] == "person"
        
        # Step 3: Send events to event manager
        for event in events:
            event_manager.process_event(event)
        
        # Step 4: Wait for notification to be sent
        def notification_sent():
            return len(notifications_received) > 0
        
        assert wait_for_condition(notification_sent, timeout=5), "Notification not sent within timeout"
        
        # Verify notification
        assert len(notifications_received) == 1, "Expected 1 notification"
        assert notifications_received[0]["label"] == "person"
        
        # Verify event was stored in database
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 1, "Expected 1 event in database"
        assert stored_events[0]["label"] == "person"

    def test_event_lifecycle(self, event_flow_setup, sample_frame, wait_for_condition):
        """Test the complete lifecycle of an event from creation to end."""
        # Get components from setup
        camera = event_flow_setup["camera"]
        analytics = event_flow_setup["analytics"]
        event_processor = event_flow_setup["event_processor"]
        event_manager = event_flow_setup["event_manager"]
        database = event_flow_setup["database"]
        
        # Configure mock detector and tracker for event creation
        mock_detector = analytics._detector
        mock_tracker = analytics._tracker
        
        # Configure for initial detection
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
            }
        ]
        
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            }
        ]
        
        # Process initial frame to create event
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time())
        
        events = []
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                events.append(event)
                event_manager.process_event(event)
        
        assert len(events) == 1, "Expected 1 event"
        event_id = events[0]["id"]
        
        # Verify event was created in database
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 1, "Expected 1 event in database"
        assert stored_events[0]["id"] == event_id
        assert stored_events[0]["end_time"] is None, "Event should not have ended yet"
        
        # Configure for continued tracking
        for i in range(5):
            mock_tracker.track.return_value = [
                {
                    "id": "track_1",
                    "label": "person",
                    "score": 0.95,
                    "box": [150 + i*10, 150 + i*10, 100, 100],  # Moving object
                    "area": 10000,
                    "region": [100 + i*10, 100 + i*10, 200, 200],
                    "stationary": False,
                    "motionless_count": 0,
                    "position_changes": 5 + i,
                }
            ]
            
            # Process frame with moving object
            frame = camera.get_frame()
            detections = analytics.process_frame(frame, time.time() + i)
            
            for detection in detections:
                event = event_processor.process(detection, frame)
                if event:
                    event_manager.process_event(event)
        
        # Verify event is still active
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 1, "Expected 1 event in database"
        assert stored_events[0]["id"] == event_id
        assert stored_events[0]["end_time"] is None, "Event should not have ended yet"
        
        # Configure for object disappearance
        mock_tracker.track.return_value = []
        
        # Process frame with no objects
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time() + 10)
        assert len(detections) == 0, "Expected no detections"
        
        # Process empty detections to end event
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                event_manager.process_event(event)
        
        # Process a frame with no detections to trigger event end
        event_processor.process_empty_frame(time.time() + 10)
        
        # Wait for event to be marked as ended
        def event_ended():
            events = database.get_events(limit=10)
            return events[0]["end_time"] is not None
        
        assert wait_for_condition(event_ended, timeout=5), "Event not ended within timeout"
        
        # Verify event was ended in database
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 1, "Expected 1 event in database"
        assert stored_events[0]["id"] == event_id
        assert stored_events[0]["end_time"] is not None, "Event should have ended"

    def test_multiple_object_tracking(self, event_flow_setup, sample_frame, wait_for_condition):
        """Test tracking and event generation for multiple objects."""
        # Get components from setup
        camera = event_flow_setup["camera"]
        analytics = event_flow_setup["analytics"]
        event_processor = event_flow_setup["event_processor"]
        event_manager = event_flow_setup["event_manager"]
        database = event_flow_setup["database"]
        
        # Configure mock detector and tracker for multiple objects
        mock_detector = analytics._detector
        mock_tracker = analytics._tracker
        
        # Configure for multiple detections
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
            },
            {
                "label": "car",
                "score": 0.9,
                "box": [300, 300, 200, 100],
                "area": 20000,
                "region": [250, 250, 300, 200],
            },
            {
                "label": "dog",
                "score": 0.85,
                "box": [500, 150, 80, 60],
                "area": 4800,
                "region": [460, 120, 160, 120],
            }
        ]
        
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            },
            {
                "id": "track_2",
                "label": "car",
                "score": 0.9,
                "box": [300, 300, 200, 100],
                "area": 20000,
                "region": [250, 250, 300, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 3,
            },
            {
                "id": "track_3",
                "label": "dog",
                "score": 0.85,
                "box": [500, 150, 80, 60],
                "area": 4800,
                "region": [460, 120, 160, 120],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 7,
            }
        ]
        
        # Process frame with multiple objects
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time())
        
        assert len(detections) == 3, "Expected 3 detections"
        
        # Process detections to create events
        events = []
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                events.append(event)
                event_manager.process_event(event)
        
        assert len(events) == 3, "Expected 3 events"
        
        # Verify events were created in database
        def events_created():
            stored_events = database.get_events(limit=10)
            return len(stored_events) == 3
        
        assert wait_for_condition(events_created, timeout=5), "Events not created within timeout"
        
        # Verify event details
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 3, "Expected 3 events in database"
        
        labels = [event["label"] for event in stored_events]
        assert "person" in labels, "Expected person event"
        assert "car" in labels, "Expected car event"
        assert "dog" in labels, "Expected dog event"
        
        # Configure for some objects disappearing
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [160, 160, 100, 100],
                "area": 10000,
                "region": [110, 110, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 6,
            },
            # Car is gone
            {
                "id": "track_3",
                "label": "dog",
                "score": 0.85,
                "box": [510, 160, 80, 60],
                "area": 4800,
                "region": [470, 130, 160, 120],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 8,
            }
        ]
        
        # Process frame with some objects missing
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time() + 5)
        
        assert len(detections) == 2, "Expected 2 detections"
        
        # Process detections to update events
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                event_manager.process_event(event)
        
        # Process a frame with missing detections to trigger event end for the car
        event_processor.process_empty_frame(time.time() + 5)
        
        # Wait for car event to be marked as ended
        def car_event_ended():
            events = database.get_events(limit=10)
            for event in events:
                if event["label"] == "car":
                    return event["end_time"] is not None
            return False
        
        assert wait_for_condition(car_event_ended, timeout=5), "Car event not ended within timeout"
        
        # Verify car event was ended but others are still active
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 3, "Expected 3 events in database"
        
        for event in stored_events:
            if event["label"] == "car":
                assert event["end_time"] is not None, "Car event should have ended"
            else:
                assert event["end_time"] is None, f"{event['label']} event should not have ended yet"

    def test_event_with_zones(self, event_flow_setup, sample_frame, wait_for_condition):
        """Test event generation with zone detection."""
        # Get components from setup
        camera = event_flow_setup["camera"]
        analytics = event_flow_setup["analytics"]
        event_processor = event_flow_setup["event_processor"]
        event_manager = event_flow_setup["event_manager"]
        database = event_flow_setup["database"]
        
        # Add zones to analytics
        analytics.zones = {
            "yard": {
                "coordinates": [[0, 0], [640, 0], [640, 480], [0, 480]],
                "objects": ["person", "car", "dog"],
            },
            "driveway": {
                "coordinates": [[100, 100], [300, 100], [300, 300], [100, 300]],
                "objects": ["car"],
            },
        }
        
        # Configure mock detector and tracker
        mock_detector = analytics._detector
        mock_tracker = analytics._tracker
        
        # Configure for detection in zones
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],  # In yard and driveway
                "area": 10000,
                "region": [100, 100, 200, 200],
            },
            {
                "label": "car",
                "score": 0.9,
                "box": [200, 200, 200, 100],  # In yard and driveway
                "area": 20000,
                "region": [150, 150, 300, 200],
            }
        ]
        
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            },
            {
                "id": "track_2",
                "label": "car",
                "score": 0.9,
                "box": [200, 200, 200, 100],
                "area": 20000,
                "region": [150, 150, 300, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 3,
            }
        ]
        
        # Process frame with objects in zones
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time())
        
        assert len(detections) == 2, "Expected 2 detections"
        
        # Check zone information in detections
        for detection in detections:
            assert "current_zones" in detection, "Detection should have zone information"
            assert "yard" in detection["current_zones"], "Detection should be in yard zone"
            
            if detection["label"] == "car":
                assert "driveway" in detection["current_zones"], "Car should be in driveway zone"
        
        # Process detections to create events
        events = []
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                events.append(event)
                event_manager.process_event(event)
        
        assert len(events) == 2, "Expected 2 events"
        
        # Verify events were created in database with zone information
        def events_created():
            stored_events = database.get_events(limit=10)
            return len(stored_events) == 2
        
        assert wait_for_condition(events_created, timeout=5), "Events not created within timeout"
        
        # Verify event details
        stored_events = database.get_events(limit=10)
        assert len(stored_events) == 2, "Expected 2 events in database"
        
        for event in stored_events:
            assert "current_zones" in event, "Event should have zone information"
            assert "yard" in event["current_zones"], "Event should be in yard zone"
            
            if event["label"] == "car":
                assert "driveway" in event["current_zones"], "Car event should be in driveway zone"
            elif event["label"] == "person":
                assert "driveway" not in event["current_zones"], "Person event should not be in driveway zone"

    def test_event_with_snapshot_and_clip(self, event_flow_setup, sample_frame, wait_for_condition, temp_dir):
        """Test event generation with snapshot and clip creation."""
        # Get components from setup
        camera = event_flow_setup["camera"]
        analytics = event_flow_setup["analytics"]
        event_processor = event_flow_setup["event_processor"]
        event_manager = event_flow_setup["event_manager"]
        database = event_flow_setup["database"]
        
        # Configure event processor for snapshot and clip creation
        event_processor.snapshot_dir = temp_dir / "snapshots"
        event_processor.snapshot_dir.mkdir(exist_ok=True)
        
        event_processor.clip_dir = temp_dir / "clips"
        event_processor.clip_dir.mkdir(exist_ok=True)
        
        # Configure mock detector and tracker
        mock_detector = analytics._detector
        mock_tracker = analytics._tracker
        
        # Configure for detection
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
            }
        ]
        
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            }
        ]
        
        # Process frame to create event
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time())
        
        assert len(detections) == 1, "Expected 1 detection"
        
        # Process detection to create event with snapshot
        events = []
        for detection in detections:
            event = event_processor.process(detection, frame)
            if event:
                events.append(event)
                event_manager.process_event(event)
        
        assert len(events) == 1, "Expected 1 event"
        event_id = events[0]["id"]
        
        # Verify event was created with snapshot
        assert events[0]["has_snapshot"] is True, "Event should have snapshot"
        
        # Verify snapshot file was created
        snapshot_path = event_processor.snapshot_dir / f"{event_id}.jpg"
        assert snapshot_path.exists(), "Snapshot file should exist"
        
        # Process more frames to create clip
        for i in range(5):
            frame = camera.get_frame()
            detections = analytics.process_frame(frame, time.time() + i)
            
            for detection in detections:
                event = event_processor.process(detection, frame)
                if event:
                    event_manager.process_event(event)
        
        # End the event
        mock_tracker.track.return_value = []
        frame = camera.get_frame()
        detections = analytics.process_frame(frame, time.time() + 10)
        event_processor.process_empty_frame(time.time() + 10)
        
        # Wait for event to be marked as ended and clip to be created
        def event_ended_with_clip():
            events = database.get_events(limit=10)
            return events[0]["end_time"] is not None and events[0]["has_clip"] is True
        
        assert wait_for_condition(event_ended_with_clip, timeout=10), "Event not ended with clip within timeout"
        
        # Verify clip file was created
        clip_path = event_processor.clip_dir / f"{event_id}.mp4"
        assert clip_path.exists(), "Clip file should exist"
