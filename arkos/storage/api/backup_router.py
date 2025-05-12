"""
API router for the backup and recovery system.
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, BackgroundTasks
from pydantic import BaseModel, Field

from arkos.api.auth import requires_auth
from arkos.storage.backup import (
    BackupManager, 
    BackupDestination, 
    BackupDestinationType, 
    BackupContentType, 
    BackupStatus
)
from arkos.storage.recovery import RecoveryManager

logger = logging.getLogger(__name__)


class BackupDestinationResponse(BaseModel):
    """Response model for backup destination."""

    name: str
    path: str
    destination_type: str
    retention_days: int
    max_backups: int


class BackupResponse(BaseModel):
    """Response model for backup."""

    id: str
    name: str
    destination: str
    content_types: List[str]
    created_at: datetime
    status: str
    size_mb: float
    filename: str


class BackupCreateRequest(BaseModel):
    """Request model for creating a backup."""

    name: str = Field(..., description="Name of the backup")
    destination: str = Field(..., description="Name of the destination")
    content_types: List[BackupContentType] = Field(
        default=[BackupContentType.ALL], 
        description="Content types to backup"
    )


class BackupRestoreRequest(BaseModel):
    """Request model for restoring a backup."""

    content_types: Optional[List[BackupContentType]] = Field(
        default=None, 
        description="Content types to restore, or None for all"
    )
    restore_path: Optional[str] = Field(
        default=None, 
        description="Path to restore to, or None for default"
    )


class BackupVerificationResponse(BaseModel):
    """Response model for backup verification."""

    success: bool
    errors: List[str]
    verified_files: int
    total_files: int
    verified_size: int
    total_size: int


def create_backup_router(
    backup_manager: BackupManager, 
    recovery_manager: RecoveryManager
) -> APIRouter:
    """
    Create a router for backup and recovery API endpoints.
    
    Args:
        backup_manager: Backup manager
        recovery_manager: Recovery manager
        
    Returns:
        APIRouter: Router for backup and recovery API endpoints
    """
    router = APIRouter()
    
    @router.get(
        "/destinations",
        response_model=List[BackupDestinationResponse],
        summary="Get all backup destinations",
        description="Returns all configured backup destinations",
    )
    async def get_backup_destinations(
        user=Depends(requires_auth),
    ) -> List[BackupDestinationResponse]:
        """Get all backup destinations."""
        destinations = []
        
        for name, destination in backup_manager.destinations.items():
            destinations.append(
                BackupDestinationResponse(
                    name=name,
                    path=destination.path,
                    destination_type=destination.destination_type.value,
                    retention_days=destination.retention_days,
                    max_backups=destination.max_backups,
                )
            )
        
        return destinations
    
    @router.get(
        "/destinations/{name}",
        response_model=BackupDestinationResponse,
        summary="Get a backup destination",
        description="Returns a specific backup destination",
    )
    async def get_backup_destination(
        name: str = Path(..., description="Name of the destination"),
        user=Depends(requires_auth),
    ) -> BackupDestinationResponse:
        """Get a backup destination."""
        if name not in backup_manager.destinations:
            raise HTTPException(status_code=404, detail=f"Backup destination {name} not found")
        
        destination = backup_manager.destinations[name]
        
        return BackupDestinationResponse(
            name=name,
            path=destination.path,
            destination_type=destination.destination_type.value,
            retention_days=destination.retention_days,
            max_backups=destination.max_backups,
        )
    
    @router.get(
        "/backups",
        response_model=Dict[str, List[BackupResponse]],
        summary="Get all backups",
        description="Returns all backups from all destinations",
    )
    async def get_backups(
        user=Depends(requires_auth),
    ) -> Dict[str, List[BackupResponse]]:
        """Get all backups."""
        backups_by_destination = {}
        
        for name, destination in backup_manager.destinations.items():
            backups = []
            
            for backup in destination.list_backups():
                backups.append(
                    BackupResponse(
                        id=backup.get("id", ""),
                        name=backup.get("name", ""),
                        destination=name,
                        content_types=backup.get("content_types", []),
                        created_at=datetime.fromtimestamp(backup.get("created_at", 0)),
                        status=backup.get("status", BackupStatus.COMPLETED.value),
                        size_mb=backup.get("size_mb", 0),
                        filename=backup.get("filename", ""),
                    )
                )
            
            backups_by_destination[name] = backups
        
        return backups_by_destination
    
    @router.post(
        "/backups",
        response_model=BackupResponse,
        summary="Create a backup",
        description="Creates a new backup",
    )
    async def create_backup(
        request: BackupCreateRequest,
        background_tasks: BackgroundTasks,
        user=Depends(requires_auth),
    ) -> BackupResponse:
        """Create a backup."""
        if request.destination not in backup_manager.destinations:
            raise HTTPException(status_code=404, detail=f"Backup destination {request.destination} not found")
        
        # Create backup in background
        backup_id = backup_manager.create_backup_id()
        backup_info = {
            "id": backup_id,
            "name": request.name,
            "destination": request.destination,
            "content_types": [ct.value for ct in request.content_types],
            "created_at": datetime.now().timestamp(),
            "status": BackupStatus.PENDING.value,
            "size_mb": 0,
            "filename": f"backup_{backup_id}.tar.gz",
        }
        
        # Add to backup history
        backup_manager.backup_history.append(backup_info)
        
        # Start backup in background
        background_tasks.add_task(
            backup_manager.create_backup,
            backup_id=backup_id,
            name=request.name,
            destination_name=request.destination,
            content_types=request.content_types,
        )
        
        return BackupResponse(
            id=backup_id,
            name=request.name,
            destination=request.destination,
            content_types=[ct.value for ct in request.content_types],
            created_at=datetime.fromtimestamp(backup_info["created_at"]),
            status=backup_info["status"],
            size_mb=backup_info["size_mb"],
            filename=backup_info["filename"],
        )
    
    @router.get(
        "/backups/{backup_id}",
        response_model=BackupResponse,
        summary="Get a backup",
        description="Returns a specific backup",
    )
    async def get_backup(
        backup_id: str = Path(..., description="ID of the backup"),
        user=Depends(requires_auth),
    ) -> BackupResponse:
        """Get a backup."""
        backup_details = recovery_manager.get_backup_details(backup_id)
        
        if not backup_details:
            # Check backup history
            for backup in backup_manager.backup_history:
                if backup.get("id") == backup_id:
                    return BackupResponse(
                        id=backup.get("id", ""),
                        name=backup.get("name", ""),
                        destination=backup.get("destination", ""),
                        content_types=backup.get("content_types", []),
                        created_at=datetime.fromtimestamp(backup.get("created_at", 0)),
                        status=backup.get("status", BackupStatus.PENDING.value),
                        size_mb=backup.get("size_mb", 0),
                        filename=backup.get("filename", ""),
                    )
            
            raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found")
        
        backup, destination_name = backup_details
        
        return BackupResponse(
            id=backup.get("id", ""),
            name=backup.get("name", ""),
            destination=destination_name,
            content_types=backup.get("content_types", []),
            created_at=datetime.fromtimestamp(backup.get("created_at", 0)),
            status=backup.get("status", BackupStatus.COMPLETED.value),
            size_mb=backup.get("size_mb", 0),
            filename=backup.get("filename", ""),
        )
    
    @router.delete(
        "/backups/{backup_id}",
        response_model=dict,
        summary="Delete a backup",
        description="Deletes a specific backup",
    )
    async def delete_backup(
        backup_id: str = Path(..., description="ID of the backup"),
        user=Depends(requires_auth),
    ) -> dict:
        """Delete a backup."""
        backup_details = recovery_manager.get_backup_details(backup_id)
        
        if not backup_details:
            raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found")
        
        backup, destination_name = backup_details
        destination = backup_manager.destinations[destination_name]
        
        if not destination.delete_backup(backup_id):
            raise HTTPException(status_code=500, detail=f"Failed to delete backup {backup_id}")
        
        # Remove from backup history
        backup_manager.backup_history = [b for b in backup_manager.backup_history if b.get("id") != backup_id]
        
        return {"message": f"Backup {backup_id} deleted successfully"}
    
    @router.post(
        "/backups/{backup_id}/restore",
        response_model=dict,
        summary="Restore a backup",
        description="Restores a specific backup",
    )
    async def restore_backup(
        backup_id: str = Path(..., description="ID of the backup"),
        request: BackupRestoreRequest = None,
        background_tasks: BackgroundTasks = None,
        user=Depends(requires_auth),
    ) -> dict:
        """Restore a backup."""
        backup_details = recovery_manager.get_backup_details(backup_id)
        
        if not backup_details:
            raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found")
        
        # Start restore in background
        background_tasks.add_task(
            recovery_manager.restore_backup,
            backup_id=backup_id,
            content_types=request.content_types,
            restore_path=request.restore_path,
        )
        
        return {"message": f"Backup {backup_id} restore started"}
    
    @router.post(
        "/backups/{backup_id}/verify",
        response_model=BackupVerificationResponse,
        summary="Verify a backup",
        description="Verifies the integrity of a specific backup",
    )
    async def verify_backup(
        backup_id: str = Path(..., description="ID of the backup"),
        user=Depends(requires_auth),
    ) -> BackupVerificationResponse:
        """Verify a backup."""
        backup_details = recovery_manager.get_backup_details(backup_id)
        
        if not backup_details:
            raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found")
        
        # Verify backup
        is_valid = recovery_manager.verify_backup_integrity(backup_id)
        
        if not is_valid:
            return BackupVerificationResponse(
                success=False,
                errors=["Backup verification failed"],
                verified_files=0,
                total_files=0,
                verified_size=0,
                total_size=0,
            )
        
        return BackupVerificationResponse(
            success=True,
            errors=[],
            verified_files=1,
            total_files=1,
            verified_size=1,
            total_size=1,
        )
    
    return router
