"""
Pytest configuration and fixtures for Arkos AI testing.

This module provides common fixtures for testing Arkos AI components.
"""

import os
import time
import json
import shutil
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Generator, Tuple

import pytest
import docker
import numpy as np
import cv2
from unittest.mock import MagicMock, patch


# --- Path Fixtures --- #

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_videos_dir(fixtures_dir: Path) -> Path:
    """Return the sample videos directory."""
    return fixtures_dir / "sample_videos"


@pytest.fixture
def sample_audio_dir(fixtures_dir: Path) -> Path:
    """Return the sample audio directory."""
    return fixtures_dir / "sample_audio"


@pytest.fixture
def test_data_dir(fixtures_dir: Path) -> Path:
    """Return the test data directory."""
    return fixtures_dir / "test_data"


# --- Configuration Fixtures --- #

@pytest.fixture
def default_config() -> Dict[str, Any]:
    """Return a default configuration for testing."""
    return {
        "mqtt": {
            "host": "localhost",
            "port": 1883,
            "topic_prefix": "arkos",
            "client_id": "arkos-test",
            "user": None,
            "password": None,
        },
        "database": {
            "path": ":memory:",
        },
        "rtsp": {
            "host": "localhost",
            "port": 8554,
        },
        "cameras": {
            "test_camera": {
                "ffmpeg": {
                    "inputs": [
                        {
                            "path": "rtsp://localhost:8554/standard",
                            "roles": ["detect", "record"],
                        }
                    ],
                    "output_args": {
                        "detect": "-f rawvideo -pix_fmt yuv420p",
                        "record": "-f segment -segment_time 60 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy",
                    },
                },
                "detect": {
                    "enabled": True,
                    "width": 1280,
                    "height": 720,
                    "fps": 5,
                },
                "objects": {
                    "track": ["person", "car", "dog"],
                    "filters": {
                        "person": {
                            "min_area": 5000,
                            "max_area": 100000,
                            "threshold": 0.7,
                        },
                        "car": {
                            "min_area": 10000,
                            "max_area": 200000,
                            "threshold": 0.7,
                        },
                        "dog": {
                            "min_area": 3000,
                            "max_area": 50000,
                            "threshold": 0.7,
                        },
                    },
                },
                "zones": {
                    "yard": {
                        "coordinates": [[0, 0], [1280, 0], [1280, 720], [0, 720]],
                        "objects": ["person", "car", "dog"],
                    },
                },
                "snapshots": {
                    "enabled": True,
                    "retain": {
                        "default": 30,
                        "objects": {
                            "person": 60,
                        },
                    },
                },
                "record": {
                    "enabled": True,
                    "retain": {
                        "days": 30,
                        "mode": "all",
                    },
                },
            },
            "ptz_camera": {
                "ffmpeg": {
                    "inputs": [
                        {
                            "path": "rtsp://localhost:8554/ptz",
                            "roles": ["detect", "record"],
                        }
                    ],
                    "output_args": {
                        "detect": "-f rawvideo -pix_fmt yuv420p",
                        "record": "-f segment -segment_time 60 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy",
                    },
                },
                "detect": {
                    "enabled": True,
                    "width": 1280,
                    "height": 720,
                    "fps": 5,
                },
                "objects": {
                    "track": ["person", "car", "dog"],
                    "filters": {
                        "person": {
                            "min_area": 5000,
                            "max_area": 100000,
                            "threshold": 0.7,
                        },
                        "car": {
                            "min_area": 10000,
                            "max_area": 200000,
                            "threshold": 0.7,
                        },
                        "dog": {
                            "min_area": 3000,
                            "max_area": 50000,
                            "threshold": 0.7,
                        },
                    },
                },
                "ptz": {
                    "enabled": True,
                    "type": "onvif",
                    "host": "localhost",
                    "port": 8556,
                    "username": "admin",
                    "password": "admin",
                    "presets": {
                        "home": 1,
                        "driveway": 2,
                        "yard": 3,
                    },
                },
                "snapshots": {
                    "enabled": True,
                    "retain": {
                        "default": 30,
                        "objects": {
                            "person": 60,
                        },
                    },
                },
                "record": {
                    "enabled": True,
                    "retain": {
                        "days": 30,
                        "mode": "all",
                    },
                },
            },
            "audio_camera": {
                "ffmpeg": {
                    "inputs": [
                        {
                            "path": "rtsp://localhost:8554/audio",
                            "roles": ["detect", "record", "audio"],
                        }
                    ],
                    "output_args": {
                        "detect": "-f rawvideo -pix_fmt yuv420p",
                        "record": "-f segment -segment_time 60 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy",
                        "audio": "-f wav -ar 16000 -ac 1",
                    },
                },
                "detect": {
                    "enabled": True,
                    "width": 1280,
                    "height": 720,
                    "fps": 5,
                },
                "audio": {
                    "enabled": True,
                    "sample_rate": 16000,
                    "channels": 1,
                    "detect": {
                        "enabled": True,
                        "events": ["dog_bark", "glass_break", "car_alarm"],
                    },
                },
                "objects": {
                    "track": ["person", "car", "dog"],
                    "filters": {
                        "person": {
                            "min_area": 5000,
                            "max_area": 100000,
                            "threshold": 0.7,
                        },
                        "car": {
                            "min_area": 10000,
                            "max_area": 200000,
                            "threshold": 0.7,
                        },
                        "dog": {
                            "min_area": 3000,
                            "max_area": 50000,
                            "threshold": 0.7,
                        },
                    },
                },
                "snapshots": {
                    "enabled": True,
                    "retain": {
                        "default": 30,
                        "objects": {
                            "person": 60,
                        },
                    },
                },
                "record": {
                    "enabled": True,
                    "retain": {
                        "days": 30,
                        "mode": "all",
                    },
                },
            },
        },
        "detectors": {
            "cpu": {
                "type": "cpu",
                "model": {
                    "path": "models/yolov4-tiny.tflite",
                },
            },
        },
        "logger": {
            "level": "DEBUG",
        },
        "storage": {
            "path": "/tmp/arkos-test",
        },
    }


