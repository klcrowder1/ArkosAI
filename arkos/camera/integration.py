import logging
from typing import Dict

from arkos.camera import CameraMetrics
from arkos.camera.connection import CameraConnectionManager
from arkos.config import ArkosConfig, CameraConfig

logger = logging.getLogger(__name__)


def init_camera_connection_manager(
    config: ArkosConfig, camera_metrics: Dict[str, CameraMetrics]
) -> CameraConnectionManager:
    """
    Initialize the camera connection manager.
    
    Args:
        config: Arkos configuration
        camera_metrics: Dictionary of camera metrics
        
    Returns:
        CameraConnectionManager: Initialized camera connection manager
    """
    # Create a dictionary of camera configurations
    camera_configs = {name: camera for name, camera in config.cameras.items()}
    
    # Create the connection manager
    connection_manager = CameraConnectionManager(camera_configs, camera_metrics)
    
    # Start the connection manager
    connection_manager.start()
    
    logger.info("Camera connection manager initialized")
    
    return connection_manager


def register_camera_connection_api(app, connection_manager: CameraConnectionManager) -> None:
    """
    Register the camera connection API endpoints.
    
    Args:
        app: FastAPI application
        connection_manager: Camera connection manager
    """
    from arkos.camera.api import create_camera_connection_router
    
    # Create the router
    router = create_camera_connection_router(connection_manager)
    
    # Register the router
    app.include_router(router, prefix="/api/cameras/connection", tags=["cameras"])
    
    logger.info("Camera connection API endpoints registered")
