"""
Unit tests for video analytics in Arkos AI.

This module tests the video analytics functionality, including object detection and tracking.
"""

import time
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

# Import the modules to test
from arkos.object_detection.video_analytics import VideoAnalytics


class TestVideoAnalytics:
    """Test suite for video analytics."""

    @pytest.fixture
    def video_analytics(self, default_config, mock_detector, mock_tracker):
        """Create a video analytics object for testing."""
        camera_name = "test_camera"
        config = default_config["cameras"][camera_name]
        
        analytics = VideoAnalytics(
            camera_name=camera_name,
            config=config,
            detector=mock_detector,
            tracker=mock_tracker,
        )
        
        return analytics

    def test_process_frame(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame."""
        # Configure mock detector to return a detection
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
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 1, "Expected 1 detection"
        assert result[0]["label"] == "person", "Expected label to be 'person'"
        assert result[0]["id"] == "track_1", "Expected id to be 'track_1'"
        assert result[0]["score"] == 0.95, "Expected score to be 0.95"
        assert result[0]["box"] == [150, 150, 100, 100], "Expected box to be [150, 150, 100, 100]"
        assert result[0]["area"] == 10000, "Expected area to be 10000"
        assert result[0]["region"] == [100, 100, 200, 200], "Expected region to be [100, 100, 200, 200]"
        assert result[0]["stationary"] is False, "Expected stationary to be False"
        assert result[0]["motionless_count"] == 0, "Expected motionless_count to be 0"
        assert result[0]["position_changes"] == 5, "Expected position_changes to be 5"
        
        # Verify the detector was called
        mock_detector.detect.assert_called_once()
        
        # Verify the tracker was called
        mock_tracker.track.assert_called_once()

    def test_process_frame_no_detections(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with no detections."""
        # Configure mock detector to return no detections
        mock_detector.detect.return_value = []
        
        # Configure mock tracker to return no tracked objects
        mock_tracker.track.return_value = []
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 0, "Expected 0 detections"
        
        # Verify the detector was called
        mock_detector.detect.assert_called_once()
        
        # Verify the tracker was called
        mock_tracker.track.assert_called_once()

    def test_process_frame_multiple_detections(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with multiple detections."""
        # Configure mock detector to return multiple detections
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
        
        # Configure mock tracker to return multiple tracked objects
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
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 3, "Expected 3 detections"
        
        # Verify each detection
        labels = [detection["label"] for detection in result]
        assert "person" in labels, "Expected 'person' in labels"
        assert "car" in labels, "Expected 'car' in labels"
        assert "dog" in labels, "Expected 'dog' in labels"
        
        # Verify the detector was called
        mock_detector.detect.assert_called_once()
        
        # Verify the tracker was called
        mock_tracker.track.assert_called_once()

    def test_process_frame_with_zones(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with zones."""
        # Add zones to the video analytics
        video_analytics.zones = {
            "yard": {
                "coordinates": [[0, 0], [1280, 0], [1280, 720], [0, 720]],
                "objects": ["person", "car", "dog"],
            },
            "driveway": {
                "coordinates": [[100, 100], [300, 100], [300, 300], [100, 300]],
                "objects": ["car"],
            },
        }
        
        # Configure mock detector to return detections
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
        
        # Configure mock tracker to return tracked objects
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
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 2, "Expected 2 detections"
        
        # Verify zone information in detections
        for detection in result:
            assert "current_zones" in detection, "Expected 'current_zones' in detection"
            assert "yard" in detection["current_zones"], "Expected 'yard' in current_zones"
            
            if detection["label"] == "car":
                assert "driveway" in detection["current_zones"], "Expected 'driveway' in current_zones for car"
            elif detection["label"] == "person":
                assert "driveway" not in detection["current_zones"], "Expected 'driveway' not in current_zones for person"

    def test_process_frame_with_object_filtering(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with object filtering."""
        # Configure mock detector to return detections
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,  # Within filter range
                "region": [100, 100, 200, 200],
            },
            {
                "label": "person",
                "score": 0.95,
                "box": [350, 350, 50, 50],
                "area": 2500,  # Below min_area
                "region": [325, 325, 100, 100],
            },
            {
                "label": "person",
                "score": 0.95,
                "box": [500, 500, 400, 400],
                "area": 160000,  # Above max_area
                "region": [300, 300, 800, 800],
            },
            {
                "label": "person",
                "score": 0.6,  # Below threshold
                "box": [700, 700, 100, 100],
                "area": 10000,
                "region": [650, 650, 200, 200],
            }
        ]
        
        # Configure mock tracker to return tracked objects
        # The tracker should only receive the first detection (within filter range)
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
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 1, "Expected 1 detection after filtering"
        assert result[0]["label"] == "person", "Expected label to be 'person'"
        assert result[0]["area"] == 10000, "Expected area to be 10000"

    def test_process_frame_with_stationary_object(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with a stationary object."""
        # Configure mock detector to return a detection
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
            }
        ]
        
        # Configure mock tracker to return a stationary tracked object
        mock_tracker.track.return_value = [
            {
                "id": "track_1",
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],
                "area": 10000,
                "region": [100, 100, 200, 200],
                "stationary": True,
                "motionless_count": 10,
                "position_changes": 0,
            }
        ]
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 1, "Expected 1 detection"
        assert result[0]["stationary"] is True, "Expected stationary to be True"
        assert result[0]["motionless_count"] == 10, "Expected motionless_count to be 10"
        assert result[0]["position_changes"] == 0, "Expected position_changes to be 0"

    def test_process_frame_with_motion_detection(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with motion detection."""
        # Add motion detection to the video analytics
        video_analytics.motion_detector = MagicMock()
        video_analytics.motion_detector.detect_motion.return_value = (True, np.ones((720, 1280), dtype=np.uint8))
        
        # Configure mock detector to return a detection
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
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 1, "Expected 1 detection"
        
        # Verify motion detection was called
        video_analytics.motion_detector.detect_motion.assert_called_once()

    def test_process_frame_with_region_filtering(self, video_analytics, sample_frame, mock_detector, mock_tracker):
        """Test processing a frame with region filtering."""
        # Add regions to the video analytics
        video_analytics.regions = {
            "region1": {
                "coordinates": [[0, 0], [640, 0], [640, 720], [0, 720]],
                "objects": ["person", "car", "dog"],
            },
            "region2": {
                "coordinates": [[640, 0], [1280, 0], [1280, 720], [640, 720]],
                "objects": ["car"],
            },
        }
        
        # Configure mock detector to return detections
        mock_detector.detect.return_value = [
            {
                "label": "person",
                "score": 0.95,
                "box": [150, 150, 100, 100],  # In region1
                "area": 10000,
                "region": [100, 100, 200, 200],
            },
            {
                "label": "car",
                "score": 0.9,
                "box": [700, 200, 200, 100],  # In region2
                "area": 20000,
                "region": [600, 150, 400, 200],
            },
            {
                "label": "dog",
                "score": 0.85,
                "box": [800, 150, 80, 60],  # In region2, but not allowed
                "area": 4800,
                "region": [760, 120, 160, 120],
            }
        ]
        
        # Configure mock tracker to return tracked objects
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
                "box": [700, 200, 200, 100],
                "area": 20000,
                "region": [600, 150, 400, 200],
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 3,
            }
        ]
        
        # Process a frame
        result = video_analytics.process_frame(sample_frame, time.time())
        
        # Verify the result
        assert len(result) == 2, "Expected 2 detections after region filtering"
        
        # Verify region information in detections
        for detection in result:
            assert "current_regions" in detection, "Expected 'current_regions' in detection"
            
            if detection["label"] == "person":
                assert "region1" in detection["current_regions"], "Expected 'region1' in current_regions for person"
                assert "region2" not in detection["current_regions"], "Expected 'region2' not in current_regions for person"
            elif detection["label"] == "car":
                assert "region2" in detection["current_regions"], "Expected 'region2' in current_regions for car"
                assert "region1" not in detection["current_regions"], "Expected 'region1' not in current_regions for car"
        
        # Verify dog was filtered out
        labels = [detection["label"] for detection in result]
        assert "dog" not in labels, "Expected 'dog' to be filtered out"
