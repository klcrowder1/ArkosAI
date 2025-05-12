"""
Integration module for the storage module.
"""

import logging
import multiprocessing as mp

from arkos.config import ArkosConfig
from arkos.storage.monitor import StorageMonitor
from arkos.storage.backup import BackupManager
from arkos.storage.recovery import RecoveryManager

logger = logging.getLogger(__name__)


def register_storage_api(app, storage_monitor: StorageMonitor, config: ArkosConfig, notification_manager=None) -> None:
    """
    Register the storage API endpoints.
    
    Args:
        app: FastAPI application
        storage_monitor: Storage monitor
        config: Arkos configuration
        notification_manager: Notification manager
    """
    from arkos.storage.api import create_storage_router
    from arkos.storage.api.backup_router import create_backup_router
    
    # Create the storage router
    storage_router = create_storage_router(storage_monitor)
    
    # Register the storage router
    app.include_router(storage_router, prefix="/api/storage", tags=["storage"])
    
    # Initialize backup and recovery managers
    stop_event = mp.Event()
    backup_manager = BackupManager(config, stop_event, notification_manager)
    recovery_manager = RecoveryManager(config, backup_manager, notification_manager)
    
    # Create the backup router
    backup_router = create_backup_router(backup_manager, recovery_manager)
    
    # Register the backup router
    app.include_router(backup_router, prefix="/api/storage/backup", tags=["backup"])
    
    logger.info("Storage API endpoints registered")
