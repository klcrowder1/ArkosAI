# Camera Integration Refactoring Plan

This document outlines the plan for refactoring the camera integration code in the Arkos AI project. The goal is to improve the code organization, maintainability, and extensibility while maintaining compatibility with the rest of the system.

## Current Architecture

The current camera integration code is spread across several files:

- `frigate/camera/__init__.py`: Defines the `CameraMetrics` and `PTZMetrics` classes for tracking camera performance metrics
- `frigate/camera/activity_manager.py`: Manages camera activity and updates listeners
- `frigate/camera/state.py`: Maintains the state of the camera, including tracked objects and frames
- `frigate/video.py`: Contains the main camera capture and processing logic

The main application (`app.py`) initializes the camera metrics and starts the camera capture and processing threads.

## Issues with Current Implementation

1. **Tight Coupling**: The camera code is tightly coupled with other components, making it difficult to extend or modify.
2. **Code Organization**: Functionality is spread across multiple files without a clear separation of concerns.
3. **Error Handling**: Error handling is inconsistent and often relies on logging rather than proper exception handling.
4. **Type Hints**: Type hints are used inconsistently, making it harder to understand the code.
5. **Testability**: The current code is difficult to test due to its tight coupling and reliance on global state.
6. **Configuration Management**: Camera configuration is passed around as parameters rather than being encapsulated in a proper class.
7. **Process Management**: The process management code is complex and difficult to understand.

## Refactoring Goals

1. **Improve Code Organization**: Reorganize the camera code into a more logical structure with clear separation of concerns.
2. **Reduce Coupling**: Reduce coupling between the camera code and other components.
3. **Improve Error Handling**: Implement consistent error handling throughout the camera code.
4. **Add Type Hints**: Add comprehensive type hints to improve code readability and maintainability.
5. **Improve Testability**: Make the code more testable by reducing dependencies and using dependency injection.
6. **Encapsulate Configuration**: Encapsulate camera configuration in a proper class.
7. **Simplify Process Management**: Simplify the process management code.

## Proposed Architecture

The proposed architecture organizes the camera code into a more logical structure with clear separation of concerns and renames the module from "frigate" to "arkos":

```
arkos/
└── camera/
    ├── __init__.py                # Public API
    ├── metrics.py                 # Camera metrics classes
    ├── capture.py                 # Camera capture logic
    ├── processing.py              # Frame processing logic
    ├── state.py                   # Camera state management
    ├── activity.py                # Camera activity management
    ├── watchdog.py                # Camera watchdog
    └── manager.py                 # Camera manager
```

### Component Responsibilities

1. **metrics.py**: Contains the `CameraMetrics` and `PTZMetrics` classes for tracking camera performance metrics.
2. **capture.py**: Contains the camera capture logic, including the `CameraCapture` class and related functions.
3. **processing.py**: Contains the frame processing logic, including object detection and tracking.
4. **state.py**: Contains the camera state management logic, including the `CameraState` class.
5. **activity.py**: Contains the camera activity management logic, including the `CameraActivityManager` class.
6. **watchdog.py**: Contains the camera watchdog logic, including the `CameraWatchdog` class.
7. **manager.py**: Contains the camera manager logic, which coordinates the other components.

## Implementation Plan

The refactoring will be implemented in several phases:

### Phase 1: Code Reorganization

1. Create the new file structure
2. Move existing code to the appropriate files
3. Update imports to reflect the new structure
4. Ensure the code still works with minimal changes

### Phase 2: Improve Code Quality

1. Add comprehensive type hints
2. Improve error handling
3. Refactor complex functions into smaller, more focused functions
4. Remove duplicated code

### Phase 3: Reduce Coupling

1. Introduce interfaces for dependencies
2. Use dependency injection to reduce coupling
3. Replace global state with proper class attributes

### Phase 4: Testing

1. Write unit tests for the refactored code
2. Ensure all functionality is covered by tests
3. Fix any issues discovered during testing

## Detailed Implementation

### metrics.py

