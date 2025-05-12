"""
Cameras API router for Arkos AI.

This module provides the API router for camera-related endpoints.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from pydantic import BaseModel, Field

from arkos.api.auth_enhanced import requires_read, requires_write, requires_admin
from arkos.api.base import create_api_router, create_error_response, GenericResponse, PaginatedResponse
from arkos.config import ArkosConfig

logger = logging.getLogger(__name__)


# Request and response models
class CameraInfo(BaseModel):
    """Camera information model."""
    
    id: str = Field(..., description="Camera ID")
    name: str = Field(..., description="Camera name")
    enabled: bool = Field(..., description="Whether the camera is enabled")
    url: str = Field(..., description="Camera URL")
    type: str = Field(..., description="Camera type")
    width: int = Field(..., description="Camera width")
    height: int = Field(..., description="Camera height")
    fps: int = Field(..., description="Camera FPS")
    rtsp_url: Optional[str] = Field(None, description="Camera RTSP URL")
    ptz_enabled: bool = Field(False, description="Whether PTZ is enabled")
    audio_enabled: bool = Field(False, description="Whether audio is enabled")
    detect_enabled: bool = Field(True, description="Whether object detection is enabled")
    motion_enabled: bool = Field(True, description="Whether motion detection is enabled")
    recording_enabled: bool = Field(True, description="Whether recording is enabled")
    snapshot_enabled: bool = Field(True, description="Whether snapshots are enabled")
    zones: Dict[str, Any] = Field({}, description="Camera zones")
    objects: List[str] = Field([], description="Objects to detect")


class CameraList(PaginatedResponse):
    """Camera list response model."""
    
    items: List[CameraInfo]


class CameraConnectionStatus(BaseModel):
    """Camera connection status model."""
    
    status: str = Field(..., description="Connection status")
    error: Optional[str] = Field(None, description="Error message")
    reconnect_count: int = Field(0, description="Reconnect count")
    uptime: float = Field(0.0, description="Uptime in seconds")
    last_connect_attempt: float = Field(0.0, description="Last connect attempt timestamp")


class CameraConnectionStatuses(BaseModel):
    """Camera connection statuses model."""
    
    cameras: Dict[str, CameraConnectionStatus]


class CameraCreateRequest(BaseModel):
    """Camera create request model."""
    
    name: str = Field(..., description="Camera name")
    url: str = Field(..., description="Camera URL")
    type: str = Field(..., description="Camera type")
    width: int = Field(..., description="Camera width")
    height: int = Field(..., description="Camera height")
    fps: int = Field(5, description="Camera FPS")
    rtsp_url: Optional[str] = Field(None, description="Camera RTSP URL")
    ptz_enabled: bool = Field(False, description="Whether PTZ is enabled")
    audio_enabled: bool = Field(False, description="Whether audio is enabled")
    detect_enabled: bool = Field(True, description="Whether object detection is enabled")
    motion_enabled: bool = Field(True, description="Whether motion detection is enabled")
    recording_enabled: bool = Field(True, description="Whether recording is enabled")
    snapshot_enabled: bool = Field(True, description="Whether snapshots are enabled")
    zones: Dict[str, Any] = Field({}, description="Camera zones")
    objects: List[str] = Field([], description="Objects to detect")


class CameraUpdateRequest(BaseModel):
    """Camera update request model."""
    
    name: Optional[str] = Field(None, description="Camera name")
    url: Optional[str] = Field(None, description="Camera URL")
    type: Optional[str] = Field(None, description="Camera type")
    width: Optional[int] = Field(None, description="Camera width")
    height: Optional[int] = Field(None, description="Camera height")
    fps: Optional[int] = Field(None, description="Camera FPS")
    rtsp_url: Optional[str] = Field(None, description="Camera RTSP URL")
    ptz_enabled: Optional[bool] = Field(None, description="Whether PTZ is enabled")
    audio_enabled: Optional[bool] = Field(None, description="Whether audio is enabled")
    detect_enabled: Optional[bool] = Field(None, description="Whether object detection is enabled")
    motion_enabled: Optional[bool] = Field(None, description="Whether motion detection is enabled")
    recording_enabled: Optional[bool] = Field(None, description="Whether recording is enabled")
    snapshot_enabled: Optional[bool] = Field(None, description="Whether snapshots are enabled")
    zones: Optional[Dict[str, Any]] = Field(None, description="Camera zones")
    objects: Optional[List[str]] = Field(None, description="Objects to detect")


def create_cameras_router(config: ArkosConfig) -> APIRouter:
    """
    Create a router for camera-related endpoints.
    
    Args:
        config: Arkos configuration
        
    Returns:
        APIRouter: Router for camera-related endpoints
    """
    router = create_api_router("/cameras", ["cameras"])
    
    @router.get(
        "",
        response_model=CameraList,
        summary="List cameras",
        description="Returns a list of all cameras",
    )
    async def list_cameras(
        request: Request,
        limit: int = Query(100, description="Maximum number of cameras to return"),
        offset: int = Query(0, description="Number of cameras to skip"),
        user=Depends(requires_read),
    ) -> CameraList:
        """List all cameras."""
        # Get cameras from config
        cameras = []
        for name, camera in request.app.state.config.cameras.items():
            cameras.append(
                CameraInfo(
                    id=name,
                    name=name,
                    enabled=camera.enabled,
                    url=camera.ffmpeg.inputs[0].path,
                    type=camera.ffmpeg.inputs[0].input_type,
                    width=camera.detect.width,
                    height=camera.detect.height,
                    fps=camera.detect.fps,
                    rtsp_url=camera.ffmpeg.inputs[0].path if camera.ffmpeg.inputs[0].input_type == "rtsp" else None,
                    ptz_enabled=camera.onvif.enabled,
                    audio_enabled=camera.audio.enabled_in_config,
                    detect_enabled=camera.detect.enabled,
                    motion_enabled=camera.motion.enabled,
                    recording_enabled=camera.record.enabled,
                    snapshot_enabled=camera.snapshots.enabled,
                    zones=camera.zones,
                    objects=list(camera.objects.track),
                )
            )
        
        # Apply pagination
        total = len(cameras)
        cameras = cameras[offset:offset + limit]
        
        return CameraList(
            items=cameras,
            pagination={
                "total": total,
                "limit": limit,
                "offset": offset,
                "next": f"/api/v1/cameras?limit={limit}&offset={offset + limit}" if offset + limit < total else None,
            },
        )
    
    @router.get(
        "/{camera_id}",
        response_model=CameraInfo,
        summary="Get camera",
        description="Returns details for a specific camera",
    )
    async def get_camera(
        request: Request,
        camera_id: str = Path(..., description="Camera ID"),
        user=Depends(requires_read),
    ) -> CameraInfo:
        """Get a specific camera."""
        # Get camera from config
        if camera_id not in request.app.state.config.cameras:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "camera_not_found",
                    f"Camera {camera_id} not found",
                    None,
                ),
            )
        
        camera = request.app.state.config.cameras[camera_id]
        
        return CameraInfo(
            id=camera_id,
            name=camera_id,
            enabled=camera.enabled,
            url=camera.ffmpeg.inputs[0].path,
            type=camera.ffmpeg.inputs[0].input_type,
            width=camera.detect.width,
            height=camera.detect.height,
            fps=camera.detect.fps,
            rtsp_url=camera.ffmpeg.inputs[0].path if camera.ffmpeg.inputs[0].input_type == "rtsp" else None,
            ptz_enabled=camera.onvif.enabled,
            audio_enabled=camera.audio.enabled_in_config,
            detect_enabled=camera.detect.enabled,
            motion_enabled=camera.motion.enabled,
            recording_enabled=camera.record.enabled,
            snapshot_enabled=camera.snapshots.enabled,
            zones=camera.zones,
            objects=list(camera.objects.track),
        )
    
    @router.post(
        "",
        response_model=CameraInfo,
        summary="Create camera",
        description="Creates a new camera",
        status_code=201,
    )
    async def create_camera(
        request: Request,
        camera: CameraCreateRequest,
        user=Depends(requires_admin),
    ) -> CameraInfo:
        """Create a new camera."""
        # Check if camera already exists
        if camera.name in request.app.state.config.cameras:
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    "camera_already_exists",
                    f"Camera {camera.name} already exists",
                    None,
                ),
            )
        
        # TODO: Implement camera creation
        # This would involve updating the config file and restarting the camera processes
        
        return CameraInfo(
            id=camera.name,
            name=camera.name,
            enabled=True,
            url=camera.url,
            type=camera.type,
            width=camera.width,
            height=camera.height,
            fps=camera.fps,
            rtsp_url=camera.rtsp_url,
            ptz_enabled=camera.ptz_enabled,
            audio_enabled=camera.audio_enabled,
            detect_enabled=camera.detect_enabled,
            motion_enabled=camera.motion_enabled,
            recording_enabled=camera.recording_enabled,
            snapshot_enabled=camera.snapshot_enabled,
            zones=camera.zones,
            objects=camera.objects,
        )
    
    @router.put(
        "/{camera_id}",
        response_model=CameraInfo,
        summary="Update camera",
        description="Updates an existing camera",
    )
    async def update_camera(
        request: Request,
        camera_id: str = Path(..., description="Camera ID"),
        camera: CameraUpdateRequest = None,
        user=Depends(requires_write),
    ) -> CameraInfo:
        """Update an existing camera."""
        # Check if camera exists
        if camera_id not in request.app.state.config.cameras:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "camera_not_found",
                    f"Camera {camera_id} not found",
                    None,
                ),
            )
        
        # TODO: Implement camera update
        # This would involve updating the config file and restarting the camera processes
        
        # Get the current camera config
        current_camera = request.app.state.config.cameras[camera_id]
        
        # Return the updated camera info
        return CameraInfo(
            id=camera_id,
            name=camera_id,
            enabled=current_camera.enabled,
            url=current_camera.ffmpeg.inputs[0].path,
            type=current_camera.ffmpeg.inputs[0].input_type,
            width=current_camera.detect.width,
            height=current_camera.detect.height,
            fps=current_camera.detect.fps,
            rtsp_url=current_camera.ffmpeg.inputs[0].path if current_camera.ffmpeg.inputs[0].input_type == "rtsp" else None,
            ptz_enabled=current_camera.onvif.enabled,
            audio_enabled=current_camera.audio.enabled_in_config,
            detect_enabled=current_camera.detect.enabled,
            motion_enabled=current_camera.motion.enabled,
            recording_enabled=current_camera.record.enabled,
            snapshot_enabled=current_camera.snapshots.enabled,
            zones=current_camera.zones,
            objects=list(current_camera.objects.track),
        )
    
    @router.delete(
        "/{camera_id}",
        response_model=GenericResponse,
        summary="Delete camera",
        description="Deletes an existing camera",
    )
    async def delete_camera(
        request: Request,
        camera_id: str = Path(..., description="Camera ID"),
        user=Depends(requires_admin),
    ) -> GenericResponse:
        """Delete an existing camera."""
        # Check if camera exists
        if camera_id not in request.app.state.config.cameras:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "camera_not_found",
                    f"Camera {camera_id} not found",
                    None,
                ),
            )
        
        # TODO: Implement camera deletion
        # This would involve updating the config file and stopping the camera processes
        
        return GenericResponse(
            success=True,
            message=f"Camera {camera_id} deleted",
        )
    
    @router.get(
        "/connection/status",
        response_model=CameraConnectionStatuses,
        summary="Get connection status for all cameras",
        description="Returns the connection status for all cameras",
    )
    async def get_all_connection_status(
        request: Request,
        user=Depends(requires_read),
    ) -> CameraConnectionStatuses:
        """Get connection status for all cameras."""
        # Get connection manager
        connection_manager = request.app.state.camera_connection_manager
        
        # Get connection status for all cameras
        statuses = {}
        for camera_name in connection_manager.camera_metrics.keys():
            stats = connection_manager.get_connection_stats(camera_name)
            statuses[camera_name] = CameraConnectionStatus(
                status=stats["status"],
                error=stats["error"],
                reconnect_count=stats["reconnect_count"],
                uptime=stats["uptime"],
                last_connect_attempt=stats["last_connect_attempt"],
            )
        
        return CameraConnectionStatuses(cameras=statuses)
    
    @router.get(
        "/{camera_id}/connection/status",
        response_model=CameraConnectionStatus,
        summary="Get connection status for a specific camera",
        description="Returns the connection status for a specific camera",
    )
    async def get_connection_status(
        request: Request,
        camera_id: str = Path(..., description="Camera ID"),
        user=Depends(requires_read),
    ) -> CameraConnectionStatus:
        """Get connection status for a specific camera."""
        # Get connection manager
        connection_manager = request.app.state.camera_connection_manager
        
        # Check if camera exists
        if camera_id not in connection_manager.camera_metrics:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "camera_not_found",
                    f"Camera {camera_id} not found",
                    None,
                ),
            )
        
        # Get connection status
        stats = connection_manager.get_connection_stats(camera_id)
        
        return CameraConnectionStatus(
            status=stats["status"],
            error=stats["error"],
            reconnect_count=stats["reconnect_count"],
            uptime=stats["uptime"],
            last_connect_attempt=stats["last_connect_attempt"],
        )
    
    @router.post(
        "/{camera_id}/connection/reset",
        response_model=CameraConnectionStatus,
        summary="Reset connection for a specific camera",
        description="Resets the connection for a specific camera",
    )
    async def reset_connection(
        request: Request,
        camera_id: str = Path(..., description="Camera ID"),
        user=Depends(requires_write),
    ) -> CameraConnectionStatus:
        """Reset connection for a specific camera."""
        # Get connection manager
        connection_manager = request.app.state.camera_connection_manager
        
        # Check if camera exists
        if camera_id not in connection_manager.camera_metrics:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "camera_not_found",
                    f"Camera {camera_id} not found",
                    None,
                ),
            )
        
        # Reset connection
        success = connection_manager.reset_connection(camera_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    "reset_failed",
                    f"Failed to reset connection for camera {camera_id}",
                    None,
                ),
            )
        
        # Get updated connection status
        stats = connection_manager.get_connection_stats(camera_id)
        
        return CameraConnectionStatus(
            status=stats["status"],
            error=stats["error"],
            reconnect_count=stats["reconnect_count"],
            uptime=stats["uptime"],
            last_connect_attempt=stats["last_connect_attempt"],
        )
    
    return router
