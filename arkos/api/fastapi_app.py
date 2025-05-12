"""
FastAPI application for Arkos AI.

This module provides the main FastAPI application for Arkos AI, including
API versioning, authentication, rate limiting, and documentation.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from arkos.api.base import create_error_response
from arkos.api.docs import setup_api_docs, generate_openapi_spec
from arkos.api.rate_limit import setup_rate_limiting
from arkos.api.version import APIVersion, VersionedAPIRouter, register_api_versions
from arkos.config import ArkosConfig
from arkos.storage import StorageMaintainer, StorageMonitor
from arkos.track.object_processing import TrackedObjectProcessor
from arkos.version import VERSION

logger = logging.getLogger(__name__)


def create_fastapi_app(
    config: ArkosConfig,
    db,
    embeddings,
    detected_frames_processor: TrackedObjectProcessor,
    storage_maintainer: StorageMaintainer,
    onvif_controller,
    stats_emitter,
    event_metadata_updater,
    storage_monitor: Optional[StorageMonitor] = None,
) -> FastAPI:
    """
    Create a FastAPI application.
    
    Args:
        config: Arkos configuration
        db: Database connection
        embeddings: Embeddings context
        detected_frames_processor: Tracked object processor
        storage_maintainer: Storage maintainer
        onvif_controller: ONVIF controller
        stats_emitter: Stats emitter
        event_metadata_updater: Event metadata updater
        storage_monitor: Storage monitor
        
    Returns:
        FastAPI: FastAPI application
    """
    # Create the FastAPI application
    app = FastAPI(
        title="Arkos AI API",
        description="API for Arkos AI",
        version=VERSION,
        docs_url=None,  # Disable default docs
        redoc_url=None,  # Disable default redoc
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Set up rate limiting
    setup_rate_limiting(
        app,
        rate=config.api.rate_limit.rate,
        per=config.api.rate_limit.per,
        burst=config.api.rate_limit.burst,
        exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"],
    )
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle generic exceptions."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                "internal_server_error",
                "Internal server error",
                {"detail": str(exc)},
            ),
        )
    
    # Add dependencies
    app.state.config = config
    app.state.db = db
    app.state.embeddings = embeddings
    app.state.detected_frames_processor = detected_frames_processor
    app.state.storage_maintainer = storage_maintainer
    app.state.onvif_controller = onvif_controller
    app.state.stats_emitter = stats_emitter
    app.state.event_metadata_updater = event_metadata_updater
    app.state.storage_monitor = storage_monitor
    
    # Add static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}
    
    # Set up API documentation
    setup_api_docs(
        app,
        title="Arkos AI API",
        description="API for Arkos AI",
        version=VERSION,
    )
    
    # Create a versioned API router
    api_router = VersionedAPIRouter()
    
    # Register API routers
    from arkos.api.routers import register_routers
    register_routers(app, api_router, config)
    
    # Register API versions
    register_api_versions(app, api_router)
    
    # Generate OpenAPI specification
    generate_openapi_spec(app, "docs/static/arkos-api.json")
    
    return app