```python
import multiprocessing as mp
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Event
from typing import Optional


class CameraMetrics:
    """Metrics for tracking camera performance."""
    
    camera_fps: Synchronized
    detection_fps: Synchronized
    detection_frame: Synchronized
    process_fps: Synchronized
    skipped_fps: Synchronized
    read_start: Synchronized
    audio_rms: Synchronized
    audio_dBFS: Synchronized

    frame_queue: mp.Queue

    process: Optional[mp.Process]
    capture_process: Optional[mp.Process]
    ffmpeg_pid: Synchronized

    def __init__(self):
        self.camera_fps = mp.Value("d", 0)
        self.detection_fps = mp.Value("d", 0)
        self.detection_frame = mp.Value("d", 0)
        self.process_fps = mp.Value("d", 0)
        self.skipped_fps = mp.Value("d", 0)
        self.read_start = mp.Value("d", 0)
        self.audio_rms = mp.Value("d", 0)
        self.audio_dBFS = mp.Value("d", 0)

        self.frame_queue = mp.Queue(maxsize=2)

        self.process = None
        self.capture_process = None
        self.ffmpeg_pid = mp.Value("i", 0)


class PTZMetrics:
    """Metrics for tracking PTZ camera performance."""
    
    autotracker_enabled: Synchronized

    start_time: Synchronized
    stop_time: Synchronized
    frame_time: Synchronized
    zoom_level: Synchronized
    max_zoom: Synchronized
    min_zoom: Synchronized

    tracking_active: Event
    motor_stopped: Event
    reset: Event

    def __init__(self, *, autotracker_enabled: bool):
        self.autotracker_enabled = mp.Value("i", autotracker_enabled)

        self.start_time = mp.Value("d", 0)
        self.stop_time = mp.Value("d", 0)
        self.frame_time = mp.Value("d", 0)
        self.zoom_level = mp.Value("d", 0)
        self.max_zoom = mp.Value("d", 0)
        self.min_zoom = mp.Value("d", 0)

        self.tracking_active = mp.Event()
        self.motor_stopped = mp.Event()
        self.reset = mp.Event()

        self.motor_stopped.set()
```

### capture.py

```python
import datetime
import logging
import queue
import subprocess as sp
import threading
import time
from multiprocessing import Queue, Value
from multiprocessing.synchronize import Event as MpEvent
from typing import Any, Optional, Tuple

from frigate.camera.metrics import CameraMetrics
from frigate.comms.config_updater import ConfigSubscriber
from frigate.config import CameraConfig
from frigate.util.builtin import EventsPerSecond
from frigate.util.image import FrameManager

logger = logging.getLogger(__name__)


def stop_ffmpeg(ffmpeg_process, logger):
    """Stop an ffmpeg process gracefully."""
    logger.info("Terminating the existing ffmpeg process...")
    ffmpeg_process.terminate()
    try:
        logger.info("Waiting for ffmpeg to exit gracefully...")
        ffmpeg_process.communicate(timeout=30)
    except sp.TimeoutExpired:
        logger.info("FFmpeg didn't exit. Force killing...")
        ffmpeg_process.kill()
        ffmpeg_process.communicate()
    ffmpeg_process = None


def start_or_restart_ffmpeg(
    ffmpeg_cmd, logger, logpipe, frame_size=None, ffmpeg_process=None
):
    """Start or restart an ffmpeg process."""
    if ffmpeg_process is not None:
        stop_ffmpeg(ffmpeg_process, logger)

    if frame_size is None:
        process = sp.Popen(
            ffmpeg_cmd,
            stdout=sp.DEVNULL,
            stderr=logpipe,
            stdin=sp.DEVNULL,
            start_new_session=True,
        )
    else:
        process = sp.Popen(
            ffmpeg_cmd,
            stdout=sp.PIPE,
            stderr=logpipe,
            stdin=sp.DEVNULL,
            bufsize=frame_size * 10,
            start_new_session=True,
        )
    return process


def capture_frames(
    ffmpeg_process,
    config: CameraConfig,
    shm_frame_count: int,
    frame_index: int,
    frame_shape: Tuple[int, int],
    frame_manager: FrameManager,
    frame_queue: Queue,
    fps: Value,
    skipped_fps: Value,
    current_frame: Value,
    stop_event: MpEvent,
):
    """Capture frames from an ffmpeg process."""
    frame_size = frame_shape[0] * frame_shape[1]
    frame_rate = EventsPerSecond()
    frame_rate.start()
    skipped_eps = EventsPerSecond()
    skipped_eps.start()
    config_subscriber = ConfigSubscriber(f"config/enabled/{config.name}", True)

    def get_enabled_state():
        """Fetch the latest enabled state from ZMQ."""
        _, config_data = config_subscriber.check_for_update()

        if config_data:
            config.enabled = config_data.enabled

        return config.enabled

    while not stop_event.is_set():
        if not get_enabled_state():
            logger.debug(f"Stopping capture thread for disabled {config.name}")
            break

        fps.value = frame_rate.eps()
        skipped_fps.value = skipped_eps.eps()
        current_frame.value = datetime.datetime.now().timestamp()
        frame_name = f"{config.name}_frame{frame_index}"
        frame_buffer = frame_manager.write(frame_name)
        try:
            frame_buffer[:] = ffmpeg_process.stdout.read(frame_size)
        except Exception:
            # shutdown has been initiated
            if stop_event.is_set():
                break

            logger.error(f"{config.name}: Unable to read frames from ffmpeg process.")

            if ffmpeg_process.poll() is not None:
                logger.error(
                    f"{config.name}: ffmpeg process is not running. exiting capture thread..."
                )
                break

            continue

        frame_rate.update()

        # don't lock the queue to check, just try since it should rarely be full
        try:
            # add to the queue
            frame_queue.put((frame_name, current_frame.value), False)
            frame_manager.close(frame_name)
        except queue.Full:
            # if the queue is full, skip this frame
            skipped_eps.update()

        frame_index = 0 if frame_index == shm_frame_count - 1 else frame_index + 1


class CameraCapture(threading.Thread):
    """Thread for capturing frames from a camera."""
    
    def __init__(
        self,
        config: CameraConfig,
        shm_frame_count: int,
        frame_index: int,
        ffmpeg_process,
        frame_shape: Tuple[int, int],
        frame_queue: Queue,
        fps: Value,
        skipped_fps: Value,
        stop_event: MpEvent,
    ):
        threading.Thread.__init__(self)
        self.name = f"capture:{config.name}"
        self.config = config
        self.shm_frame_count = shm_frame_count
        self.frame_index = frame_index
        self.frame_shape = frame_shape
        self.frame_queue = frame_queue
        self.fps = fps
        self.stop_event = stop_event
        self.skipped_fps = skipped_fps
        self.frame_manager = SharedMemoryFrameManager()
        self.ffmpeg_process = ffmpeg_process
        self.current_frame = Value("d", 0.0)
        self.last_frame = 0

    def run(self):
        """Run the camera capture thread."""
        capture_frames(
            self.ffmpeg_process,
            self.config,
            self.shm_frame_count,
            self.frame_index,
            self.frame_shape,
            self.frame_manager,
            self.frame_queue,
            self.fps,
            self.skipped_fps,
            self.current_frame,
            self.stop_event,
        )
```

