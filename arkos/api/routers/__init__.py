"""
API routers package for Arkos AI.

This package contains the API routers for the Arkos AI API.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, FastAPI

from arkos.api.version import APIVersion, VersionedAPIRouter
from arkos.config import ArkosConfig

logger = logging.getLogger(__name__)


def register_routers(
    app: FastAPI,
    api_router: VersionedAPIRouter,
    config: ArkosConfig,
) -> None:
    """
    Register all API routers with the FastAPI application.
    
    Args:
        app: FastAPI application
        api_router: Versioned API router
        config: Arkos configuration
    """
    # Import routers
    from arkos.api.routers.auth import create_auth_router
    from arkos.api.routers.cameras import create_cameras_router
    from arkos.api.routers.events import create_events_router
    from arkos.api.routers.health import create_health_router
    from arkos.api.routers.recordings import create_recordings_router
    from arkos.api.routers.storage import create_storage_router
    from arkos.api.routers.system import create_system_router
    
    # Create routers
    auth_router = create_auth_router(config)
    cameras_router = create_cameras_router(config)
    events_router = create_events_router(config)
    health_router = create_health_router(config)
    recordings_router = create_recordings_router(config)
    storage_router = create_storage_router(config)
    system_router = create_system_router(config)
    
    # Register routers with API v1
    api_router.include_router(auth_router, version=APIVersion.V1)
    api_router.include_router(cameras_router, version=APIVersion.V1)
    api_router.include_router(events_router, version=APIVersion.V1)
    api_router.include_router(health_router, version=APIVersion.V1)
    api_router.include_router(recordings_router, version=APIVersion.V1)
    api_router.include_router(storage_router, version=APIVersion.V1)
    api_router.include_router(system_router, version=APIVersion.V1)
    
    # Register routers with API v2 (same routers for now, but could be different in the future)
    api_router.include_router(auth_router, version=APIVersion.V2)
    api_router.include_router(cameras_router, version=APIVersion.V2)
    api_router.include_router(events_router, version=APIVersion.V2)
    api_router.include_router(health_router, version=APIVersion.V2)
    api_router.include_router(recordings_router, version=APIVersion.V2)
    api_router.include_router(storage_router, version=APIVersion.V2)
    api_router.include_router(system_router, version=APIVersion.V2)
    
    logger.info("API routers registered")
