# Camera Integration Refactoring Implementation

This document outlines the specific implementation steps for refactoring the camera integration code in the Arkos AI project, as described in the [Camera Refactoring Plan](./camera-refactoring-plan.md).

## Implementation Steps

### Phase 1: Code Reorganization and Renaming

1. **Create New File Structure**
   - Create the following files:
     - `arkos/camera/metrics.py`
     - `arkos/camera/capture.py`
     - `arkos/camera/processing.py`
     - `arkos/camera/state.py` (already exists, will be updated)
     - `arkos/camera/activity.py`
     - `arkos/camera/watchdog.py`
     - `arkos/camera/manager.py`

2. **Move and Rename Existing Code**
   - Move `CameraMetrics` and `PTZMetrics` from `frigate/camera/__init__.py` to `arkos/camera/metrics.py`
   - Move `CameraActivityManager` from `frigate/camera/activity_manager.py` to `arkos/camera/activity.py`
   - Move `CameraState` from `frigate/camera/state.py` to the new `arkos/camera/state.py`
   - Move camera capture code from `frigate/video.py` to `arkos/camera/capture.py`
   - Move camera processing code from `frigate/video.py` to `arkos/camera/processing.py`
   - Move camera watchdog code from `frigate/video.py` to `arkos/camera/watchdog.py`
   - Create a new `CameraManager` class in `arkos/camera/manager.py`
   - Update all imports to use `arkos` instead of `frigate`

3. **Update Imports**
   - Update imports in all files to reflect the new structure
   - Update `frigate/camera/__init__.py` to expose the public API

4. **Update References in Other Files**
   - Update references to camera code in `frigate/app.py` and other files

### Phase 2: Improve Code Quality

1. **Add Type Hints**
   - Add comprehensive type hints to all functions and classes
   - Use `Optional` for parameters that can be `None`
   - Use `Tuple`, `List`, `Dict`, etc. for collection types

2. **Improve Error Handling**
   - Add try/except blocks for error-prone operations
   - Add proper error messages and logging
   - Add error recovery mechanisms where appropriate

3. **Refactor Complex Functions**
   - Break down complex functions into smaller, more focused functions
   - Extract common code into utility functions
   - Improve function and variable naming

4. **Remove Duplicated Code**
   - Identify and remove duplicated code
   - Create utility functions for common operations

### Phase 3: Reduce Coupling

1. **Introduce Interfaces**
   - Create interfaces for dependencies using abstract base classes
   - Use dependency injection to reduce coupling

2. **Use Dependency Injection**
   - Pass dependencies as parameters rather than creating them in the class
   - Use factory functions to create dependencies

3. **Replace Global State**
   - Replace global state with proper class attributes
   - Use context managers for resources that need cleanup

### Phase 4: Testing

1. **Write Unit Tests**
   - Write unit tests for each component
   - Use mocks for dependencies
   - Test error handling

2. **Write Integration Tests**
   - Write integration tests for the camera module
   - Test interactions between components

3. **Fix Issues**
   - Fix any issues discovered during testing
   - Update documentation as needed

## Detailed Implementation Tasks

### Task 1: Create New File Structure

```bash
# Create new files
touch frigate/camera/metrics.py
touch frigate/camera/capture.py
touch frigate/camera/processing.py
touch frigate/camera/activity.py
touch frigate/camera/watchdog.py
touch frigate/camera/manager.py
```

### Task 2: Implement `metrics.py`

Move `CameraMetrics` and `PTZMetrics` from `frigate/camera/__init__.py` to `frigate/camera/metrics.py`:

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

### Task 3: Implement `activity.py`

Move `CameraActivityManager` from `frigate/camera/activity_manager.py` to `frigate/camera/activity.py`:

```python
"""Manage camera activity and updating listeners."""

from collections import Counter
from typing import Callable, Dict, Set

from frigate.config.config import FrigateConfig


class CameraActivityManager:
    """Manages camera activity and updates listeners."""
    
    def __init__(
        self, config: FrigateConfig, publish: Callable[[str, any], None]
    ) -> None:
        self.config = config
        self.publish = publish
        self.last_camera_activity: Dict[str, Dict[str, any]] = {}
        self.camera_all_object_counts: Dict[str, Counter] = {}
        self.camera_active_object_counts: Dict[str, Counter] = {}
        self.zone_all_object_counts: Dict[str, Counter] = {}
        self.zone_active_object_counts: Dict[str, Counter] = {}
        self.all_zone_labels: Dict[str, Set[str]] = {}

        for camera_config in config.cameras.values():
            if not camera_config.enabled_in_config:
                continue

            self.last_camera_activity[camera_config.name] = {}
            self.camera_all_object_counts[camera_config.name] = Counter()
            self.camera_active_object_counts[camera_config.name] = Counter()

            for zone, zone_config in camera_config.zones.items():
                if zone not in self.all_zone_labels:
                    self.zone_all_object_counts[zone] = Counter()
                    self.zone_active_object_counts[zone] = Counter()
                    self.all_zone_labels[zone] = set()

                self.all_zone_labels[zone].update(
                    zone_config.objects
                    if zone_config.objects
                    else camera_config.objects.track
                )

    def update_activity(self, new_activity: Dict[str, Dict[str, any]]) -> None:
        """Update camera activity and notify listeners."""
        all_objects: list[dict[str, any]] = []

        for camera in new_activity.keys():
            new_objects = new_activity[camera].get("objects", [])
            all_objects.extend(new_objects)

            if self.last_camera_activity.get(camera, {}).get("objects") != new_objects:
                self.compare_camera_activity(camera, new_objects)

        # run through every zone, getting a count of objects in that zone right now
        for zone, labels in self.all_zone_labels.items():
            all_zone_objects = Counter(
                obj["label"].replace("-verified", "")
                for obj in all_objects
                if zone in obj["current_zones"]
            )
            active_zone_objects = Counter(
                obj["label"].replace("-verified", "")
                for obj in all_objects
                if zone in obj["current_zones"] and not obj["stationary"]
            )
            any_changed = False

            # run through each object and check what topics need to be updated for this zone
            for label in labels:
                new_count = all_zone_objects[label]
                new_active_count = active_zone_objects[label]

                if (
                    new_count != self.zone_all_object_counts[zone][label]
                    or label not in self.zone_all_object_counts[zone]
                ):
                    any_changed = True
                    self.publish(f"{zone}/{label}", new_count)
                    self.zone_all_object_counts[zone][label] = new_count

                if (
                    new_active_count != self.zone_active_object_counts[zone][label]
                    or label not in self.zone_active_object_counts[zone]
                ):
                    any_changed = True
                    self.publish(f"{zone}/{label}/active", new_active_count)
                    self.zone_active_object_counts[zone][label] = new_active_count

            if any_changed:
                self.publish(f"{zone}/all", sum(list(all_zone_objects.values())))
                self.publish(
                    f"{zone}/all/active", sum(list(active_zone_objects.values()))
                )

        self.last_camera_activity = new_activity

    def compare_camera_activity(
        self, camera: str, new_activity: Dict[str, any]
    ) -> None:
        """Compare camera activity and update listeners."""
        all_objects = Counter(
            obj["label"].replace("-verified", "") for obj in new_activity
        )
        active_objects = Counter(
            obj["label"].replace("-verified", "")
            for obj in new_activity
            if not obj["stationary"]
        )
        any_changed = False

        # run through each object and check what topics need to be updated
        for label in self.config.cameras[camera].objects.track:
            if label in self.config.model.non_logo_attributes:
                continue

            new_count = all_objects[label]
            new_active_count = active_objects[label]

            if (
                new_count != self.camera_all_object_counts[camera][label]
                or label not in self.camera_all_object_counts[camera]
            ):
                any_changed = True
                self.publish(f"{camera}/{label}", new_count)
                self.camera_all_object_counts[camera][label] = new_count

            if (
                new_active_count != self.camera_active_object_counts[camera][label]
                or label not in self.camera_active_object_counts[camera]
            ):
                any_changed = True
                self.publish(f"{camera}/{label}/active", new_active_count)
                self.camera_active_object_counts[camera][label] = new_active_count

        if any_changed:
            self.publish(f"{camera}/all", sum(list(all_objects.values())))
            self.publish(f"{camera}/all/active", sum(list(active_objects.values())))
```

### Task 4: Update `__init__.py`

Update `frigate/camera/__init__.py` to expose the public API:

