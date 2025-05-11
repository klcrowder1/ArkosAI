"""Storage monitoring for Arkos AI."""

import datetime
import logging
import os
import shutil
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import psutil

from arkos.config import ArkosConfig
from arkos.const import RECORD_DIR
from arkos.models import Event, Recordings
from arkos.storage.tiered import StorageTier, StorageTierType, TieredStorageManager
from arkos.notifications.types import NotificationLevel

logger = logging.getLogger(__name__)


class StorageHealthStatus(str, Enum):
    """Storage health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class StorageMetrics:
    """Storage metrics for a specific path."""

    def __init__(self, path: str) -> None:
        """Initialize storage metrics.

        Args:
            path: Path to monitor
        """
        self.path = path
        self.total_space_mb = 0.0
        self.used_space_mb = 0.0
        self.free_space_mb = 0.0
        self.usage_percent = 0.0
        self.read_speed_mbps = 0.0
        self.write_speed_mbps = 0.0
        self.io_errors = 0
        self.health_status = StorageHealthStatus.UNKNOWN
        self.last_updated = datetime.datetime.now()

    def update(self) -> None:
        """Update storage metrics."""
        try:
            # Get disk usage
            usage = shutil.disk_usage(self.path)
            self.total_space_mb = round(usage.total / pow(2, 20), 1)
            self.used_space_mb = round((usage.total - usage.free) / pow(2, 20), 1)
            self.free_space_mb = round(usage.free / pow(2, 20), 1)
            self.usage_percent = round(self.used_space_mb / self.total_space_mb * 100, 1) if self.total_space_mb > 0 else 0

            # Update health status based on usage
            if self.usage_percent >= 95:
                self.health_status = StorageHealthStatus.CRITICAL
            elif self.usage_percent >= 85:
                self.health_status = StorageHealthStatus.WARNING
            else:
                self.health_status = StorageHealthStatus.HEALTHY

            # Update timestamp
            self.last_updated = datetime.datetime.now()
        except Exception as e:
            logger.error(f"Error updating storage metrics for {self.path}: {e}")
            self.health_status = StorageHealthStatus.UNKNOWN

    def measure_io_performance(self, test_file_size_mb: int = 10) -> None:
        """Measure I/O performance.

        Args:
            test_file_size_mb: Size of test file in MB
        """
        test_file = os.path.join(self.path, ".arkos_io_test")
        test_data = b'0' * 1024 * 1024  # 1MB of data

        try:
            # Measure write speed
            start_time = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(test_file_size_mb):
                    f.write(test_data)
            write_time = time.time() - start_time
            self.write_speed_mbps = round(test_file_size_mb / write_time, 2) if write_time > 0 else 0

            # Measure read speed
            start_time = time.time()
            with open(test_file, 'rb') as f:
                while f.read(1024 * 1024):
                    pass
            read_time = time.time() - start_time
            self.read_speed_mbps = round(test_file_size_mb / read_time, 2) if read_time > 0 else 0

            # Clean up test file
            os.remove(test_file)
        except Exception as e:
            logger.error(f"Error measuring I/O performance for {self.path}: {e}")
            self.io_errors += 1

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary.

        Returns:
            Dictionary of metrics
        """
        return {
            "path": self.path,
            "total_space_mb": self.total_space_mb,
            "used_space_mb": self.used_space_mb,
            "free_space_mb": self.free_space_mb,
            "usage_percent": self.usage_percent,
            "read_speed_mbps": self.read_speed_mbps,
            "write_speed_mbps": self.write_speed_mbps,
            "io_errors": self.io_errors,
            "health_status": self.health_status,
            "last_updated": self.last_updated.isoformat(),
        }