# --- Docker Fixtures --- #

@pytest.fixture
def docker_client() -> docker.DockerClient:
    """Return a Docker client."""
    return docker.from_env()


@pytest.fixture
def rtsp_simulator() -> Dict[str, str]:
    """Return RTSP simulator URLs."""
    return {
        "standard_url": "rtsp://localhost:8554/standard",
        "ptz_url": "rtsp://localhost:8554/ptz",
        "audio_url": "rtsp://localhost:8554/audio",
        "multi_object_url": "rtsp://localhost:8554/multi-object",
        "license_plate_url": "rtsp://localhost:8554/license-plate",
    }


# --- Mock Fixtures --- #

@pytest.fixture
def mock_detector() -> MagicMock:
    """Return a mock detector."""
    detector = MagicMock()
    detector.detect.return_value = [
        {
            "label": "person",
            "score": 0.95,
            "box": [150, 150, 100, 100],
            "area": 10000,
            "region": [100, 100, 200, 200],
        }
    ]
    return detector


@pytest.fixture
def mock_tracker() -> MagicMock:
    """Return a mock tracker."""
    tracker = MagicMock()
    tracker.track.return_value = [
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
    return tracker


@pytest.fixture
def mock_mqtt_client() -> MagicMock:
    """Return a mock MQTT client."""
    client = MagicMock()
    client.connect.return_value = None
    client.publish.return_value = None
    client.subscribe.return_value = None
    client.on_message = None
    return client


@pytest.fixture
def mqtt_client(mock_mqtt_client: MagicMock) -> MagicMock:
    """Return a mock MQTT client with patched paho.mqtt.client."""
    with patch("paho.mqtt.client.Client", return_value=mock_mqtt_client):
        yield mock_mqtt_client


# --- Sample Data Fixtures --- #

@pytest.fixture
def sample_frame() -> np.ndarray:
    """Return a sample video frame."""
    # Create a blank frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Add a person
    cv2.rectangle(frame, (150, 150), (250, 250), (0, 0, 255), -1)
    
    return frame


@pytest.fixture
def sample_detection_event() -> Dict[str, Any]:
    """Return a sample detection event."""
    return {
        "id": "event_1",
        "camera": "test_camera",
        "label": "person",
        "score": 0.95,
        "box": [150, 150, 100, 100],
        "area": 10000,
        "region": [100, 100, 200, 200],
        "current_zones": ["yard"],
        "thumbnail": "/path/to/thumbnail.jpg",
        "has_snapshot": True,
        "has_clip": False,
        "start_time": time.time(),
        "end_time": None,
    }


# --- Utility Fixtures --- #

@pytest.fixture
def wait_for_condition() -> Callable[[Callable[[], bool], int, float], bool]:
    """Return a function to wait for a condition to be true."""
    def _wait_for_condition(condition: Callable[[], bool], timeout: int = 10, interval: float = 0.1) -> bool:
        """Wait for a condition to be true."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False
    
    return _wait_for_condition
