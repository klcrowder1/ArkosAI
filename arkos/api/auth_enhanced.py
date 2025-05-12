"""
Enhanced authentication and authorization module for Arkos AI API.

This module provides enhanced authentication and authorization functionality
for the Arkos AI API, including JWT token support, API key authentication,
and role-based access control.
"""

import logging
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any

import jwt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader

from arkos.api.base import create_error_response
from arkos.models import User

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT settings
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "arkos_secret_key")  # Should be loaded from environment or config
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)


class UserRole(str, Enum):
    """User role enum."""
    
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permission enum."""
    
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


# Role-based permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.ADMIN],
    UserRole.OPERATOR: [Permission.READ, Permission.WRITE],
    UserRole.VIEWER: [Permission.READ],
}


def create_jwt_token(user_id: str, username: str, role: str) -> str:
    """
    Create a JWT token for the given user.
    
    Args:
        user_id: User ID
        username: Username
        role: User role
        
    Returns:
        str: JWT token
    """
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + JWT_EXPIRATION_DELTA,
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        HTTPException: If the token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "token_expired",
                "Token has expired",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "invalid_token",
                "Invalid token",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    api_key: Optional[str] = Security(api_key_header),
) -> Dict[str, Any]:
    """
    Get the current user from the request.
    
    Args:
        request: FastAPI request
        credentials: HTTP authorization credentials
        api_key: API key
        
    Returns:
        Dict: User information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if auth is enabled
    if not request.app.state.config.auth.enabled:
        return {"username": "admin", "role": UserRole.ADMIN}
    
    # Check for JWT token
    if credentials:
        token = credentials.credentials
        payload = decode_jwt_token(token)
        
        # Get the user from the database
        user = User.get_or_none(User.id == payload["sub"])
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "user_not_found",
                    "User not found",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"username": user.username, "role": user.role, "user_id": user.id}
    
    # Check for API key
    if api_key:
        # TODO: Implement API key validation
        # This is a placeholder for API key validation
        # In a real implementation, you would validate the API key against a database
        if api_key == "test_api_key":
            return {"username": "api", "role": UserRole.OPERATOR, "api_key": api_key}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "invalid_api_key",
                "Invalid API key",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # No authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=create_error_response(
            "authentication_required",
            "Authentication required",
            None
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def has_permission(required_permission: Permission):
    """
    Dependency to check if the user has the required permission.
    
    Args:
        required_permission: Required permission
        
    Returns:
        Callable: Dependency function
    """
    async def check_permission(user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("role")
        
        if user_role not in ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=create_error_response(
                    "invalid_role",
                    "Invalid user role",
                    None
                ),
            )
        
        if required_permission not in ROLE_PERMISSIONS[user_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=create_error_response(
                    "insufficient_permissions",
                    f"User does not have {required_permission} permission",
                    None
                ),
            )
        
        return user
    
    return check_permission


# Convenience dependencies for common permission checks
requires_read = has_permission(Permission.READ)
requires_write = has_permission(Permission.WRITE)
requires_admin = has_permission(Permission.ADMIN)
