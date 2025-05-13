"""
Two-factor authentication module for Arkos AI API.

This module provides two-factor authentication functionality for the Arkos AI API,
including TOTP (Time-based One-Time Password) support.
"""

import base64
import logging
import os
import time
from typing import Dict, Optional, Tuple, Any

import pyotp
import qrcode
from fastapi import Depends, HTTPException, Request, status
from io import BytesIO

from arkos.api.auth_enhanced import get_current_user
from arkos.api.base import create_error_response
from arkos.models.user import User, TOTPDevice

logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """
    Generate a random secret for TOTP.
    
    Returns:
        str: Base32 encoded secret
    """
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str, issuer: str = "Arkos AI") -> str:
    """
    Get the TOTP URI for QR code generation.
    
    Args:
        secret: TOTP secret
        username: Username
        issuer: Issuer name
        
    Returns:
        str: TOTP URI
    """
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=issuer
    )


def generate_qr_code(uri: str) -> bytes:
    """
    Generate a QR code image from a URI.
    
    Args:
        uri: URI to encode in the QR code
        
    Returns:
        bytes: QR code image data
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify a TOTP code.
    
    Args:
        secret: TOTP secret
        code: TOTP code to verify
        
    Returns:
        bool: True if the code is valid
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


async def setup_2fa(
    request: Request,
    user_id: str,
) -> Dict[str, Any]:
    """
    Set up two-factor authentication for a user.
    
    Args:
        request: FastAPI request
        user_id: User ID
        
    Returns:
        Dict: Setup information including secret and QR code
        
    Raises:
        HTTPException: If the user is not found or 2FA is already enabled
    """
    # Get the user
    user = User.get_or_none(User.id == user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                "user_not_found",
                "User not found",
                None
            ),
        )
    
    # Check if 2FA is already enabled
    existing_device = TOTPDevice.get_or_none(
        (TOTPDevice.user == user) &
        (TOTPDevice.is_active == True)
    )
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "2fa_already_enabled",
                "Two-factor authentication is already enabled for this user",
                None
            ),
        )
    
    # Generate a new secret
    secret = generate_totp_secret()
    
    # Create a new TOTP device
    device = TOTPDevice.create(
        user=user,
        secret=secret,
        name="Default",
        is_active=False,  # Will be activated after verification
    )
    
    # Generate QR code
    uri = get_totp_uri(secret, user.username)
    qr_code = generate_qr_code(uri)
    qr_code_base64 = base64.b64encode(qr_code).decode("utf-8")
    
    return {
        "secret": secret,
        "qr_code": qr_code_base64,
        "device_id": str(device.id),
    }


async def verify_2fa_setup(
    request: Request,
    device_id: str,
    code: str,
) -> Dict[str, Any]:
    """
    Verify and activate a 2FA device.
    
    Args:
        request: FastAPI request
        device_id: Device ID
        code: TOTP code
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If the device is not found or the code is invalid
    """
    # Get the device
    device = TOTPDevice.get_or_none(TOTPDevice.id == device_id)
    
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                "device_not_found",
                "Device not found",
                None
            ),
        )
    
    # Verify the code
    if not verify_totp_code(device.secret, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "invalid_code",
                "Invalid verification code",
                None
            ),
        )
    
    # Activate the device
    device.is_active = True
    device.confirmed_at = time.time()
    device.save()
    
    return {
        "message": "Two-factor authentication has been enabled successfully",
    }


async def verify_2fa(
    request: Request,
    user_id: str,
    code: str,
) -> Dict[str, Any]:
    """
    Verify a 2FA code during login.
    
    Args:
        request: FastAPI request
        user_id: User ID
        code: TOTP code
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If the user is not found, 2FA is not enabled, or the code is invalid
    """
    # Get the user
    user = User.get_or_none(User.id == user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                "user_not_found",
                "User not found",
                None
            ),
        )
    
    # Get the active device
    device = TOTPDevice.get_or_none(
        (TOTPDevice.user == user) &
        (TOTPDevice.is_active == True)
    )
    
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "2fa_not_enabled",
                "Two-factor authentication is not enabled for this user",
                None
            ),
        )
    
    # Verify the code
    if not verify_totp_code(device.secret, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "invalid_code",
                "Invalid verification code",
                None
            ),
        )
    
    # Update last used timestamp
    device.last_used_at = time.time()
    device.save()
    
    return {
        "message": "Two-factor authentication verification successful",
    }


async def disable_2fa(
    request: Request,
    user_id: str,
    code: str,
) -> Dict[str, Any]:
    """
    Disable 2FA for a user.
    
    Args:
        request: FastAPI request
        user_id: User ID
        code: TOTP code for verification
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If the user is not found, 2FA is not enabled, or the code is invalid
    """
    # Get the user
    user = User.get_or_none(User.id == user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                "user_not_found",
                "User not found",
                None
            ),
        )
    
    # Get the active device
    device = TOTPDevice.get_or_none(
        (TOTPDevice.user == user) &
        (TOTPDevice.is_active == True)
    )
    
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "2fa_not_enabled",
                "Two-factor authentication is not enabled for this user",
                None
            ),
        )
    
    # Verify the code
    if not verify_totp_code(device.secret, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                "invalid_code",
                "Invalid verification code",
                None
            ),
        )
    
    # Deactivate the device
    device.is_active = False
    device.save()
    
    return {
        "message": "Two-factor authentication has been disabled successfully",
    }


async def get_2fa_status(
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
    # Get the user
    user_obj = User.get_or_none(User.id == user["id"])
    
    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                "user_not_found",
                "User not found",
                None
            ),
        )
    
    # Get the active device
    device = TOTPDevice.get_or_none(
        (TOTPDevice.user == user_obj) &
        (TOTPDevice.is_active == True)
    )
    
    return {
        "enabled": device is not None,
        "device": device.to_dict() if device else None,
    }
