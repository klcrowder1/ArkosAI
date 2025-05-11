"""
Connectivity monitor for camera health.
"""

import logging
import socket
import subprocess as sp
import threading
import time
from typing import Dict, List, Optional, Tuple, Union

import requests
from requests.exceptions import RequestException

from arkos.camera import CameraMetrics, ConnectionError, ConnectionStatus
from arkos.camera.connection import CameraConnectionManager
from arkos.config import CameraConfig
from arkos.health import (
    CameraHealth,
    HealthCheck,
    HealthMetric,
    HealthMetricType,
    HealthStatus,
)

logger = logging.getLogger(__name__)


class ConnectivityMonitor:
    """
    Monitors camera connectivity, bandwidth, and latency.
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
        Initialize the connectivity monitor.
        
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
        self.check_interval = check_interval
        self.bandwidth_check_interval = bandwidth_check_interval
        self.latency_check_interval = latency_check_interval
        
        self.health_data: Dict[str, CameraHealth] = {}
        self.last_check: Dict[str, float] = {}
        self.last_bandwidth_check: Dict[str, float] = {}
        self.last_latency_check: Dict[str, float] = {}
        
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.running = False

    def start(self) -> None:
        """Start the connectivity monitor."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Initialize health data for each camera
        for camera_name in self.camera_metrics.keys():
            self.health_data[camera_name] = CameraHealth(
                camera_id=camera_name,
                status=HealthStatus.UNKNOWN,
                checks=[
                    HealthCheck(
                        name="connectivity",
                        status=HealthStatus.UNKNOWN,
                        message="Connectivity status unknown",
                        metrics=[],
                        timestamp=time.time(),
                    )
                ],
            )
            self.last_check[camera_name] = 0
            self.last_bandwidth_check[camera_name] = 0
            self.last_latency_check[camera_name] = 0
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="connectivity_monitor",
            daemon=True,
        )
        self.monitor_thread.start()
        
        logger.info(f"Connectivity monitor started for {len(self.health_data)} cameras")

    def stop(self) -> None:
        """Stop the connectivity monitor."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            if self.monitor_thread.is_alive():
                logger.warning("Connectivity monitor thread did not stop gracefully")
        
        self.monitor_thread = None
        logger.info("Connectivity monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self.stop_event.is_set():
            # Check connectivity for each camera
            for camera_name in self.camera_metrics.keys():
                now = time.time()
                
                # Check connectivity
                if now - self.last_check.get(camera_name, 0) >= self.check_interval:
                    self._check_connectivity(camera_name)
                    self.last_check[camera_name] = now
                
                # Check bandwidth
                if now - self.last_bandwidth_check.get(camera_name, 0) >= self.bandwidth_check_interval:
                    self._check_bandwidth(camera_name)
                    self.last_bandwidth_check[camera_name] = now
                
                # Check latency
                if now - self.last_latency_check.get(camera_name, 0) >= self.latency_check_interval:
                    self._check_latency(camera_name)
                    self.last_latency_check[camera_name] = now
            
            # Sleep for a short time to avoid busy waiting
            time.sleep(1)

    def _check_connectivity(self, camera_name: str) -> None:
        """
        Check connectivity for a camera.
        
        Args:
            camera_name: Name of the camera
        """
        if camera_name not in self.camera_metrics:
            return
        
        # Get connection status from connection manager
        status, error = self.connection_manager.get_connection_status(camera_name)
        stats = self.connection_manager.get_connection_stats(camera_name)
        
        # Map connection status to health status
        health_status = HealthStatus.UNKNOWN
        message = ""
        
        if status == ConnectionStatus.CONNECTED.value:
            health_status = HealthStatus.HEALTHY
            message = "Camera is connected"
        elif status == ConnectionStatus.CONNECTING.value:
            health_status = HealthStatus.WARNING
            message = "Camera is connecting"
        elif status == ConnectionStatus.DISCONNECTED.value:
            health_status = HealthStatus.ERROR
            message = "Camera is disconnected"
        elif status == ConnectionStatus.ERROR.value:
            health_status = HealthStatus.CRITICAL
            message = f"Camera connection error: {error}"
        elif status == ConnectionStatus.DISABLED.value:
            health_status = HealthStatus.UNKNOWN
            message = "Camera is disabled"
        
        # Create health metrics
        metrics = [
            HealthMetric(
                name="status",
                value=status,
                type=HealthMetricType.CONNECTIVITY,
                status=health_status,
                timestamp=time.time(),
            ),
            HealthMetric(
                name="error",
                value=error,
                type=HealthMetricType.CONNECTIVITY,
                status=health_status,
                timestamp=time.time(),
            ),
            HealthMetric(
                name="reconnect_count",
                value=stats["reconnect_count"],
                type=HealthMetricType.CONNECTIVITY,
                status=health_status,
                timestamp=time.time(),
            ),
            HealthMetric(
                name="uptime",
                value=stats["uptime"],
                type=HealthMetricType.CONNECTIVITY,
                status=health_status,
                timestamp=time.time(),
            ),
            HealthMetric(
                name="last_connect_attempt",
                value=stats["last_connect_attempt"],
                type=HealthMetricType.CONNECTIVITY,
                status=health_status,
                timestamp=time.time(),
            ),
        ]
        
        # Update health data
        connectivity_check = None
        for check in self.health_data[camera_name].checks:
            if check.name == "connectivity":
                connectivity_check = check
                break
        
        if connectivity_check:
            connectivity_check.status = health_status
            connectivity_check.message = message
            connectivity_check.metrics = metrics
            connectivity_check.timestamp = time.time()
        else:
            self.health_data[camera_name].checks.append(
                HealthCheck(
                    name="connectivity",
                    status=health_status,
                    message=message,
                    metrics=metrics,
                    timestamp=time.time(),
                )
            )
        
        # Update overall camera health status
        self._update_camera_health_status(camera_name)

    def _check_bandwidth(self, camera_name: str) -> None:
        """
        Check bandwidth for a camera.
        
        Args:
            camera_name: Name of the camera
        """
        if camera_name not in self.camera_metrics:
            return
        
        # Get camera metrics
        metrics = self.camera_metrics[camera_name]
        
        # Calculate bandwidth based on camera FPS and frame size
        # This is a simplified calculation and should be replaced with actual bandwidth measurement
        bandwidth = 0.0
        if metrics.camera_fps.value > 0:
            # Assume average frame size of 50KB for a 720p stream
            frame_size_kb = 50
            bandwidth = metrics.camera_fps.value * frame_size_kb * 8 / 1000  # Mbps
        
        # Determine health status based on bandwidth
        health_status = HealthStatus.UNKNOWN
        message = ""
        
        if bandwidth == 0:
            health_status = HealthStatus.UNKNOWN
            message = "Bandwidth unknown"
        elif bandwidth < 1:
            health_status = HealthStatus.WARNING
            message = f"Low bandwidth: {bandwidth:.2f} Mbps"
        else:
            health_status = HealthStatus.HEALTHY
            message = f"Bandwidth: {bandwidth:.2f} Mbps"
        
        # Create health metric
        bandwidth_metric = HealthMetric(
            name="bandwidth",
            value=bandwidth,
            type=HealthMetricType.BANDWIDTH,
            status=health_status,
            timestamp=time.time(),
        )
        
        # Update health data
        bandwidth_check = None
        for check in self.health_data[camera_name].checks:
            if check.name == "bandwidth":
                bandwidth_check = check
                break
        
        if bandwidth_check:
            bandwidth_check.status = health_status
            bandwidth_check.message = message
            bandwidth_check.metrics = [bandwidth_metric]
            bandwidth_check.timestamp = time.time()
        else:
            self.health_data[camera_name].checks.append(
                HealthCheck(
                    name="bandwidth",
                    status=health_status,
                    message=message,
                    metrics=[bandwidth_metric],
                    timestamp=time.time(),
                )
            )
        
        # Update overall camera health status
        self._update_camera_health_status(camera_name)

    def _check_latency(self, camera_name: str) -> None:
        """
        Check latency for a camera.
        
        Args:
            camera_name: Name of the camera
        """
        if camera_name not in self.camera_metrics or camera_name not in self.config:
            return
        
        # Get camera config
        camera_config = self.config[camera_name]
        
        # Get camera metrics
        metrics = self.camera_metrics[camera_name]
        
        # Calculate latency based on frame timestamps
        # This is a simplified calculation and should be replaced with actual latency measurement
        latency = 0.0
        if metrics.last_frame_time.value > 0:
            latency = time.time() - metrics.last_frame_time.value
        
        # Determine health status based on latency
        health_status = HealthStatus.UNKNOWN
        message = ""
        
        if latency == 0:
            health_status = HealthStatus.UNKNOWN
            message = "Latency unknown"
        elif latency > 2.0:
            health_status = HealthStatus.CRITICAL
            message = f"High latency: {latency:.2f} seconds"
        elif latency > 1.0:
            health_status = HealthStatus.ERROR
            message = f"Elevated latency: {latency:.2f} seconds"
        elif latency > 0.5:
            health_status = HealthStatus.WARNING
            message = f"Moderate latency: {latency:.2f} seconds"
        else:
            health_status = HealthStatus.HEALTHY
            message = f"Latency: {latency:.2f} seconds"
        
        # Create health metric
        latency_metric = HealthMetric(
            name="latency",
            value=latency,
            type=HealthMetricType.LATENCY,
            status=health_status,
            timestamp=time.time(),
        )
        
        # Update health data
        latency_check = None
        for check in self.health_data[camera_name].checks:
            if check.name == "latency":
                latency_check = check
                break
        
        if latency_check:
            latency_check.status = health_status
            latency_check.message = message
            latency_check.metrics = [latency_metric]
            latency_check.timestamp = time.time()
        else:
            self.health_data[camera_name].checks.append(
                HealthCheck(
                    name="latency",
                    status=health_status,
                    message=message,
                    metrics=[latency_metric],
                    timestamp=time.time(),
                )
            )
        
        # Update overall camera health status
        self._update_camera_health_status(camera_name)

    def _update_camera_health_status(self, camera_name: str) -> None:
        """
        Update the overall health status for a camera.
        
        Args:
            camera_name: Name of the camera
        """
        if camera_name not in self.health_data:
            return
        
        # Determine the worst health status among all checks
        worst_status = HealthStatus.HEALTHY
        for check in self.health_data[camera_name].checks:
            if check.status == HealthStatus.CRITICAL:
                worst_status = HealthStatus.CRITICAL
                break
            elif check.status == HealthStatus.ERROR and worst_status != HealthStatus.CRITICAL:
                worst_status = HealthStatus.ERROR
            elif check.status == HealthStatus.WARNING and worst_status not in [HealthStatus.CRITICAL, HealthStatus.ERROR]:
                worst_status = HealthStatus.WARNING
            elif check.status == HealthStatus.UNKNOWN and worst_status == HealthStatus.HEALTHY:
                worst_status = HealthStatus.UNKNOWN
        
        # Update camera health status
        self.health_data[camera_name].status = worst_status

    def get_camera_health(self, camera_name: str) -> Optional[CameraHealth]:
        """
        Get health data for a specific camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            Optional[CameraHealth]: Camera health data, or None if camera not found
        """
        return self.health_data.get(camera_name)

    def get_all_camera_health(self) -> Dict[str, CameraHealth]:
        """
        Get health data for all cameras.
        
        Returns:
            Dict[str, CameraHealth]: Dictionary of camera health data
        """
        return self.health_data

    def reset_camera_health(self, camera_name: str) -> bool:
        """
        Reset health data for a specific camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            bool: True if reset was successful, False otherwise
        """
        if camera_name not in self.health_data:
            return False
        
        # Reset health data
        self.health_data[camera_name] = CameraHealth(
            camera_id=camera_name,
            status=HealthStatus.UNKNOWN,
            checks=[
                HealthCheck(
                    name="connectivity",
                    status=HealthStatus.UNKNOWN,
                    message="Connectivity status unknown",
                    metrics=[],
                    timestamp=time.time(),
                )
            ],
        )
        
        # Reset check timestamps
        self.last_check[camera_name] = 0
        self.last_bandwidth_check[camera_name] = 0
        self.last_latency_check[camera_name] = 0
        
        return True
