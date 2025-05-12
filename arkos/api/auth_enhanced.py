"""
Enhanced authentication and authorization module for Arkos AI API.

This module provides enhanced authentication and authorization functionality
for the Arkos AI API, including JWT token support, API key authentication,
and role-based access control.
"""

import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple

import jwt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader

from arkos.api.base import create_error_response
from arkos.models.user import User, APIKey, Session

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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


class TokenType(str, Enum):
    """Token type enum."""
    
    ACCESS = "access"
    REFRESH = "refresh"


def create_tokens(
    user_id: str,
    username: str,
    role: str,
    config: Any,
) -> Tuple[str, str]:
    """
    Create access and refresh tokens for the given user.
    
    Args:
        user_id: User ID
        username: Username
        role: User role
        config: Auth configuration
        
    Returns:
        Tuple[str, str]: Access token and refresh token
    """
    # Create access token
    access_payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": TokenType.ACCESS,
        "exp": datetime.utcnow() + config.jwt.access_token_expire_delta,
        "iat": datetime.utcnow(),
    }
    
    access_token = jwt.encode(
        access_payload,
        config.jwt.secret_key,
        algorithm=config.jwt.algorithm,
    )
    
    # Create refresh token
    refresh_payload = {
        "sub": user_id,
        "type": TokenType.REFRESH,
        "exp": datetime.utcnow() + config.jwt.refresh_token_expire_delta,
        "iat": datetime.utcnow(),
    }
    
    refresh_token = jwt.encode(
        refresh_payload,
        config.jwt.secret_key,
        algorithm=config.jwt.algorithm,
    )
    
    return access_token, refresh_token


def decode_token(token: str, config: Any) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token
        config: Auth configuration
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        HTTPException: If the token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            config.jwt.secret_key,
            algorithms=[config.jwt.algorithm],
        )
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


def create_session(
    user: User,
    request: Request,
    config: Any,
) -> Session:
    """
    Create a new session for the user.
    
    Args:
        user: User
        request: FastAPI request
        config: Auth configuration
        
    Returns:
        Session: Created session
    """
    # Generate tokens
    access_token, refresh_token = create_tokens(
        user_id=str(user.id),
        username=user.username,
        role=user.role,
        config=config,
    )
    
    # Create session
    session = Session.create(
        user=user,
        token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.now() + config.jwt.refresh_token_expire_delta,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    
    # Check if the user has too many sessions
    if config.session.max_sessions_per_user > 0:
        sessions = Session.select().where(
            (Session.user == user) &
            (Session.is_active == True)
        ).order_by(Session.last_activity.desc())
        
        if sessions.count() > config.session.max_sessions_per_user:
            # Deactivate the oldest sessions
            for old_session in sessions.offset(config.session.max_sessions_per_user):
                old_session.is_active = False
                old_session.save()
    
    return session


def refresh_session(
    refresh_token: str,
    request: Request,
    config: Any,
) -> Tuple[str, str]:
    """
    Refresh a session using a refresh token.
    
    Args:
        refresh_token: Refresh token
        request: FastAPI request
        config: Auth configuration
        
    Returns:
        Tuple[str, str]: New access token and refresh token
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    # Decode the refresh token
    payload = decode_token(refresh_token, config)
    
    # Check if it's a refresh token
    if payload.get("type") != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "invalid_token_type",
                "Invalid token type",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get the user
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
    
    # Get the session
    session = Session.get_or_none(
        (Session.refresh_token == refresh_token) &
        (Session.is_active == True)
    )
    
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "invalid_session",
                "Invalid session",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the session is expired
    if session.is_expired():
        session.is_active = False
        session.save()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                "session_expired",
                "Session has expired",
                None
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    access_token, refresh_token = create_tokens(
        user_id=str(user.id),
        username=user.username,
        role=user.role,
        config=config,
    )
    
    # Update the session
    session.token = access_token
    session.refresh_token = refresh_token
    session.expires_at = datetime.now() + config.jwt.refresh_token_expire_delta
    session.last_activity = datetime.now()
    session.save()
    
    return access_token, refresh_token


def create_api_key(
    user: User,
    name: str,
    config: Any,
    expires_in_days: Optional[int] = None,
) -> APIKey:
    """
    Create a new API key for the user.
    
    Args:
        user: User
        name: API key name
        config: Auth configuration
        expires_in_days: Number of days until the API key expires
        
    Returns:
        APIKey: Created API key
    """
    # Generate API key
    key = APIKey.generate_key(config.api_key.key_length)
    
    # Set expiration date
    if expires_in_days is None:
        expires_in_days = config.api_key.expiration_days
    
    expires_at = None
    if expires_in_days > 0:
        expires_at = datetime.now().replace(
            day=datetime.now().day + expires_in_days
        )
    
    # Create API key
    api_key = APIKey.create(
        user=user,
        name=name,
        key=key,
        expires_at=expires_at,
    )
    
    return api_key


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
    # Get auth configuration
    config = request.app.state.config.auth
    
    # Check if auth is enabled
    if not config.enabled:
        return {"username": "admin", "role": UserRole.ADMIN}
    
    # Check for JWT token
    if credentials:
        token = credentials.credentials
        payload = decode_token(token, config)
        
        # Check if it's an access token
        if payload.get("type") != TokenType.ACCESS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "invalid_token_type",
                    "Invalid token type",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
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
        
        # Check if the user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "user_inactive",
                    "User is inactive",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the user is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "user_locked",
                    "User is locked",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get the session
        session = Session.get_or_none(
            (Session.token == token) &
            (Session.is_active == True)
        )
        
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "invalid_session",
                    "Invalid session",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the session is expired
        if session.is_expired():
            session.is_active = False
            session.save()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "session_expired",
                    "Session has expired",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update session activity
        session.update_activity()
        
        return user.to_dict()
    
    # Check for API key
    if api_key and config.api_key.enabled:
        # Get the API key from the database
        api_key_obj = APIKey.get_or_none(APIKey.key == api_key)
        
        if api_key_obj is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "invalid_api_key",
                    "Invalid API key",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the API key is active
        if not api_key_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "api_key_inactive",
                    "API key is inactive",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the API key is expired
        if api_key_obj.is_expired():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "api_key_expired",
                    "API key has expired",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get the user
        user = api_key_obj.user
        
        # Check if the user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    "user_inactive",
                    "User is inactive",
                    None
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Record API key usage
        api_key_obj.record_usage()
        
        # Return user information with API key flag
        user_dict = user.to_dict()
        user_dict["api_key"] = True
        
        return user_dict
    
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
    async def check_permission(
        request: Request,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        # Get auth configuration
        config = request.app.state.config.auth
        
        # Get user role
        user_role = user.get("role")
        
        # Get role permissions
        role = config.roles.get_role(user_role)
        
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=create_error_response(
                    "invalid_role",
                    "Invalid user role",
                    None
                ),
            )
        
        # Check if the user has the required permission
        if required_permission.value not in role.permissions:
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