```python
"""Camera module for Arkos AI."""

from frigate.camera.metrics import CameraMetrics, PTZMetrics
from frigate.camera.activity import CameraActivityManager
from frigate.camera.state import CameraState
from frigate.camera.manager import CameraManager

__all__ = [
    "CameraMetrics",
    "PTZMetrics",
    "CameraActivityManager",
    "CameraState",
    "CameraManager",
]
```

### Task 5: Update `app.py`

Update `frigate/app.py` to use the new camera module:

```python
# Replace imports
from frigate.camera import CameraMetrics, PTZMetrics
from frigate.camera.manager import CameraManager

# Replace camera initialization code
def init_camera_metrics(self) -> None:
    # create camera_metrics
    self.camera_manager = CameraManager(self.config)
    self.camera_manager.init_camera_metrics()
    self.camera_metrics = self.camera_manager.camera_metrics
    self.ptz_metrics = self.camera_manager.ptz_metrics

# Replace camera start code
def start_camera_capture_processes(self) -> None:
    shm_frame_count = self.shm_frame_count()
    self.camera_manager.start_camera_capture_processes(shm_frame_count)

# Replace camera stop code
def stop(self) -> None:
    logger.info("Stopping...")

    self.stop_event.set()

    # set an end_time on entries without an end_time before exiting
    Event.update(
        end_time=datetime.datetime.now().timestamp(), has_snapshot=False
    ).where(Event.end_time == None).execute()
    ReviewSegment.update(end_time=datetime.datetime.now().timestamp()).where(
        ReviewSegment.end_time == None
    ).execute()

    # stop the audio process
    if self.audio_process:
        self.audio_process.terminate()
        self.audio_process.join()

    # stop the onvif controller
    if self.onvif_controller:
        self.onvif_controller.close()

    # stop the camera processes
    self.camera_manager.stop_camera_capture_processes()

    # ensure the detectors are done
    for detector in self.detectors.values():
        detector.stop()

    empty_and_close_queue(self.detection_queue)
    logger.info("Detection queue closed")

    self.detected_frames_processor.join()
    empty_and_close_queue(self.detected_frames_queue)
    logger.info("Detected frames queue closed")

    self.timeline_processor.join()
    self.event_processor.join()
    empty_and_close_queue(self.timeline_queue)
    logger.info("Timeline queue closed")

    self.output_processor.terminate()
    self.output_processor.join()

    self.recording_process.terminate()
    self.recording_process.join()

    self.review_segment_process.terminate()
    self.review_segment_process.join()

    self.dispatcher.stop()
    self.ptz_autotracker_thread.join()

    self.event_cleanup.join()
    self.record_cleanup.join()
    self.stats_emitter.join()
    self.frigate_watchdog.join()
    self.db.stop()

    # Save embeddings stats to disk
    if self.embeddings:
        self.embeddings.stop()

    # Stop Communicators
    self.inter_process_communicator.stop()
    self.inter_config_updater.stop()
    self.event_metadata_updater.stop()
    self.inter_zmq_proxy.stop()

    self.frame_manager.cleanup()
    while len(self.detection_shms) > 0:
        shm = self.detection_shms.pop()
        shm.close()
        shm.unlink()

    os._exit(os.EX_OK)
```

## Testing Plan

### Unit Tests

1. **Test `CameraMetrics` and `PTZMetrics`**
   - Test initialization
   - Test value updates

2. **Test `CameraActivityManager`**
   - Test initialization
   - Test activity updates
   - Test zone updates

3. **Test `CameraState`**
   - Test initialization
   - Test state updates
   - Test object tracking

4. **Test `CameraCapture`**
   - Test frame capture
   - Test error handling

5. **Test `CameraWatchdog`**
   - Test process monitoring
   - Test process restart

6. **Test `CameraManager`**
   - Test initialization
   - Test camera start/stop

### Integration Tests

1. **Test Camera Module Integration**
   - Test camera module with mock ffmpeg
   - Test camera module with mock object detector

2. **Test Camera Module with App**
   - Test camera module integration with app
   - Test camera module with real ffmpeg (if possible)

## Conclusion

This implementation plan provides a detailed roadmap for refactoring the camera integration code in the Arkos AI project. By following this plan, we can improve the code organization, maintainability, and extensibility while maintaining compatibility with the rest of the system.