### watchdog.py

```python
import datetime
import logging
import os
import threading
import time
from multiprocessing import Queue, Value
from multiprocessing.synchronize import Event as MpEvent
from typing import Any, List, Optional

from frigate.camera.capture import CameraCapture, start_or_restart_ffmpeg, stop_ffmpeg
from frigate.comms.config_updater import ConfigSubscriber
from frigate.config import CameraConfig
from frigate.const import CACHE_DIR, CACHE_SEGMENT_FORMAT
from frigate.log import LogPipe

logger = logging.getLogger(__name__)


class CameraWatchdog(threading.Thread):
    """Watchdog for monitoring and restarting camera processes."""
    
    def __init__(
        self,
        camera_name: str,
        config: CameraConfig,
        shm_frame_count: int,
        frame_queue: Queue,
        camera_fps: Value,
        skipped_fps: Value,
        ffmpeg_pid: Value,
        stop_event: MpEvent,
    ):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(f"watchdog.{camera_name}")
        self.camera_name = camera_name
        self.config = config
        self.shm_frame_count = shm_frame_count
        self.capture_thread = None
        self.ffmpeg_detect_process = None
        self.logpipe = LogPipe(f"ffmpeg.{self.camera_name}.detect")
        self.ffmpeg_other_processes: List[dict[str, Any]] = []
        self.camera_fps = camera_fps
        self.skipped_fps = skipped_fps
        self.ffmpeg_pid = ffmpeg_pid
        self.frame_queue = frame_queue
        self.frame_shape = self.config.frame_shape_yuv
        self.frame_size = self.frame_shape[0] * self.frame_shape[1]
        self.fps_overflow_count = 0
        self.frame_index = 0
        self.stop_event = stop_event
        self.sleeptime = self.config.ffmpeg.retry_interval

        self.config_subscriber = ConfigSubscriber(f"config/enabled/{camera_name}", True)
        self.was_enabled = self.config.enabled

    def _update_enabled_state(self) -> bool:
        """Fetch the latest config and update enabled state."""
        _, config_data = self.config_subscriber.check_for_update()
        if config_data:
            self.config.enabled = config_data.enabled
            return config_data.enabled

        return self.config.enabled

    def run(self):
        """Run the camera watchdog thread."""
        if self._update_enabled_state():
            self.start_all_ffmpeg()

        time.sleep(self.sleeptime)
        while not self.stop_event.wait(self.sleeptime):
            enabled = self._update_enabled_state()
            if enabled != self.was_enabled:
                if enabled:
                    self.logger.debug(f"Enabling camera {self.camera_name}")
                    self.start_all_ffmpeg()
                else:
                    self.logger.debug(f"Disabling camera {self.camera_name}")
                    self.stop_all_ffmpeg()
                self.was_enabled = enabled
                continue

            if not enabled:
                continue

            now = datetime.datetime.now().timestamp()

            if not self.capture_thread.is_alive():
                self.camera_fps.value = 0
                self.logger.error(
                    f"Ffmpeg process crashed unexpectedly for {self.camera_name}."
                )
                self.logger.error(
                    "The following ffmpeg logs include the last 100 lines prior to exit."
                )
                self.logpipe.dump()
                self.start_ffmpeg_detect()
            elif now - self.capture_thread.current_frame.value > 20:
                self.camera_fps.value = 0
                self.logger.info(
                    f"No frames received from {self.camera_name} in 20 seconds. Exiting ffmpeg..."
                )
                self.ffmpeg_detect_process.terminate()
                try:
                    self.logger.info("Waiting for ffmpeg to exit gracefully...")
                    self.ffmpeg_detect_process.communicate(timeout=30)
                except sp.TimeoutExpired:
                    self.logger.info("FFmpeg did not exit. Force killing...")
                    self.ffmpeg_detect_process.kill()
                    self.ffmpeg_detect_process.communicate()
            elif self.camera_fps.value >= (self.config.detect.fps + 10):
                self.fps_overflow_count += 1

                if self.fps_overflow_count == 3:
                    self.fps_overflow_count = 0
                    self.camera_fps.value = 0
                    self.logger.info(
                        f"{self.camera_name} exceeded fps limit. Exiting ffmpeg..."
                    )
                    self.ffmpeg_detect_process.terminate()
                    try:
                        self.logger.info("Waiting for ffmpeg to exit gracefully...")
                        self.ffmpeg_detect_process.communicate(timeout=30)
                    except sp.TimeoutExpired:
                        self.logger.info("FFmpeg did not exit. Force killing...")
                        self.ffmpeg_detect_process.kill()
                        self.ffmpeg_detect_process.communicate()
            else:
                # process is running normally
                self.fps_overflow_count = 0

            for p in self.ffmpeg_other_processes:
                poll = p["process"].poll()

                if self.config.record.enabled and "record" in p["roles"]:
                    latest_segment_time = self.get_latest_segment_datetime(
                        p.get(
                            "latest_segment_time",
                            datetime.datetime.now().astimezone(datetime.timezone.utc),
                        )
                    )

                    if datetime.datetime.now().astimezone(datetime.timezone.utc) > (
                        latest_segment_time + datetime.timedelta(seconds=120)
                    ):
                        self.logger.error(
                            f"No new recording segments were created for {self.camera_name} in the last 120s. restarting the ffmpeg record process..."
                        )
                        p["process"] = start_or_restart_ffmpeg(
                            p["cmd"],
                            self.logger,
                            p["logpipe"],
                            ffmpeg_process=p["process"],
                        )
                        continue
                    else:
                        p["latest_segment_time"] = latest_segment_time

                if poll is None:
                    continue

                p["logpipe"].dump()
                p["process"] = start_or_restart_ffmpeg(
                    p["cmd"], self.logger, p["logpipe"], ffmpeg_process=p["process"]
                )

        self.stop_all_ffmpeg()
        self.logpipe.close()
        self.config_subscriber.stop()

    def start_ffmpeg_detect(self):
        """Start the ffmpeg process for detection."""
        ffmpeg_cmd = [
            c["cmd"] for c in self.config.ffmpeg_cmds if "detect" in c["roles"]
        ][0]
        self.ffmpeg_detect_process = start_or_restart_ffmpeg(
            ffmpeg_cmd, self.logger, self.logpipe, self.frame_size
        )
        self.ffmpeg_pid.value = self.ffmpeg_detect_process.pid
        self.capture_thread = CameraCapture(
            self.config,
            self.shm_frame_count,
            self.frame_index,
            self.ffmpeg_detect_process,
            self.frame_shape,
            self.frame_queue,
            self.camera_fps,
            self.skipped_fps,
            self.stop_event,
        )
        self.capture_thread.start()

    def start_all_ffmpeg(self):
        """Start all ffmpeg processes (detection and others)."""
        logger.debug(f"Starting all ffmpeg processes for {self.camera_name}")
        self.start_ffmpeg_detect()
        for c in self.config.ffmpeg_cmds:
            if "detect" in c["roles"]:
                continue
            logpipe = LogPipe(
                f"ffmpeg.{self.camera_name}.{'_'.join(sorted(c['roles']))}"
            )
            self.ffmpeg_other_processes.append(
                {
                    "cmd": c["cmd"],
                    "roles": c["roles"],
                    "logpipe": logpipe,
                    "process": start_or_restart_ffmpeg(c["cmd"], self.logger, logpipe),
                }
            )

    def stop_all_ffmpeg(self):
        """Stop all ffmpeg processes (detection and others)."""
        logger.debug(f"Stopping all ffmpeg processes for {self.camera_name}")
        if self.capture_thread is not None and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)
            if self.capture_thread.is_alive():
                self.logger.warning(
                    f"Capture thread for {self.camera_name} did not stop gracefully."
                )
        if self.ffmpeg_detect_process is not None:
            stop_ffmpeg(self.ffmpeg_detect_process, self.logger)
            self.ffmpeg_detect_process = None
        for p in self.ffmpeg_other_processes[:]:
            if p["process"] is not None:
                stop_ffmpeg(p["process"], self.logger)
            p["logpipe"].close()
        self.ffmpeg_other_processes.clear()

    def get_latest_segment_datetime(self, latest_segment: datetime.datetime) -> int:
        """Checks if ffmpeg is still writing recording segments to cache."""
        cache_files = sorted(
            [
                d
                for d in os.listdir(CACHE_DIR)
                if os.path.isfile(os.path.join(CACHE_DIR, d))
                and d.endswith(".mp4")
                and not d.startswith("preview_")
            ]
        )
        newest_segment_time = latest_segment

        for file in cache_files:
            if self.camera_name in file:
                basename = os.path.splitext(file)[0]
                _, date = basename.rsplit("@", maxsplit=1)
                segment_time = datetime.datetime.strptime(
                    date, CACHE_SEGMENT_FORMAT
                ).astimezone(datetime.timezone.utc)
                if segment_time > newest_segment_time:
                    newest_segment_time = segment_time

        return newest_segment_time
```

