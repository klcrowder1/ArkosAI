"""
Integration module for the health module.
"""

import logging
from typing import Dict

from arkos.camera import CameraMetrics
from arkos.camera.connection import CameraConnectionManager
from arkos.config import ArkosConfig, CameraConfig
from arkos.health.service import HealthManager

logger = logging.getLogger(__name__)


def init_health_manager(
    config: ArkosConfig,
    connection_manager: CameraConnectionManager,
    camera_metrics: Dict[str, CameraMetrics],
    check_interval: int = 60,
    bandwidth_check_interval: int = 300,
    latency_check_interval: int = 60,
) -> HealthManager:
    """
    Initialize the health manager.
    
    Args:
        config: Arkos configuration
        connection_manager: Camera connection manager
        camera_metrics: Dictionary of camera metrics
        check_interval: Interval in seconds between connectivity checks
        bandwidth_check_interval: Interval in seconds between bandwidth checks
        latency_check_interval: Interval in seconds between latency checks
        
    Returns:
        HealthManager: Initialized health manager
    """
    # Create a dictionary of camera configurations
    camera_configs = {name: camera for name, camera in config.cameras.items()}
    
    # Create the health manager
    health_manager = HealthManager(
        connection_manager=connection_manager,
        config=camera_configs,
        camera_metrics=camera_metrics,
        check_interval=check_interval,
        bandwidth_check_interval=bandwidth_check_interval,
        latency_check_interval=latency_check_interval,
    )
    
    # Start the health manager
    health_manager.start()
    
    logger.info("Health manager initialized")
    
    return health_manager


def register_health_api(app, health_manager: HealthManager) -> None:
    """
    Register the health API endpoints.
    
    Args:
        app: FastAPI application
        health_manager: Health manager
    """
    from arkos.health.api import create_health_router
    
    # Create the router
    router = create_health_router(health_manager)
    
    # Register the router
    app.include_router(router, prefix="/api/health", tags=["health"])
    
    logger.info("Health API endpoints registered")
