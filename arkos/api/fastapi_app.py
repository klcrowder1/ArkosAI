"""
FastAPI application for Arkos AI.
"""

import logging
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from arkos.config import ArkosConfig
from arkos.storage import StorageMaintainer, StorageMonitor
from arkos.track.object_processing import TrackedObjectProcessor

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
    app = FastAPI(
        title="Arkos AI API",
        description="API for Arkos AI",
        version="1.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle generic exceptions."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
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
    
    return app