### manager.py

```python
import logging
import multiprocessing as mp
import os
import signal
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MpEvent
from typing import Dict, Optional

from setproctitle import setproctitle

from frigate.camera.metrics import CameraMetrics, PTZMetrics
from frigate.camera.watchdog import CameraWatchdog
from frigate.config import CameraConfig
from frigate.util.image import SharedMemoryFrameManager

logger = logging.getLogger(__name__)


class CameraManager:
    """Manager for camera processes."""
    
    def __init__(self, config):
        self.config = config
        self.camera_metrics: Dict[str, CameraMetrics] = {}
        self.ptz_metrics: Dict[str, PTZMetrics] = {}
        self.stop_event: MpEvent = mp.Event()
        self.frame_manager = SharedMemoryFrameManager()
        
    def init_camera_metrics(self) -> None:
        """Initialize camera metrics."""
        for camera_name in self.config.cameras.keys():
            self.camera_metrics[camera_name] = CameraMetrics()
            self.ptz_metrics[camera_name] = PTZMetrics(
                autotracker_enabled=self.config.cameras[
                    camera_name
                ].onvif.autotracking.enabled
            )
            
    def start_camera_capture_processes(self, shm_frame_count: int) -> None:
        """Start camera capture processes."""
        for name, config in self.config.cameras.items():
            if not self.config.cameras[name].enabled:
                logger.info(f"Capture process not started for disabled camera {name}")
                continue

            # pre-create shms
            for i in range(shm_frame_count):
                frame_size = config.frame_shape_yuv[0] * config.frame_shape_yuv[1]
                self.frame_manager.create(f"{config.name}_frame{i}", frame_size)

            capture_process = mp.Process(
                target=capture_camera,
                name=f"camera_capture:{name}",
                args=(name, config, shm_frame_count, self.camera_metrics[name]),
            )
            capture_process.daemon = True
            self.camera_metrics[name].capture_process = capture_process
            capture_process.start()
            logger.info(f"Capture process started for {name}: {capture_process.pid}")
            
    def stop_camera_capture_processes(self) -> None:
        """Stop camera capture processes."""
        for camera, metrics in self.camera_metrics.items():
            capture_process = metrics.capture_process
            if capture_process is not None:
                logger.info(f"Waiting for capture process for {camera} to stop")
                capture_process.terminate()
                capture_process.join()


def capture_camera(
    name: str, 
    config: CameraConfig, 
    shm_frame_count: int, 
    camera_metrics: CameraMetrics
) -> None:
    """Capture frames from a camera."""
    stop_event = mp.Event()

    def receiveSignal(signalNumber, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)

    threading.current_thread().name = f"capture:{name}"
    setproctitle(f"frigate.capture:{name}")

    camera_watchdog = CameraWatchdog(
        name,
        config,
        shm_frame_count,
        camera_metrics.frame_queue,
        camera_metrics.camera_fps,
        camera_metrics.skipped_fps,
        camera_metrics.ffmpeg_pid,
        stop_event,
    )
    camera_watchdog.start()
    camera_watchdog.join()
```

