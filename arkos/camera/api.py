import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from arkos.api.auth import requires_auth
from arkos.camera import ConnectionError, ConnectionStatus
from arkos.camera.connection import CameraConnectionManager

logger = logging.getLogger(__name__)


class ConnectionStatusResponse(BaseModel):
    """Response model for connection status."""

    status: str
    error: str
    reconnect_count: int
    uptime: float
    last_connect_attempt: float


class ConnectionStatusesResponse(BaseModel):
    """Response model for all camera connection statuses."""

    cameras: Dict[str, ConnectionStatusResponse]


def create_camera_connection_router(connection_manager: CameraConnectionManager) -> APIRouter:
    """
    Create a router for camera connection management API endpoints.
    
    Args:
        connection_manager: Camera connection manager
        
    Returns:
        APIRouter: Router for camera connection management
    """
    router = APIRouter()
    
    @router.get(
        "/status",
        response_model=ConnectionStatusesResponse,
        summary="Get connection status for all cameras",
        description="Returns the connection status for all cameras",
    )
    async def get_all_connection_status(
        user=Depends(requires_auth),
    ) -> ConnectionStatusesResponse:
        """Get connection status for all cameras."""
        statuses = {}
        
        for camera_name in connection_manager.camera_metrics.keys():
            stats = connection_manager.get_connection_stats(camera_name)
            statuses[camera_name] = ConnectionStatusResponse(
                status=stats["status"],
                error=stats["error"],
                reconnect_count=stats["reconnect_count"],
                uptime=stats["uptime"],
                last_connect_attempt=stats["last_connect_attempt"],
            )
            
        return ConnectionStatusesResponse(cameras=statuses)
    
    @router.get(
        "/{camera_name}/status",
        response_model=ConnectionStatusResponse,
        summary="Get connection status for a specific camera",
        description="Returns the connection status for a specific camera",
    )
    async def get_connection_status(
        camera_name: str = Path(..., description="Name of the camera"),
        user=Depends(requires_auth),
    ) -> ConnectionStatusResponse:
        """Get connection status for a specific camera."""
        if camera_name not in connection_manager.camera_metrics:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        stats = connection_manager.get_connection_stats(camera_name)
        
        return ConnectionStatusResponse(
            status=stats["status"],
            error=stats["error"],
            reconnect_count=stats["reconnect_count"],
            uptime=stats["uptime"],
            last_connect_attempt=stats["last_connect_attempt"],
        )
    
    @router.post(
        "/{camera_name}/reset",
        response_model=ConnectionStatusResponse,
        summary="Reset connection for a specific camera",
        description="Resets the connection for a specific camera",
    )
    async def reset_connection(
        camera_name: str = Path(..., description="Name of the camera"),
        user=Depends(requires_auth),
    ) -> ConnectionStatusResponse:
        """Reset connection for a specific camera."""
        if camera_name not in connection_manager.camera_metrics:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        success = connection_manager.reset_connection(camera_name)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to reset connection for camera {camera_name}")
            
        # Get updated status
        stats = connection_manager.get_connection_stats(camera_name)
        
        return ConnectionStatusResponse(
            status=stats["status"],
            error=stats["error"],
            reconnect_count=stats["reconnect_count"],
            uptime=stats["uptime"],
            last_connect_attempt=stats["last_connect_attempt"],
        )
    
    return router
