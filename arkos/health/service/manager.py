"""
Health manager for coordinating health monitoring components.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Union

from arkos.camera import CameraMetrics
from arkos.camera.connection import CameraConnectionManager
from arkos.config import CameraConfig
from arkos.health import CameraHealth, HealthCheck, HealthStatus
from arkos.health.connectivity import ConnectivityMonitor

logger = logging.getLogger(__name__)


class HealthManager:
    """
    Manages health monitoring components and provides a unified interface for health data.
    """

    def __init__(
        self,
        connection_manager: CameraConnectionManager,
        config: Dict[str, CameraConfig],
        camera_metrics: Dict[str, CameraMetrics],
        check_interval: int = 60,
        bandwidth_check_interval: int = 300,
        latency_check_interval: int = 60,
    ):
        """
        Initialize the health manager.
        
        Args:
            connection_manager: Camera connection manager
            config: Dictionary of camera configurations
            camera_metrics: Dictionary of camera metrics
            check_interval: Interval in seconds between connectivity checks
            bandwidth_check_interval: Interval in seconds between bandwidth checks
            latency_check_interval: Interval in seconds between latency checks
        """
        self.connection_manager = connection_manager
        self.config = config
        self.camera_metrics = camera_metrics
        
        # Initialize connectivity monitor
        self.connectivity_monitor = ConnectivityMonitor(
            connection_manager=connection_manager,
            config=config,
            camera_metrics=camera_metrics,
            check_interval=check_interval,
            bandwidth_check_interval=bandwidth_check_interval,
            latency_check_interval=latency_check_interval,
        )
        
        # Initialize other monitors as needed
        # self.quality_monitor = QualityMonitor(...)
        # self.scene_change_monitor = SceneChangeMonitor(...)
        
        self.running = False

    def start(self) -> None:
        """Start the health manager."""
        if self.running:
            return
        
        self.running = True
        
        # Start monitors
        self.connectivity_monitor.start()
        # self.quality_monitor.start()
        # self.scene_change_monitor.start()
        
        logger.info("Health manager started")

    def stop(self) -> None:
        """Stop the health manager."""
        if not self.running:
            return
        
        self.running = False
        
        # Stop monitors
        self.connectivity_monitor.stop()
        # self.quality_monitor.stop()
        # self.scene_change_monitor.stop()
        
        logger.info("Health manager stopped")

    def get_camera_health(self, camera_name: str) -> Optional[CameraHealth]:
        """
        Get health data for a specific camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            Optional[CameraHealth]: Camera health data, or None if camera not found
        """
        # Get health data from connectivity monitor
        connectivity_health = self.connectivity_monitor.get_camera_health(camera_name)
        
        if not connectivity_health:
            return None
        
        # Combine health data from all monitors
        # For now, we only have connectivity monitor
        return connectivity_health

    def get_all_camera_health(self) -> Dict[str, CameraHealth]:
        """
        Get health data for all cameras.
        
        Returns:
            Dict[str, CameraHealth]: Dictionary of camera health data
        """
        # Get health data from connectivity monitor
        connectivity_health = self.connectivity_monitor.get_all_camera_health()
        
        # Combine health data from all monitors
        # For now, we only have connectivity monitor
        return connectivity_health

    def reset_camera_health(self, camera_name: str) -> bool:
        """
        Reset health data for a specific camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            bool: True if reset was successful, False otherwise
        """
        # Reset health data in all monitors
        connectivity_reset = self.connectivity_monitor.reset_camera_health(camera_name)
        
        # Return True if any monitor reset successfully
        return connectivity_reset

    def get_overall_health_status(self) -> HealthStatus:
        """
        Get the overall health status for all cameras.
        
        Returns:
            HealthStatus: Overall health status
        """
        # Get health data for all cameras
        camera_health = self.get_all_camera_health()
        
        # Determine the worst health status among all cameras
        worst_status = HealthStatus.HEALTHY
        for health in camera_health.values():
            if health.status == HealthStatus.CRITICAL:
                worst_status = HealthStatus.CRITICAL
                break
            elif health.status == HealthStatus.ERROR and worst_status != HealthStatus.CRITICAL:
                worst_status = HealthStatus.ERROR
            elif health.status == HealthStatus.WARNING and worst_status not in [HealthStatus.CRITICAL, HealthStatus.ERROR]:
                worst_status = HealthStatus.WARNING
            elif health.status == HealthStatus.UNKNOWN and worst_status == HealthStatus.HEALTHY:
                worst_status = HealthStatus.UNKNOWN
        
        return worst_status

    def get_health_summary(self) -> Dict[str, Union[str, Dict[str, int]]]:
        """
        Get a summary of health status for all cameras.
        
        Returns:
            Dict[str, Union[str, Dict[str, int]]]: Health summary
        """
        # Get health data for all cameras
        camera_health = self.get_all_camera_health()
        
        # Count cameras by status
        status_counts = {
            HealthStatus.HEALTHY.value: 0,
            HealthStatus.WARNING.value: 0,
            HealthStatus.ERROR.value: 0,
            HealthStatus.CRITICAL.value: 0,
            HealthStatus.UNKNOWN.value: 0,
        }
        
        for health in camera_health.values():
            status_counts[health.status.value] += 1
        
        # Get overall health status
        overall_status = self.get_overall_health_status()
        
        return {
            "status": overall_status.value,
            "camera_counts": status_counts,
            "total_cameras": len(camera_health),
        }