### processing.py

```python
import datetime
import logging
import multiprocessing as mp
import signal
import threading
import time
from multiprocessing import Queue
from multiprocessing.synchronize import Event as MpEvent
from typing import Any, Dict, List, Optional, Tuple

from setproctitle import setproctitle

from frigate.camera.metrics import CameraMetrics, PTZMetrics
from frigate.comms.config_updater import ConfigSubscriber
from frigate.comms.inter_process import InterProcessRequestor
from frigate.config import CameraConfig, DetectConfig, ModelConfig
from frigate.config.camera.camera import CameraTypeEnum
from frigate.const import REQUEST_REGION_GRID
from frigate.motion import MotionDetector
from frigate.motion.improved_motion import ImprovedMotionDetector
from frigate.object_detection.base import RemoteObjectDetector
from frigate.ptz.autotrack import ptz_moving_at_frame_time
from frigate.track import ObjectTracker
from frigate.track.norfair_tracker import NorfairTracker
from frigate.track.tracked_object import TrackedObjectAttribute
from frigate.util.builtin import EventsPerSecond, get_tomorrow_at_time
from frigate.util.image import FrameManager, SharedMemoryFrameManager
from frigate.util.object import (
    create_tensor_input,
    get_cluster_candidates,
    get_cluster_region,
    get_cluster_region_from_grid,
    get_min_region_size,
    get_startup_regions,
    inside_any,
    intersects_any,
    is_object_filtered,
    reduce_detections,
)
from frigate.util.services import listen

logger = logging.getLogger(__name__)


def detect(
    detect_config: DetectConfig,
    object_detector,
    frame,
    model_config: ModelConfig,
    region,
    objects_to_track,
    object_filters,
):
    """Detect objects in a frame."""
    tensor_input = create_tensor_input(frame, model_config, region)

    detections = []
    region_detections = object_detector.detect(tensor_input)
    for d in region_detections:
        box = d[2]
        size = region[2] - region[0]
        x_min = int(max(0, (box[1] * size) + region[0]))
        y_min = int(max(0, (box[0] * size) + region[1]))
        x_max = int(min(detect_config.width - 1, (box[3] * size) + region[0]))
        y_max = int(min(detect_config.height - 1, (box[2] * size) + region[1]))

        # ignore objects that were detected outside the frame
        if (x_min >= detect_config.width - 1) or (y_min >= detect_config.height - 1):
            continue

        width = x_max - x_min
        height = y_max - y_min
        area = width * height
        ratio = width / max(1, height)
        det = (d[0], d[1], (x_min, y_min, x_max, y_max), area, ratio, region)
        # apply object filters
        if is_object_filtered(det, objects_to_track, object_filters):
            continue
        detections.append(det)
    return detections


def process_frames(
    camera_name: str,
    requestor: InterProcessRequestor,
    frame_queue: Queue,
    frame_shape: Tuple
