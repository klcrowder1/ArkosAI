import datetime
import logging
import socket
import subprocess as sp
import threading
import time
from typing import Dict, List, Optional, Tuple, Union

import requests
from requests.exceptions import RequestException

from arkos.camera import CameraMetrics, ConnectionError, ConnectionStatus
from arkos.comms.config_updater import ConfigPublisher
from arkos.config import CameraConfig
from arkos.log import LogPipe

logger = logging.getLogger(__name__)


class CameraConnectionManager:
    """
    Manages camera connections, handles reconnection attempts, and monitors connection status.
    """

    def __init__(self, config: Dict[str, CameraConfig], camera_metrics: Dict[str, CameraMetrics]):
        """
        Initialize the camera connection manager.
        
        Args:
            config: Dictionary of camera configurations
            camera_metrics: Dictionary of camera metrics
        """
        self.config = config
        self.camera_metrics = camera_metrics
        self.connection_threads: Dict[str, threading.Thread] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        self.config_publisher = ConfigPublisher()
        self.logpipes: Dict[str, LogPipe] = {}
        self.last_check: Dict[str, float] = {}
        self.connection_lock = threading.Lock()
        self.running = False

    def start(self) -> None:
        """Start the connection manager."""
        if self.running:
            return
        
        self.running = True
        
        # Start connection threads for each camera
        for camera_name, camera_config in self.config.items():
            if camera_name not in self.camera_metrics:
                logger.warning(f"No metrics found for camera {camera_name}, skipping connection management")
                continue
                
            self.stop_events[camera_name] = threading.Event()
            self.logpipes[camera_name] = LogPipe(f"connection.{camera_name}")
            self.last_check[camera_name] = 0
            
            # Initialize connection status based on camera enabled state
            if not camera_config.enabled:
                self.camera_metrics[camera_name].connection_status.value = ConnectionStatus.DISABLED.value
            else:
                self.camera_metrics[camera_name].connection_status.value = ConnectionStatus.DISCONNECTED.value
            
            # Start connection thread
            self.connection_threads[camera_name] = threading.Thread(
                target=self._manage_connection,
                name=f"connection:{camera_name}",
                args=(camera_name, camera_config, self.camera_metrics[camera_name], self.stop_events[camera_name]),
                daemon=True
            )
            self.connection_threads[camera_name].start()
            
        logger.info(f"Camera connection manager started for {len(self.connection_threads)} cameras")

    def stop(self) -> None:
        """Stop the connection manager."""
        if not self.running:
            return
            
        self.running = False
        
        # Stop all connection threads
        for camera_name, stop_event in self.stop_events.items():
            stop_event.set()
            
        # Wait for all threads to stop
        for camera_name, thread in self.connection_threads.items():
            thread.join(timeout=5)
            if thread.is_alive():
                logger.warning(f"Connection thread for {camera_name} did not stop gracefully")
                
        # Close all logpipes
        for camera_name, logpipe in self.logpipes.items():
            logpipe.close()
            
        self.connection_threads.clear()
        self.stop_events.clear()
        self.logpipes.clear()
        self.last_check.clear()
        
        logger.info("Camera connection manager stopped")

    def _manage_connection(
        self, 
        camera_name: str, 
        camera_config: CameraConfig, 
        camera_metrics: CameraMetrics, 
        stop_event: threading.Event
    ) -> None:
        """
        Manage the connection for a single camera.
        
        Args:
            camera_name: Name of the camera
            camera_config: Camera configuration
            camera_metrics: Camera metrics
            stop_event: Event to signal thread to stop
        """
        logger.debug(f"Starting connection management for camera {camera_name}")
        
        # Initial connection check
        self._check_connection(camera_name, camera_config, camera_metrics)
        
        # Connection management loop
        while not stop_event.is_set():
            # Check if camera is enabled
            if not camera_config.enabled:
                camera_metrics.connection_status.value = ConnectionStatus.DISABLED.value
                camera_metrics.connection_error.value = ConnectionError.NONE.value
                time.sleep(5)
                continue
                
            # Check connection status periodically
            now = time.time()
            if now - self.last_check.get(camera_name, 0) >= camera_config.ffmpeg.retry_interval:
                self._check_connection(camera_name, camera_config, camera_metrics)
                self.last_check[camera_name] = now
                
            # Sleep for a short time to avoid busy waiting
            time.sleep(1)
            
        logger.debug(f"Stopping connection management for camera {camera_name}")

    def _check_connection(
        self, 
        camera_name: str, 
        camera_config: CameraConfig, 
        camera_metrics: CameraMetrics
    ) -> None:
        """
        Check the connection status for a camera.
        
        Args:
            camera_name: Name of the camera
            camera_config: Camera configuration
            camera_metrics: Camera metrics
        """
        # Skip if camera is disabled
        if not camera_config.enabled:
            camera_metrics.connection_status.value = ConnectionStatus.DISABLED.value
            return
            
        # Check if ffmpeg process is running
        if camera_metrics.ffmpeg_pid.value > 0:
            try:
                # Check if process exists
                process = sp.Popen(["ps", "-p", str(camera_metrics.ffmpeg_pid.value)], stdout=sp.PIPE)
                stdout, _ = process.communicate()
                
                # If process exists and we're receiving frames, camera is connected
                if len(stdout.splitlines()) > 1 and camera_metrics.camera_fps.value > 0:
                    # Update connection status if it was previously disconnected
                    if camera_metrics.connection_status.value != ConnectionStatus.CONNECTED.value:
                        logger.info(f"Camera {camera_name} is now connected")
                        camera_metrics.connection_status.value = ConnectionStatus.CONNECTED.value
                        camera_metrics.connection_error.value = ConnectionError.NONE.value
                        camera_metrics.uptime.value = time.time()
                        
                    return
            except Exception as e:
                logger.error(f"Error checking ffmpeg process for {camera_name}: {str(e)}")
        
        # If we get here, the camera is not connected
        # Check if we need to attempt reconnection
        now = time.time()
        if (camera_metrics.connection_status.value != ConnectionStatus.CONNECTING.value or 
            now - camera_metrics.last_connect_attempt.value >= camera_config.ffmpeg.retry_interval):
            
            # Attempt to connect
            self._attempt_connection(camera_name, camera_config, camera_metrics)

    def _attempt_connection(
        self, 
        camera_name: str, 
        camera_config: CameraConfig, 
        camera_metrics: CameraMetrics
    ) -> None:
        """
        Attempt to connect to a camera.
        
        Args:
            camera_name: Name of the camera
            camera_config: Camera configuration
            camera_metrics: Camera metrics
        """
        # Update connection status
        camera_metrics.connection_status.value = ConnectionStatus.CONNECTING.value
        camera_metrics.last_connect_attempt.value = time.time()
        camera_metrics.reconnect_count.value += 1
        
        logger.info(f"Attempting to connect to camera {camera_name} (attempt {camera_metrics.reconnect_count.value})")
        
        # Check if camera is reachable
        error_type = self._check_camera_reachable(camera_config)
        
        if error_type != ConnectionError.NONE:
            # Update connection status with error
            camera_metrics.connection_status.value = ConnectionStatus.ERROR.value
            camera_metrics.connection_error.value = error_type.value
            logger.error(f"Failed to connect to camera {camera_name}: {error_type.name}")
            return
            
        # If camera is reachable, connection will be established by the camera watchdog
        # We just need to ensure the camera is enabled in the config
        with self.connection_lock:
            self.config_publisher.publish(f"config/enabled/{camera_name}", {"enabled": True})
            
        logger.info(f"Connection attempt initiated for camera {camera_name}")

    def _check_camera_reachable(self, camera_config: CameraConfig) -> ConnectionError:
        """
        Check if a camera is reachable.
        
        Args:
            camera_config: Camera configuration
            
        Returns:
            ConnectionError: Type of connection error, or NONE if camera is reachable
        """
        # Check each input
        for input_config in camera_config.ffmpeg.inputs:
            path = input_config.path
            
            # Skip file inputs
            if path.startswith("/") or path.startswith("file:"):
                continue
                
            # Parse URL
            protocol = None
            host = None
            port = None
            
            if path.startswith("rtsp://"):
                protocol = "rtsp"
                url_parts = path[7:].split("/")[0].split("@")[-1].split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 554
            elif path.startswith("http://"):
                protocol = "http"
                url_parts = path[7:].split("/")[0].split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 80
            elif path.startswith("https://"):
                protocol = "https"
                url_parts = path[8:].split("/")[0].split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 443
            
            if not host:
                continue
                
            # Check if host is reachable
            try:
                # First try a simple socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result != 0:
                    return ConnectionError.NETWORK
                    
                # For HTTP/HTTPS, try a request
                if protocol in ["http", "https"]:
                    try:
                        response = requests.head(path, timeout=5)
                        if response.status_code == 401:
                            return ConnectionError.AUTHENTICATION
                        elif response.status_code >= 400:
                            return ConnectionError.UNKNOWN
                    except RequestException:
                        # Socket connection worked but HTTP request failed
                        # This could be due to authentication or other issues
                        pass
                        
                # If we get here, the camera is reachable
                return ConnectionError.NONE
                
            except socket.gaierror:
                return ConnectionError.NETWORK
            except socket.timeout:
                return ConnectionError.TIMEOUT
            except Exception:
                return ConnectionError.UNKNOWN
                
        # If we get here, we couldn't determine if the camera is reachable
        return ConnectionError.NONE

    def get_connection_status(self, camera_name: str) -> Tuple[str, str]:
        """
        Get the connection status for a camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            Tuple[str, str]: Connection status and error type
        """
        if camera_name not in self.camera_metrics:
            return ConnectionStatus.DISCONNECTED.value, ConnectionError.UNKNOWN.value
            
        status = ConnectionStatus(self.camera_metrics[camera_name].connection_status.value).value
        error = ConnectionError(self.camera_metrics[camera_name].connection_error.value).value
        
        return status, error

    def get_connection_stats(self, camera_name: str) -> Dict[str, Union[str, int, float]]:
        """
        Get connection statistics for a camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            Dict[str, Union[str, int, float]]: Connection statistics
        """
        if camera_name not in self.camera_metrics:
            return {
                "status": ConnectionStatus.DISCONNECTED.value,
                "error": ConnectionError.UNKNOWN.value,
                "reconnect_count": 0,
                "uptime": 0,
                "last_connect_attempt": 0,
            }
            
        metrics = self.camera_metrics[camera_name]
        
        return {
            "status": ConnectionStatus(metrics.connection_status.value).value,
            "error": ConnectionError(metrics.connection_error.value).value,
            "reconnect_count": metrics.reconnect_count.value,
            "uptime": time.time() - metrics.uptime.value if metrics.uptime.value > 0 else 0,
            "last_connect_attempt": metrics.last_connect_attempt.value,
        }

    def reset_connection(self, camera_name: str) -> bool:
        """
        Reset the connection for a camera.
        
        Args:
            camera_name: Name of the camera
            
        Returns:
            bool: True if reset was initiated, False otherwise
        """
        if camera_name not in self.camera_metrics or camera_name not in self.config:
            return False
            
        # Update connection status
        self.camera_metrics[camera_name].connection_status.value = ConnectionStatus.DISCONNECTED.value
        self.camera_metrics[camera_name].connection_error.value = ConnectionError.NONE.value
        
        # Force reconnection attempt
        self._attempt_connection(camera_name, self.config[camera_name], self.camera_metrics[camera_name])
        
        return True
