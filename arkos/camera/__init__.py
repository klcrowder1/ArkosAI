import logging
import multiprocessing as mp
import threading
import time
from enum import Enum
from multiprocessing import Queue, Value
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class ConnectionStatus(str, Enum):
    """Camera connection status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DISABLED = "disabled"


class ConnectionError(str, Enum):
    """Camera connection error types."""

    NONE = "none"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    FFMPEG = "ffmpeg"
    UNKNOWN = "unknown"


class CameraMetrics:
    """Camera metrics for monitoring camera performance."""

    def __init__(self):
        self.camera_fps = Value("d", 0.0)
        self.skipped_fps = Value("d", 0.0)
        self.process_fps = Value("d", 0.0)
        self.detection_fps = Value("d", 0.0)
        self.detection_frame = Value("d", 0.0)
        self.ffmpeg_pid = Value("i", 0)
        self.frame_queue = mp.Queue(maxsize=2)
        self.process: Optional[mp.Process] = None
        self.capture_process: Optional[mp.Process] = None
        self.connection_status = Value("i", ConnectionStatus.DISCONNECTED.value)
        self.connection_error = Value("i", ConnectionError.NONE.value)
        self.last_connect_attempt = Value("d", 0.0)
        self.reconnect_count = Value("i", 0)
        self.uptime = Value("d", 0.0)
        self.last_frame_time = Value("d", 0.0)


class PTZMetrics:
    """PTZ metrics for monitoring PTZ operations."""

    def __init__(self, autotracker_enabled: bool = False):
        self.ptz_tracking_active = Value("i", 0)
        self.ptz_move_start_time = Value("d", 0.0)
        self.ptz_move_stop_time = Value("d", 0.0)
        self.ptz_move_count = Value("i", 0)
        self.ptz_error_count = Value("i", 0)
        self.ptz_last_error = Value("i", 0)
        self.ptz_last_error_time = Value("d", 0.0)
        self.ptz_last_move_time = Value("d", 0.0)
        self.ptz_last_move_duration = Value("d", 0.0)
        self.ptz_last_move_direction = Value("i", 0)
        self.ptz_last_move_speed = Value("d", 0.0)
        self.ptz_last_move_zoom = Value("d", 0.0)
        self.ptz_last_move_focus = Value("d", 0.0)
        self.ptz_last_move_iris = Value("d", 0.0)
        self.ptz_last_move_pan = Value("d", 0.0)
        self.ptz_last_move_tilt = Value("d", 0.0)
        self.ptz_last_move_preset = Value("i", 0)
        self.ptz_last_move_preset_name = Value("i", 0)
        self.ptz_last_move_preset_time = Value("d", 0.0)
        self.ptz_last_move_preset_duration = Value("d", 0.0)
        self.ptz_last_move_preset_count = Value("i", 0)
        self.ptz_last_move_preset_error = Value("i", 0)
        self.ptz_last_move_preset_error_time = Value("d", 0.0)
        self.ptz_last_move_preset_error_count = Value("i", 0)
        self.ptz_autotracker_enabled = Value("i", 1 if autotracker_enabled else 0)
        self.ptz_autotracker_active = Value("i", 0)
        self.ptz_autotracker_last_active_time = Value("d", 0.0)
        self.ptz_autotracker_last_active_duration = Value("d", 0.0)
        self.ptz_autotracker_last_active_count = Value("i", 0)
        self.ptz_autotracker_last_active_error = Value("i", 0)
        self.ptz_autotracker_last_active_error_time = Value("d", 0.0)
        self.ptz_autotracker_last_active_error_count = Value("i", 0)
        self.frame_time = Value("d", 0.0)
        self.start_time = Value("d", 0.0)
        self.stop_time = Value("d", 0.0)