class CameraStorageMetrics:
    """Storage metrics for a specific camera."""

    def __init__(self, camera: str) -> None:
        """Initialize camera storage metrics.

        Args:
            camera: Camera name
        """
        self.camera = camera
        self.total_size_mb = 0.0
        self.event_size_mb = 0.0
        self.non_event_size_mb = 0.0
        self.bandwidth_mbh = 0.0  # MB per hour
        self.recording_count = 0
        self.event_count = 0
        self.oldest_recording = None
        self.newest_recording = None
        self.last_updated = datetime.datetime.now()

    def update(self) -> None:
        """Update camera storage metrics."""
        try:
            # Get total storage used by this camera
            total_size = (
                Recordings.select(Recordings.segment_size)
                .where(Recordings.camera == self.camera)
                .scalar()
            )
            self.total_size_mb = round(total_size / pow(2, 20), 1) if total_size else 0

            # Get event recordings size
            event_size = (
                Recordings.select(Recordings.segment_size)
                .join(Event, on=(
                    (Recordings.camera == Event.camera) &
                    (Recordings.start_time <= Event.end_time) &
                    (Recordings.end_time >= Event.start_time)
                ))
                .where(Recordings.camera == self.camera)
                .scalar()
            )
            self.event_size_mb = round(event_size / pow(2, 20), 1) if event_size else 0
            self.non_event_size_mb = self.total_size_mb - self.event_size_mb

            # Get recording count
            self.recording_count = (
                Recordings.select()
                .where(Recordings.camera == self.camera)
                .count()
            )

            # Get event count
            self.event_count = (
                Event.select()
                .where(Event.camera == self.camera)
                .count()
            )

            # Get oldest and newest recordings
            oldest = (
                Recordings.select(Recordings.start_time)
                .where(Recordings.camera == self.camera)
                .order_by(Recordings.start_time.asc())
                .limit(1)
                .scalar()
            )
            newest = (
                Recordings.select(Recordings.end_time)
                .where(Recordings.camera == self.camera)
                .order_by(Recordings.end_time.desc())
                .limit(1)
                .scalar()
            )
            self.oldest_recording = datetime.datetime.fromtimestamp(oldest) if oldest else None
            self.newest_recording = datetime.datetime.fromtimestamp(newest) if newest else None

            # Calculate bandwidth (MB per hour)
            # Use the average of the last 100 segments
            bandwidth = (
                Recordings.select(fn.AVG(Recordings.segment_size / (Recordings.end_time - Recordings.start_time)))
                .where(Recordings.camera == self.camera, Recordings.segment_size > 0)
                .limit(100)
                .scalar()
            )
            self.bandwidth_mbh = round(bandwidth * 3600, 2) if bandwidth else 0

            # Update timestamp
            self.last_updated = datetime.datetime.now()
        except Exception as e:
            logger.error(f"Error updating camera storage metrics for {self.camera}: {e}")

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary.

        Returns:
            Dictionary of metrics
        """
        return {
            "camera": self.camera,
            "total_size_mb": self.total_size_mb,
            "event_size_mb": self.event_size_mb,
            "non_event_size_mb": self.non_event_size_mb,
            "bandwidth_mbh": self.bandwidth_mbh,
            "recording_count": self.recording_count,
            "event_count": self.event_count,
            "oldest_recording": self.oldest_recording.isoformat() if self.oldest_recording else None,
            "newest_recording": self.newest_recording.isoformat() if self.newest_recording else None,
            "last_updated": self.last_updated.isoformat(),
        }


class StorageMonitor(threading.Thread):
    """Monitor storage usage and health."""

    def __init__(
        self, 
        config: ArkosConfig, 
        stop_event, 
        tiered_storage_manager: Optional[TieredStorageManager] = None,
        check_interval: int = 300,
        performance_check_interval: int = 3600,
        notification_manager = None
    ) -> None:
        """Initialize storage monitor.

        Args:
            config: Arkos configuration
            stop_event: Event to signal thread to stop
            tiered_storage_manager: Tiered storage manager instance
            check_interval: Interval in seconds to check storage metrics
            performance_check_interval: Interval in seconds to check I/O performance
            notification_manager: Notification manager instance
        """
        super().__init__(name="storage_monitor")
        self.config = config
        self.stop_event = stop_event
        self.tiered_storage_manager = tiered_storage_manager
        self.check_interval = check_interval
        self.performance_check_interval = performance_check_interval
        self.notification_manager = notification_manager
        
        # Initialize metrics
        self.storage_metrics: Dict[str, StorageMetrics] = {}
        self.camera_metrics: Dict[str, CameraStorageMetrics] = {}
        self.last_performance_check = 0
        
        # Initialize metrics for default storage path
        self.storage_metrics[RECORD_DIR] = StorageMetrics(RECORD_DIR)
        
        # Initialize metrics for each camera
        for camera in self.config.cameras.keys():
            self.camera_metrics[camera] = CameraStorageMetrics(camera)
        
        # Initialize metrics for each storage tier if tiered storage is enabled
        if self.tiered_storage_manager:
            for tier in self.tiered_storage_manager.tiers:
                if tier.path not in self.storage_metrics:
                    self.storage_metrics[tier.path] = StorageMetrics(tier.path)

    def update_metrics(self) -> None:
        """Update all storage metrics."""
        # Update storage metrics
        for path, metrics in self.storage_metrics.items():
            metrics.update()
        
        # Update camera metrics
        for camera, metrics in self.camera_metrics.items():
            metrics.update()
        
        # Check if we need to perform I/O performance tests
        current_time = time.time()
        if current_time - self.last_performance_check >= self.performance_check_interval:
            self.check_io_performance()
            self.last_performance_check = current_time

    def check_io_performance(self) -> None:
        """Check I/O performance for all storage paths."""
        for path, metrics in self.storage_metrics.items():
            metrics.measure_io_performance()

    def check_storage_health(self) -> None:
        """Check storage health and send notifications if needed."""
        if not self.notification_manager:
            return
            
        for path, metrics in self.storage_metrics.items():
            # Check for critical storage issues
            if metrics.health_status == StorageHealthStatus.CRITICAL:
                self.notification_manager.send(
                    "storage_critical",
                    f"Storage critical: {path} is at {metrics.usage_percent}% capacity",
                    {"path": path, "usage_percent": metrics.usage_percent},
                    level=NotificationLevel.CRITICAL
                )
            # Check for warning storage issues
            elif metrics.health_status == StorageHealthStatus.WARNING:
                self.notification_manager.send(
                    "storage_warning",
                    f"Storage warning: {path} is at {metrics.usage_percent}% capacity",
                    {"path": path, "usage_percent": metrics.usage_percent},
                    level=NotificationLevel.WARNING
                )
            # Check for I/O errors
            if metrics.io_errors > 0:
                self.notification_manager.send(
                    "storage_io_error",
                    f"Storage I/O error: {path} has {metrics.io_errors} I/O errors",
                    {"path": path, "io_errors": metrics.io_errors},
                    level=NotificationLevel.ERROR
                )

    def get_storage_metrics(self) -> Dict[str, Dict]:
        """Get all storage metrics.

        Returns:
            Dictionary of storage metrics
        """
        return {path: metrics.to_dict() for path, metrics in self.storage_metrics.items()}

    def get_camera_metrics(self) -> Dict[str, Dict]:
        """Get all camera metrics.

        Returns:
            Dictionary of camera metrics
        """
        return {camera: metrics.to_dict() for camera, metrics in self.camera_metrics.items()}

    def get_overall_metrics(self) -> Dict:
        """Get overall storage metrics.

        Returns:
            Dictionary of overall metrics
        """
        total_space_mb = sum(m.total_space_mb for m in self.storage_metrics.values())
        used_space_mb = sum(m.used_space_mb for m in self.storage_metrics.values())
        free_space_mb = sum(m.free_space_mb for m in self.storage_metrics.values())
        usage_percent = round(used_space_mb / total_space_mb * 100, 1) if total_space_mb > 0 else 0
        
        total_camera_size_mb = sum(m.total_size_mb for m in self.camera_metrics.values())
        total_event_size_mb = sum(m.event_size_mb for m in self.camera_metrics.values())
        total_non_event_size_mb = sum(m.non_event_size_mb for m in self.camera_metrics.values())
        total_bandwidth_mbh = sum(m.bandwidth_mbh for m in self.camera_metrics.values())
        
        # Calculate estimated time until full
        hours_until_full = round(free_space_mb / total_bandwidth_mbh, 1) if total_bandwidth_mbh > 0 else float('inf')
        
        return {
            "total_space_mb": total_space_mb,
            "used_space_mb": used_space_mb,
            "free_space_mb": free_space_mb,
            "usage_percent": usage_percent,
            "total_camera_size_mb": total_camera_size_mb,
            "total_event_size_mb": total_event_size_mb,
            "total_non_event_size_mb": total_non_event_size_mb,
            "total_bandwidth_mbh": total_bandwidth_mbh,
            "hours_until_full": hours_until_full,
            "days_until_full": round(hours_until_full / 24, 1),
            "health_status": self._get_overall_health_status(),
            "last_updated": datetime.datetime.now().isoformat(),
        }

    def _get_overall_health_status(self) -> StorageHealthStatus:
        """Get overall health status.

        Returns:
            Overall health status
        """
        statuses = [m.health_status for m in self.storage_metrics.values()]
        
        if StorageHealthStatus.CRITICAL in statuses:
            return StorageHealthStatus.CRITICAL
        elif StorageHealthStatus.WARNING in statuses:
            return StorageHealthStatus.WARNING
        elif StorageHealthStatus.UNKNOWN in statuses:
            return StorageHealthStatus.UNKNOWN
        else:
            return StorageHealthStatus.HEALTHY

    def run(self) -> None:
        """Run the storage monitor."""
        logger.info("Starting storage monitor")
        
        # Initial update
        self.update_metrics()
        
        while not self.stop_event.wait(self.check_interval):
            try:
                # Update metrics
                self.update_metrics()
                
                # Check storage health
                self.check_storage_health()
                
                # Log overall metrics
                overall = self.get_overall_metrics()
                logger.info(
                    f"Storage usage: {overall['usage_percent']}% "
                    f"({overall['used_space_mb']}/{overall['total_space_mb']} MB), "
                    f"estimated {overall['days_until_full']} days until full"
                )
            except Exception as e:
                logger.error(f"Error in storage monitor: {e}")
        
        logger.info("Exiting storage monitor")
