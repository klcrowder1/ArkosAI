"""
Health module for Arkos AI.

This module provides comprehensive camera health monitoring capabilities,
ensuring that cameras are functioning properly and providing high-quality video feeds.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status enum."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthMetricType(str, Enum):
    """Health metric type enum."""

    CONNECTIVITY = "connectivity"
    BANDWIDTH = "bandwidth"
    LATENCY = "latency"
    DIRTY_LENS = "dirty_lens"
    SCENE_CHANGE = "scene_change"
    QUALITY = "quality"


class HealthMetric:
    """Health metric class."""

    def __init__(
        self,
        name: str,
        value: Union[str, int, float, bool],
        type: HealthMetricType,
        status: HealthStatus = HealthStatus.UNKNOWN,
        timestamp: Optional[float] = None,
    ):
        """
        Initialize a health metric.
        
        Args:
            name: Name of the metric
            value: Value of the metric
            type: Type of the metric
            status: Status of the metric
            timestamp: Timestamp of the metric
        """
        self.name = name
        self.value = value
        self.type = type
        self.status = status
        self.timestamp = timestamp or 0.0

    def to_dict(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Convert the health metric to a dictionary.
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary representation of the health metric
        """
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type.value,
            "status": self.status.value,
            "timestamp": self.timestamp,
        }


class HealthCheck:
    """Health check class."""

    def __init__(
        self,
        name: str,
        status: HealthStatus = HealthStatus.UNKNOWN,
        message: str = "",
        metrics: Optional[List[HealthMetric]] = None,
        timestamp: Optional[float] = None,
    ):
        """
        Initialize a health check.
        
        Args:
            name: Name of the health check
            status: Status of the health check
            message: Message for the health check
            metrics: List of metrics for the health check
            timestamp: Timestamp of the health check
        """
        self.name = name
        self.status = status
        self.message = message
        self.metrics = metrics or []
        self.timestamp = timestamp or 0.0

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[Dict[str, Union[str, int, float, bool]]]]]:
        """
        Convert the health check to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the health check
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "timestamp": self.timestamp,
        }


class CameraHealth:
    """Camera health class."""

    def __init__(
        self,
        camera_id: str,
        status: HealthStatus = HealthStatus.UNKNOWN,
        checks: Optional[List[HealthCheck]] = None,
    ):
        """
        Initialize camera health.
        
        Args:
            camera_id: Camera ID
            status: Overall health status
            checks: List of health checks
        """
        self.camera_id = camera_id
        self.status = status
        self.checks = checks or []

    def to_dict(self) -> Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool, List[Dict[str, Union[str, int, float, bool]]]]]]]]:
        """
        Convert the camera health to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the camera health
        """
        return {
            "camera_id": self.camera_id,
            "status": self.status.value,
            "checks": [check.to_dict() for check in self.checks],
        }


# Import submodules
from arkos.health.connectivity import ConnectivityMonitor
from arkos.health.service import HealthManager

__all__ = [
    "HealthStatus",
    "HealthMetricType",
    "HealthMetric",
    "HealthCheck",
    "CameraHealth",
    "ConnectivityMonitor",
    "HealthManager",
]
