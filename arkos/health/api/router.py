"""
API router for the health module.
"""

import logging
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from arkos.api.auth import requires_auth
from arkos.health import CameraHealth, HealthCheck, HealthMetric, HealthStatus
from arkos.health.service import HealthManager

logger = logging.getLogger(__name__)


class HealthMetricResponse(BaseModel):
    """Response model for health metrics."""

    name: str
    value: Union[str, int, float, bool]
    type: str
    status: str
    timestamp: float


class HealthCheckResponse(BaseModel):
    """Response model for health checks."""

    name: str
    status: str
    message: str
    metrics: List[HealthMetricResponse]
    timestamp: float


class CameraHealthResponse(BaseModel):
    """Response model for camera health."""

    camera_id: str
    status: str
    checks: List[HealthCheckResponse]


class AllCameraHealthResponse(BaseModel):
    """Response model for all camera health."""

    cameras: Dict[str, CameraHealthResponse]


class HealthSummaryResponse(BaseModel):
    """Response model for health summary."""

    status: str
    camera_counts: Dict[str, int]
    total_cameras: int


def create_health_router(health_manager: HealthManager) -> APIRouter:
    """
    Create a router for health API endpoints.
    
    Args:
        health_manager: Health manager
        
    Returns:
        APIRouter: Router for health API endpoints
    """
    router = APIRouter()
    
    @router.get(
        "/status",
        response_model=HealthSummaryResponse,
        summary="Get overall health status",
        description="Returns the overall health status for all cameras",
    )
    async def get_health_status(
        user=Depends(requires_auth),
    ) -> HealthSummaryResponse:
        """Get overall health status."""
        summary = health_manager.get_health_summary()
        
        return HealthSummaryResponse(
            status=summary["status"],
            camera_counts=summary["camera_counts"],
            total_cameras=summary["total_cameras"],
        )
    
    @router.get(
        "/cameras",
        response_model=AllCameraHealthResponse,
        summary="Get health status for all cameras",
        description="Returns the health status for all cameras",
    )
    async def get_all_camera_health(
        user=Depends(requires_auth),
    ) -> AllCameraHealthResponse:
        """Get health status for all cameras."""
        camera_health = health_manager.get_all_camera_health()
        
        # Convert to response model
        response_cameras = {}
        for camera_id, health in camera_health.items():
            response_cameras[camera_id] = _convert_camera_health_to_response(health)
            
        return AllCameraHealthResponse(cameras=response_cameras)
    
    @router.get(
        "/cameras/{camera_name}",
        response_model=CameraHealthResponse,
        summary="Get health status for a specific camera",
        description="Returns the health status for a specific camera",
    )
    async def get_camera_health(
        camera_name: str = Path(..., description="Name of the camera"),
        user=Depends(requires_auth),
    ) -> CameraHealthResponse:
        """Get health status for a specific camera."""
        health = health_manager.get_camera_health(camera_name)
        
        if not health:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        return _convert_camera_health_to_response(health)
    
    @router.post(
        "/cameras/{camera_name}/reset",
        response_model=CameraHealthResponse,
        summary="Reset health status for a specific camera",
        description="Resets the health status for a specific camera",
    )
    async def reset_camera_health(
        camera_name: str = Path(..., description="Name of the camera"),
        user=Depends(requires_auth),
    ) -> CameraHealthResponse:
        """Reset health status for a specific camera."""
        success = health_manager.reset_camera_health(camera_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        # Get updated health status
        health = health_manager.get_camera_health(camera_name)
        
        if not health:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        return _convert_camera_health_to_response(health)
    
    return router


def _convert_camera_health_to_response(health: CameraHealth) -> CameraHealthResponse:
    """
    Convert CameraHealth to CameraHealthResponse.
    
    Args:
        health: Camera health
        
    Returns:
        CameraHealthResponse: Camera health response
    """
    checks = []
    for check in health.checks:
        metrics = []
        for metric in check.metrics:
            metrics.append(
                HealthMetricResponse(
                    name=metric.name,
                    value=metric.value,
                    type=metric.type.value,
                    status=metric.status.value,
                    timestamp=metric.timestamp,
                )
            )
            
        checks.append(
            HealthCheckResponse(
                name=check.name,
                status=check.status.value,
                message=check.message,
                metrics=metrics,
                timestamp=check.timestamp,
            )
        )
        
    return CameraHealthResponse(
        camera_id=health.camera_id,
        status=health.status.value,
        checks=checks,
    )
