"""
Unit tests for object tracking module
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from arkos.track.object_tracker import ObjectTracker
from arkos.track.tracking_manager import TrackingManager


class TestObjectTracker:
    """Tests for the ObjectTracker class"""

    def test_init(self):
        """Test initialization of ObjectTracker"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        assert tracker.max_disappeared == 30
        assert tracker.max_distance == 100
        assert tracker.min_confidence == 0.5
        assert tracker.deregister_frames == 30
        assert tracker.next_object_id == 0
        assert len(tracker.objects) == 0
        assert len(tracker.disappeared) == 0

    def test_register(self):
        """Test registering a new object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register a new object
        centroid = (100, 200)
        object_id = tracker.register(centroid)
        
        # Check that object was registered
        assert object_id == 0
        assert tracker.next_object_id == 1
        assert len(tracker.objects) == 1
        assert len(tracker.disappeared) == 1
        assert tracker.objects[0] == centroid
        assert tracker.disappeared[0] == 0

    def test_deregister(self):
        """Test deregistering an object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register objects
        centroid1 = (100, 200)
        centroid2 = (300, 400)
        object_id1 = tracker.register(centroid1)
        object_id2 = tracker.register(centroid2)
        
        # Deregister an object
        tracker.deregister(object_id1)
        
        # Check that object was deregistered
        assert object_id1 not in tracker.objects
        assert object_id1 not in tracker.disappeared
        assert object_id2 in tracker.objects
        assert object_id2 in tracker.disappeared

    def test_update_with_new_object(self):
        """Test updating with a new object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Update with a new object
        centroids = [(100, 200)]
        objects = tracker.update(centroids)
        
        # Check that object was registered
        assert len(objects) == 1
        assert objects[0] == 0  # First object ID
        assert tracker.next_object_id == 1
        assert len(tracker.objects) == 1
        assert len(tracker.disappeared) == 1
        assert tracker.objects[0] == centroids[0]
        assert tracker.disappeared[0] == 0

    def test_update_with_existing_object(self):
        """Test updating with an existing object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register an object
        centroid1 = (100, 200)
        object_id = tracker.register(centroid1)
        
        # Update with a slightly moved object
        centroid2 = (110, 210)  # Moved slightly
        objects = tracker.update([centroid2])
        
        # Check that object was updated
        assert len(objects) == 1
        assert objects[0] == object_id
        assert tracker.objects[object_id] == centroid2
        assert tracker.disappeared[object_id] == 0

    def test_update_with_disappeared_object(self):
        """Test updating with a disappeared object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register an object
        centroid = (100, 200)
        object_id = tracker.register(centroid)
        
        # Update with no objects
        objects = tracker.update([])
        
        # Check that object was marked as disappeared
        assert len(objects) == 0
        assert tracker.disappeared[object_id] == 1
        
        # Update again with no objects
        objects = tracker.update([])
        
        # Check that object was marked as disappeared again
        assert len(objects) == 0
        assert tracker.disappeared[object_id] == 2

    def test_update_with_reappeared_object(self):
        """Test updating with a reappeared object"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register an object
        centroid1 = (100, 200)
        object_id = tracker.register(centroid1)
        
        # Update with no objects
        tracker.update([])
        
        # Update with the object reappearing
        centroid2 = (110, 210)  # Moved slightly
        objects = tracker.update([centroid2])
        
        # Check that object was updated
        assert len(objects) == 1
        assert objects[0] == object_id
        assert tracker.objects[object_id] == centroid2
        assert tracker.disappeared[object_id] == 0

    def test_update_with_max_disappeared(self):
        """Test updating with max disappeared frames"""
        config = {
            "max_disappeared": 2,  # Set to a small value for testing
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Register an object
        centroid = (100, 200)
        object_id = tracker.register(centroid)
        
        # Update with no objects twice
        tracker.update([])
        objects = tracker.update([])
        
        # Check that object was deregistered
        assert len(objects) == 0
        assert object_id not in tracker.objects
        assert object_id not in tracker.disappeared

    def test_calculate_centroids(self):
        """Test calculating centroids from bounding boxes"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Create bounding boxes
        boxes = [
            [100, 200, 50, 60],  # x, y, w, h
            [300, 400, 70, 80],
        ]
        
        # Calculate centroids
        centroids = tracker.calculate_centroids(boxes)
        
        # Check centroids
        assert len(centroids) == 2
        assert centroids[0] == (125, 230)  # x + w/2, y + h/2
        assert centroids[1] == (335, 440)

    def test_calculate_distances(self):
        """Test calculating distances between centroids"""
        config = {
            "max_disappeared": 30,
            "max_distance": 100,
            "min_confidence": 0.5,
            "deregister_frames": 30,
        }
        
        tracker = ObjectTracker(config)
        
        # Create centroids
        old_centroids = {
            0: (100, 200),
            1: (300, 400),
        }
        new_centroids = [
            (110, 210),  # Close to old centroid 0
            (500, 600),  # Far from both old centroids
        ]
        
        # Calculate distances
        D = tracker.calculate_distances(old_centroids, new_centroids)
        
        # Check distances
        assert D.shape == (2, 2)  # 2 old centroids, 2 new centroids
        assert D[0, 0] < D[0, 1]  # First new centroid is closer to first old centroid
        assert D[1, 0] > D[1, 1]  # Second new centroid is closer to second old centroid


class TestTrackingManager:
    """Tests for the TrackingManager class"""

    def test_init(self):
        """Test initialization of TrackingManager"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        assert manager.trackers == {}
        assert manager.config["max_disappeared"] == 30
        assert manager.config["max_distance"] == 100
        assert manager.config["min_confidence"] == 0.5
        assert manager.config["deregister_frames"] == 30

    def test_get_tracker(self):
        """Test getting a tracker for a camera"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        # Get tracker for a camera
        tracker = manager.get_tracker("test_camera")
        
        # Check that tracker was created
        assert "test_camera" in manager.trackers
        assert tracker is not None
        assert tracker.max_disappeared == 30
        assert tracker.max_distance == 100
        assert tracker.min_confidence == 0.5
        assert tracker.deregister_frames == 30

    def test_get_existing_tracker(self):
        """Test getting an existing tracker for a camera"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        # Get tracker for a camera
        tracker1 = manager.get_tracker("test_camera")
        
        # Get tracker again
        tracker2 = manager.get_tracker("test_camera")
        
        # Check that the same tracker was returned
        assert tracker1 is tracker2

    def test_track_objects(self):
        """Test tracking objects"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        # Create mock tracker
        mock_tracker = MagicMock()
        mock_tracker.calculate_centroids.return_value = [(125, 230), (335, 440)]
        mock_tracker.update.return_value = [0, 1]
        manager.trackers["test_camera"] = mock_tracker
        
        # Create detections
        detections = [
            {
                "label": "person",
                "confidence": 0.9,
                "box": [100, 200, 50, 60],  # x, y, w, h
            },
            {
                "label": "car",
                "confidence": 0.8,
                "box": [300, 400, 70, 80],
            },
        ]
        
        # Track objects
        tracked_objects = manager.track_objects("test_camera", detections)
        
        # Check that tracker was called
        mock_tracker.calculate_centroids.assert_called_once()
        mock_tracker.update.assert_called_once()
        
        # Check tracked objects
        assert len(tracked_objects) == 2
        assert tracked_objects[0]["id"] == 0
        assert tracked_objects[0]["label"] == "person"
        assert tracked_objects[0]["confidence"] == 0.9
        assert tracked_objects[0]["box"] == [100, 200, 50, 60]
        assert tracked_objects[0]["centroid"] == (125, 230)
        assert tracked_objects[1]["id"] == 1
        assert tracked_objects[1]["label"] == "car"
        assert tracked_objects[1]["confidence"] == 0.8
        assert tracked_objects[1]["box"] == [300, 400, 70, 80]
        assert tracked_objects[1]["centroid"] == (335, 440)

    def test_track_objects_with_confidence_filtering(self):
        """Test tracking objects with confidence filtering"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.85,  # Set high to filter out second detection
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        # Create mock tracker
        mock_tracker = MagicMock()
        mock_tracker.calculate_centroids.return_value = [(125, 230)]
        mock_tracker.update.return_value = [0]
        manager.trackers["test_camera"] = mock_tracker
        
        # Create detections
        detections = [
            {
                "label": "person",
                "confidence": 0.9,
                "box": [100, 200, 50, 60],  # x, y, w, h
            },
            {
                "label": "car",
                "confidence": 0.8,  # Below min_confidence
                "box": [300, 400, 70, 80],
            },
        ]
        
        # Track objects
        tracked_objects = manager.track_objects("test_camera", detections)
        
        # Check that tracker was called with only one detection
        assert len(mock_tracker.calculate_centroids.call_args[0][0]) == 1
        
        # Check tracked objects
        assert len(tracked_objects) == 1
        assert tracked_objects[0]["id"] == 0
        assert tracked_objects[0]["label"] == "person"
        assert tracked_objects[0]["confidence"] == 0.9

    def test_track_objects_with_no_detections(self):
        """Test tracking objects with no detections"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
            }
        }
        
        manager = TrackingManager(config)
        
        # Create mock tracker
        mock_tracker = MagicMock()
        mock_tracker.calculate_centroids.return_value = []
        mock_tracker.update.return_value = []
        manager.trackers["test_camera"] = mock_tracker
        
        # Track objects with no detections
        tracked_objects = manager.track_objects("test_camera", [])
        
        # Check that tracker was called
        mock_tracker.calculate_centroids.assert_called_once_with([])
        mock_tracker.update.assert_called_once_with([])
        
        # Check tracked objects
        assert len(tracked_objects) == 0

    def test_track_objects_with_camera_specific_config(self):
        """Test tracking objects with camera-specific configuration"""
        config = {
            "tracking": {
                "max_disappeared": 30,
                "max_distance": 100,
                "min_confidence": 0.5,
                "deregister_frames": 30,
                "camera_config": {
                    "test_camera": {
                        "min_confidence": 0.7,  # Override for test_camera
                    }
                }
            }
        }
        
        manager = TrackingManager(config)
        
        # Get tracker for camera
        tracker = manager.get_tracker("test_camera")
        
        # Check that camera-specific config was applied
        assert tracker.min_confidence == 0.7
