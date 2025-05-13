"""
API routes for authentication.
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional, Any

from arkos.api.auth import verify_password
from arkos.api.auth_enhanced import create_session
from arkos.models.user import User, TOTPDevice

router = APIRouter()


class LoginRequest(BaseModel):
    """Request model for login."""
    
    user: str
    password: str


class LoginResponse(BaseModel):
    """Response model for login."""
    
    message: str
    requires_2fa: bool = False
    user_id: Optional[str] = None


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
) -> Dict[str, Any]:
    """
    Login endpoint.
    
    Args:
        request: FastAPI request
        response: FastAPI response
        data: Login data
        
    Returns:
        Dict: Login response
    """
    # Get the user
    user = User.get_or_none(User.username == data.user)
    
    # Check if the user exists and the password is correct
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid username or password"},
        )
    
    # Check if 2FA is enabled for the user
    totp_device = TOTPDevice.get_or_none(
        (TOTPDevice.user == user) &
        (TOTPDevice.is_active == True)
    )
    
    if totp_device:
        # 2FA is enabled, return a response indicating that 2FA is required
        return {
            "message": "Two-factor authentication required",
            "requires_2fa": True,
            "user_id": str(user.id),
        }
    
    # No 2FA required, create a session
    session = create_session(user, request, request.app.state.config.auth)
    
    # Set the session cookie
    response.set_cookie(
        key="session",
        value=session.token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=request.app.state.config.auth.jwt.access_token_expire_delta.total_seconds(),
    )
    
    return {
        "message": "Login successful",
        "requires_2fa": False,
    }


@router.get("/logout")
async def logout(
    request: Request,
    response: Response,
) -> Dict[str, Any]:
    """
    Logout endpoint.
    
    Args:
        request: FastAPI request
        response: FastAPI response
        
    Returns:
        Dict: Logout response
    """
    # Clear the session cookie
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )
    
    return {
        "message": "Logout successful",
    }
