"""
API routes for two-factor authentication.
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional, Any

from arkos.api.auth_enhanced import get_current_user, requires_admin
from arkos.api.auth_2fa import (
    setup_2fa,
    verify_2fa_setup,
    verify_2fa,
    disable_2fa,
    get_2fa_status,
)

router = APIRouter()


class Setup2FAResponse(BaseModel):
    """Response model for 2FA setup."""
    
    secret: str
    qr_code: str
    device_id: str


class Verify2FASetupRequest(BaseModel):
    """Request model for 2FA setup verification."""
    
    device_id: str
    code: str


class Verify2FARequest(BaseModel):
    """Request model for 2FA verification."""
    
    code: str


class Disable2FARequest(BaseModel):
    """Request model for disabling 2FA."""
    
    code: str


@router.post("/setup", response_model=Setup2FAResponse)
async def setup_2fa_endpoint(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Set up two-factor authentication for the current user.
    
    Args:
        request: FastAPI request
        user: Current user
        
    Returns:
        Dict: Setup information including secret and QR code
    """
    return await setup_2fa(request, user["id"])


@router.post("/verify-setup")
async def verify_2fa_setup_endpoint(
    request: Request,
    data: Verify2FASetupRequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Verify and activate a 2FA device.
    
    Args:
        request: FastAPI request
        data: Request data
        user: Current user
        
    Returns:
        Dict: Success message
    """
    return await verify_2fa_setup(request, data.device_id, data.code)


@router.post("/verify")
async def verify_2fa_endpoint(
    request: Request,
    data: Verify2FARequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Verify a 2FA code.
    
    Args:
        request: FastAPI request
        data: Request data
        user: Current user
        
    Returns:
        Dict: Success message
    """
    return await verify_2fa(request, user["id"], data.code)


@router.post("/disable")
async def disable_2fa_endpoint(
    request: Request,
    data: Disable2FARequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Disable 2FA for the current user.
    
    Args:
        request: FastAPI request
        data: Request data
        user: Current user
        
    Returns:
        Dict: Success message
    """
    return await disable_2fa(request, user["id"], data.code)


@router.get("/status")
async def get_2fa_status_endpoint(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get the 2FA status for the current user.
    
    Args:
        request: FastAPI request
        user: Current user
        
    Returns:
        Dict: 2FA status
    """
    return await get_2fa_status(request, user)


@router.post("/admin/disable/{user_id}")
async def admin_disable_2fa_endpoint(
    request: Request,
    user_id: str,
    user: Dict[str, Any] = Depends(requires_admin),
) -> Dict[str, Any]:
    """
    Disable 2FA for a user (admin only).
    
    Args:
        request: FastAPI request
        user_id: User ID
        user: Current user (admin)
        
    Returns:
        Dict: Success message
    """
    from arkos.models.user import User, TOTPDevice
    
    # Get the user
    target_user = User.get_or_none(User.id == user_id)
    
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found"},
        )
    
    # Get the active device
    device = TOTPDevice.get_or_none(
        (TOTPDevice.user == target_user) &
        (TOTPDevice.is_active == True)
    )
    
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Two-factor authentication is not enabled for this user"},
        )
    
    # Deactivate the device
    device.is_active = False
    device.save()
    
    return {
        "message": f"Two-factor authentication has been disabled for user {target_user.username}",
    }
