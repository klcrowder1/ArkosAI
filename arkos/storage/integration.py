"""
Integration module for the storage module.
"""

import logging

from arkos.storage.monitor import StorageMonitor

logger = logging.getLogger(__name__)


def register_storage_api(app, storage_monitor: StorageMonitor) -> None:
    """
    Register the storage API endpoints.
    
    Args:
        app: FastAPI application
        storage_monitor: Storage monitor
    """
    from arkos.storage.api import create_storage_router
    
    # Create the router
    router = create_storage_router(storage_monitor)
    
    # Register the router
    app.include_router(router, prefix="/api/storage", tags=["storage"])
    
    logger.info("Storage API endpoints registered")
