"""
API router for the storage module.
"""

import logging
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from arkos.api.auth import requires_auth
from arkos.storage.monitor import StorageMonitor, StorageHealthStatus

logger = logging.getLogger(__name__)


class StorageMetricResponse(BaseModel):
    """Response model for storage metrics."""

    path: str
    total_space_mb: float
    used_space_mb: float
    free_space_mb: float
    usage_percent: float
    read_speed_mbps: float
    write_speed_mbps: float
    io_errors: int
    health_status: str
    last_updated: str


class CameraStorageMetricResponse(BaseModel):
    """Response model for camera storage metrics."""

    camera: str
    total_size_mb: float
    event_size_mb: float
    non_event_size_mb: float
    bandwidth_mbh: float
    recording_count: int
    event_count: int
    oldest_recording: Optional[str]
    newest_recording: Optional[str]
    last_updated: str


class StorageOverallMetricsResponse(BaseModel):
    """Response model for overall storage metrics."""

    total_space_mb: float
    used_space_mb: float
    free_space_mb: float
    usage_percent: float
    total_camera_size_mb: float
    total_event_size_mb: float
    total_non_event_size_mb: float
    total_bandwidth_mbh: float
    hours_until_full: float
    days_until_full: float
    health_status: str
    last_updated: str


class AllStorageMetricsResponse(BaseModel):
    """Response model for all storage metrics."""

    overall: StorageOverallMetricsResponse
    storage_paths: Dict[str, StorageMetricResponse]
    cameras: Dict[str, CameraStorageMetricResponse]


def create_storage_router(storage_monitor: StorageMonitor) -> APIRouter:
    """
    Create a router for storage API endpoints.
    
    Args:
        storage_monitor: Storage monitor
        
    Returns:
        APIRouter: Router for storage API endpoints
    """
    router = APIRouter()
    
    @router.get(
        "/status",
        response_model=StorageOverallMetricsResponse,
        summary="Get overall storage status",
        description="Returns the overall storage status",
    )
    async def get_storage_status(
        user=Depends(requires_auth),
    ) -> StorageOverallMetricsResponse:
        """Get overall storage status."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get overall metrics
        overall = storage_monitor.get_overall_metrics()
        
        return StorageOverallMetricsResponse(**overall)
    
    @router.get(
        "/metrics",
        response_model=AllStorageMetricsResponse,
        summary="Get all storage metrics",
        description="Returns all storage metrics including overall, storage paths, and cameras",
    )
    async def get_all_storage_metrics(
        user=Depends(requires_auth),
    ) -> AllStorageMetricsResponse:
        """Get all storage metrics."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get all metrics
        overall = storage_monitor.get_overall_metrics()
        storage_metrics = storage_monitor.get_storage_metrics()
        camera_metrics = storage_monitor.get_camera_metrics()
        
        return AllStorageMetricsResponse(
            overall=StorageOverallMetricsResponse(**overall),
            storage_paths={path: StorageMetricResponse(**metrics) for path, metrics in storage_metrics.items()},
            cameras={camera: CameraStorageMetricResponse(**metrics) for camera, metrics in camera_metrics.items()},
        )
    
    @router.get(
        "/paths",
        response_model=Dict[str, StorageMetricResponse],
        summary="Get storage metrics for all paths",
        description="Returns storage metrics for all monitored storage paths",
    )
    async def get_storage_paths_metrics(
        user=Depends(requires_auth),
    ) -> Dict[str, StorageMetricResponse]:
        """Get storage metrics for all paths."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get storage metrics
        storage_metrics = storage_monitor.get_storage_metrics()
        
        return {path: StorageMetricResponse(**metrics) for path, metrics in storage_metrics.items()}
    
    @router.get(
        "/paths/{path}",
        response_model=StorageMetricResponse,
        summary="Get storage metrics for a specific path",
        description="Returns storage metrics for a specific storage path",
    )
    async def get_storage_path_metrics(
        path: str = Path(..., description="Storage path"),
        user=Depends(requires_auth),
    ) -> StorageMetricResponse:
        """Get storage metrics for a specific path."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get storage metrics
        storage_metrics = storage_monitor.get_storage_metrics()
        
        # Find the matching path
        for storage_path, metrics in storage_metrics.items():
            if storage_path.endswith(path):
                return StorageMetricResponse(**metrics)
        
        raise HTTPException(status_code=404, detail=f"Storage path {path} not found")
    
    @router.get(
        "/cameras",
        response_model=Dict[str, CameraStorageMetricResponse],
        summary="Get storage metrics for all cameras",
        description="Returns storage metrics for all cameras",
    )
    async def get_camera_storage_metrics(
        user=Depends(requires_auth),
    ) -> Dict[str, CameraStorageMetricResponse]:
        """Get storage metrics for all cameras."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get camera metrics
        camera_metrics = storage_monitor.get_camera_metrics()
        
        return {camera: CameraStorageMetricResponse(**metrics) for camera, metrics in camera_metrics.items()}
    
    @router.get(
        "/cameras/{camera_name}",
        response_model=CameraStorageMetricResponse,
        summary="Get storage metrics for a specific camera",
        description="Returns storage metrics for a specific camera",
    )
    async def get_camera_storage_metric(
        camera_name: str = Path(..., description="Camera name"),
        user=Depends(requires_auth),
    ) -> CameraStorageMetricResponse:
        """Get storage metrics for a specific camera."""
        # Update metrics to ensure they're current
        storage_monitor.update_metrics()
        
        # Get camera metrics
        camera_metrics = storage_monitor.get_camera_metrics()
        
        if camera_name not in camera_metrics:
            raise HTTPException(status_code=404, detail=f"Camera {camera_name} not found")
            
        return CameraStorageMetricResponse(**camera_metrics[camera_name])
    
    @router.post(
        "/check-io-performance",
        response_model=Dict[str, StorageMetricResponse],
        summary="Run I/O performance check",
        description="Runs I/O performance check on all storage paths",
    )
    async def run_io_performance_check(
        user=Depends(requires_auth),
    ) -> Dict[str, StorageMetricResponse]:
        """Run I/O performance check."""
        # Run I/O performance check
        storage_monitor.check_io_performance()
        
        # Get updated storage metrics
        storage_metrics = storage_monitor.get_storage_metrics()
        
        return {path: StorageMetricResponse(**metrics) for path, metrics in storage_metrics.items()}
    
    return router
