"""
Authentication API router for Arkos AI.

This module provides the API router for authentication-related endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from pydantic import BaseModel, Field, validator

from arkos.api.auth_enhanced import (
    create_tokens,
    create_session,
    refresh_session,
    create_api_key,
    requires_admin,
    requires_write,
    UserRole,
)
from arkos.api.base import create_api_router, create_error_response, GenericResponse
from arkos.config import ArkosConfig
from arkos.models.user import User, APIKey, Session

logger = logging.getLogger(__name__)


# Request and response models
class LoginRequest(BaseModel):
    """Login request model."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response model."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str = Field(..., description="JWT refresh token")


class UserCreateRequest(BaseModel):
    """User create request model."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    email: Optional[str] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(UserRole.VIEWER, description="User role")
    
    @validator("password")
    def validate_password(cls, v, values, **kwargs):
        """Validate password."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdateRequest(BaseModel):
    """User update request model."""
    
    password: Optional[str] = Field(None, description="Password")
    email: Optional[str] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    
    @validator("password")
    def validate_password(cls, v, values, **kwargs):
        """Validate password."""
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserResponse(BaseModel):
    """User response model."""
    
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(..., description="User role")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    is_active: bool = Field(..., description="Whether the user is active")


class APIKeyCreateRequest(BaseModel):
    """API key create request model."""
    
    name: str = Field(..., description="API key name")
    expires_in_days: Optional[int] = Field(None, description="Expiration in days")


class APIKeyResponse(BaseModel):
    """API key response model."""
    
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key: Optional[str] = Field(None, description="API key (only returned on creation)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    last_used_at: Optional[str] = Field(None, description="Last usage timestamp")
    is_active: bool = Field(..., description="Whether the API key is active")


def create_auth_router(config: ArkosConfig) -> APIRouter:
    """
    Create a router for authentication-related endpoints.
    
    Args:
        config: Arkos configuration
        
    Returns:
        APIRouter: Router for authentication-related endpoints
    """
    router = create_api_router("/auth", ["auth"])
    
    @router.post(
        "/login",
        response_model=LoginResponse,
        summary="Login",
        description="Authenticates a user and returns JWT tokens",
    )
    async def login(
        request: Request,
        login_data: LoginRequest,
    ) -> LoginResponse:
        """Login a user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            # Return a default admin user
            return LoginResponse(
                access_token="dummy_token",
                refresh_token="dummy_refresh_token",
                token_type="bearer",
                user={
                    "id": "admin",
                    "username": "admin",
                    "role": UserRole.ADMIN,
                    "is_active": True,
                },
            )
        
        # Get the user from the database
        user = User.get_or_none(User.username == login_data.username)
        
        if user is None:
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    "invalid_credentials",
                    "Invalid username or password",
                    None,
                ),
            )
        
        # Check if the user is active
        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    "user_inactive",
                    "User is inactive",
                    None,
                ),
            )
        
        # Check if the user is locked
        if user.is_locked():
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    "user_locked",
                    "User is locked",
                    {"locked_until": user.locked_until.isoformat() if user.locked_until else None},
                ),
            )
        
        # Verify the password
        if not user.verify_password(login_data.password):
            # Record failed login attempt
            user.record_login(success=False)
            
            # Check if the user should be locked
            if user.failed_login_attempts >= config.auth.failed_login_attempts:
                user.lock_account(config.auth.lockout_duration_minutes)
                
                raise HTTPException(
                    status_code=401,
                    detail=create_error_response(
                        "account_locked",
                        "Account locked due to too many failed login attempts",
                        {"locked_until": user.locked_until.isoformat() if user.locked_until else None},
                    ),
                )
            
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    "invalid_credentials",
                    "Invalid username or password",
                    {"attempts_remaining": config.auth.failed_login_attempts - user.failed_login_attempts},
                ),
            )
        
        # Record successful login
        user.record_login(success=True)
        
        # Create a session
        session = create_session(user, request, config.auth)
        
        return LoginResponse(
            access_token=session.token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            user=user.to_dict(),
        )
    
    @router.post(
        "/refresh",
        response_model=LoginResponse,
        summary="Refresh token",
        description="Refreshes an access token using a refresh token",
    )
    async def refresh(
        request: Request,
        refresh_data: RefreshTokenRequest,
    ) -> LoginResponse:
        """Refresh an access token."""
        # Check if auth is enabled
        if not config.auth.enabled:
            # Return a default admin user
            return LoginResponse(
                access_token="dummy_token",
                refresh_token="dummy_refresh_token",
                token_type="bearer",
                user={
                    "id": "admin",
                    "username": "admin",
                    "role": UserRole.ADMIN,
                    "is_active": True,
                },
            )
        
        # Refresh the session
        access_token, refresh_token = refresh_session(
            refresh_data.refresh_token,
            request,
            config.auth,
        )
        
        # Get the user from the session
        session = Session.get_or_none(Session.token == access_token)
        user = session.user
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user.to_dict(),
        )
    
    @router.post(
        "/logout",
        response_model=GenericResponse,
        summary="Logout",
        description="Logs out a user by invalidating their session",
    )
    async def logout(
        request: Request,
        user=Depends(requires_write),
    ) -> GenericResponse:
        """Logout a user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            return GenericResponse(
                success=True,
                message="Logged out successfully",
            )
        
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Get the session
            session = Session.get_or_none(
                (Session.token == token) &
                (Session.is_active == True)
            )
            
            if session:
                # Invalidate the session
                session.is_active = False
                session.save()
        
        return GenericResponse(
            success=True,
            message="Logged out successfully",
        )
    
    @router.get(
        "/users",
        response_model=List[UserResponse],
        summary="List users",
        description="Returns a list of all users",
    )
    async def list_users(
        request: Request,
        user=Depends(requires_admin),
    ) -> List[UserResponse]:
        """List all users."""
        # Check if auth is enabled
        if not config.auth.enabled:
            return [
                UserResponse(
                    id="admin",
                    username="admin",
                    role=UserRole.ADMIN,
                    is_active=True,
                ),
            ]
        
        # Get all users from the database
        users = User.select()
        
        return [UserResponse(**user.to_dict()) for user in users]
    
    @router.post(
        "/users",
        response_model=UserResponse,
        summary="Create user",
        description="Creates a new user",
        status_code=201,
    )
    async def create_user(
        request: Request,
        user_data: UserCreateRequest,
        user=Depends(requires_admin),
    ) -> UserResponse:
        """Create a new user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "auth_disabled",
                    "Authentication is disabled",
                    None,
                ),
            )
        
        # Check if user already exists
        if User.get_or_none(User.username == user_data.username) is not None:
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    "user_already_exists",
                    f"User {user_data.username} already exists",
                    None,
                ),
            )
        
        # Validate password
        if len(user_data.password) < config.auth.password_min_length:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "invalid_password",
                    f"Password must be at least {config.auth.password_min_length} characters long",
                    None,
                ),
            )
        
        # Create the user
        new_user = User.create(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        new_user.set_password(user_data.password)
        new_user.save()
        
        return UserResponse(**new_user.to_dict())
    
    @router.get(
        "/users/{user_id}",
        response_model=UserResponse,
        summary="Get user",
        description="Returns a user by ID",
    )
    async def get_user(
        request: Request,
        user_id: str = Path(..., description="User ID"),
        user=Depends(requires_admin),
    ) -> UserResponse:
        """Get a user by ID."""
        # Check if auth is enabled
        if not config.auth.enabled:
            if user_id == "admin":
                return UserResponse(
                    id="admin",
                    username="admin",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
            
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {user_id} not found",
                    None,
                ),
            )
        
        # Get the user from the database
        db_user = User.get_or_none(User.id == user_id)
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {user_id} not found",
                    None,
                ),
            )
        
        return UserResponse(**db_user.to_dict())
    
    @router.put(
        "/users/{user_id}",
        response_model=UserResponse,
        summary="Update user",
        description="Updates an existing user",
    )
    async def update_user(
        request: Request,
        user_id: str = Path(..., description="User ID"),
        user_data: UserUpdateRequest = None,
        user=Depends(requires_admin),
    ) -> UserResponse:
        """Update an existing user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "auth_disabled",
                    "Authentication is disabled",
                    None,
                ),
            )
        
        # Get the user from the database
        db_user = User.get_or_none(User.id == user_id)
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {user_id} not found",
                    None,
                ),
            )
        
        # Update the user
        if user_data.password is not None:
            # Validate password
            if len(user_data.password) < config.auth.password_min_length:
                raise HTTPException(
                    status_code=400,
                    detail=create_error_response(
                        "invalid_password",
                        f"Password must be at least {config.auth.password_min_length} characters long",
                        None,
                    ),
                )
            
            db_user.set_password(user_data.password)
        
        if user_data.email is not None:
            db_user.email = user_data.email
        
        if user_data.full_name is not None:
            db_user.full_name = user_data.full_name
        
        if user_data.role is not None:
            db_user.role = user_data.role
        
        if user_data.is_active is not None:
            db_user.is_active = user_data.is_active
        
        db_user.updated_at = datetime.now()
        db_user.save()
        
        return UserResponse(**db_user.to_dict())
    
    @router.delete(
        "/users/{user_id}",
        response_model=GenericResponse,
        summary="Delete user",
        description="Deletes an existing user",
    )
    async def delete_user(
        request: Request,
        user_id: str = Path(..., description="User ID"),
        user=Depends(requires_admin),
    ) -> GenericResponse:
        """Delete an existing user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "auth_disabled",
                    "Authentication is disabled",
                    None,
                ),
            )
        
        # Get the user from the database
        db_user = User.get_or_none(User.id == user_id)
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {user_id} not found",
                    None,
                ),
            )
        
        # Delete the user
        db_user.delete_instance()
        
        return GenericResponse(
            success=True,
            message=f"User {db_user.username} deleted",
        )
    
    @router.get(
        "/api-keys",
        response_model=List[APIKeyResponse],
        summary="List API keys",
        description="Returns a list of all API keys for the current user",
    )
    async def list_api_keys(
        request: Request,
        user=Depends(requires_write),
    ) -> List[APIKeyResponse]:
        """List all API keys for the current user."""
        # Check if auth is enabled
        if not config.auth.enabled or not config.auth.api_key.enabled:
            return []
        
        # Get the user
        db_user = User.get_or_none(User.id == user["id"])
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    "User not found",
                    None,
                ),
            )
        
        # Get all API keys for the user
        api_keys = APIKey.select().where(APIKey.user == db_user)
        
        return [
            APIKeyResponse(
                id=str(api_key.id),
                name=api_key.name,
                created_at=api_key.created_at.isoformat() if api_key.created_at else None,
                expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
                last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                is_active=api_key.is_active,
            )
            for api_key in api_keys
        ]
    
    @router.post(
        "/api-keys",
        response_model=APIKeyResponse,
        summary="Create API key",
        description="Creates a new API key for the current user",
        status_code=201,
    )
    async def create_api_key_endpoint(
        request: Request,
        api_key_data: APIKeyCreateRequest,
        user=Depends(requires_write),
    ) -> APIKeyResponse:
        """Create a new API key for the current user."""
        # Check if auth is enabled
        if not config.auth.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "auth_disabled",
                    "Authentication is disabled",
                    None,
                ),
            )
        
        # Check if API keys are enabled
        if not config.auth.api_key.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "api_keys_disabled",
                    "API keys are disabled",
                    None,
                ),
            )
        
        # Get the user
        db_user = User.get_or_none(User.id == user["id"])
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    "User not found",
                    None,
                ),
            )
        
        # Create the API key
        api_key = create_api_key(
            db_user,
            api_key_data.name,
            config.auth,
            api_key_data.expires_in_days,
        )
        
        return APIKeyResponse(
            id=str(api_key.id),
            name=api_key.name,
            key=api_key.key,  # Only returned on creation
            created_at=api_key.created_at.isoformat() if api_key.created_at else None,
            expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
            is_active=api_key.is_active,
        )
    
    @router.delete(
        "/api-keys/{api_key_id}",
        response_model=GenericResponse,
        summary="Delete API key",
        description="Deletes an existing API key",
    )
    async def delete_api_key(
        request: Request,
        api_key_id: str = Path(..., description="API key ID"),
        user=Depends(requires_write),
    ) -> GenericResponse:
        """Delete an existing API key."""
        # Check if auth is enabled
        if not config.auth.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "auth_disabled",
                    "Authentication is disabled",
                    None,
                ),
            )
        
        # Check if API keys are enabled
        if not config.auth.api_key.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "api_keys_disabled",
                    "API keys are disabled",
                    None,
                ),
            )
        
        # Get the API key from the database
        api_key = APIKey.get_or_none(APIKey.id == api_key_id)
        
        if api_key is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "api_key_not_found",
                    f"API key {api_key_id} not found",
                    None,
                ),
            )
        
        # Check if the API key belongs to the user
        if str(api_key.user.id) != user["id"]:
            raise HTTPException(
                status_code=403,
                detail=create_error_response(
                    "forbidden",
                    "You don't have permission to delete this API key",
                    None,
                ),
            )
        
        # Delete the API key
        api_key.delete_instance()
        
        return GenericResponse(
            success=True,
            message=f"API key {api_key.name} deleted",
        )
    
    @router.get(
        "/sessions",
        response_model=List[Dict[str, Any]],
        summary="List sessions",
        description="Returns a list of all active sessions for the current user",
    )
    async def list_sessions(
        request: Request,
        user=Depends(requires_write),
    ) -> List[Dict[str, Any]]:
        """List all active sessions for the current user."""
        # Check if auth is enabled
        if not config.auth.enabled or not config.auth.session.enabled:
            return []
        
        # Get the user
        db_user = User.get_or_none(User.id == user["id"])
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    "User not found",
                    None,
                ),
            )
        
        # Get all active sessions for the user
        sessions = Session.select().where(
            (Session.user == db_user) &
            (Session.is_active == True)
        )
        
        return [session.to_dict() for session in sessions]
    
    @router.delete(
        "/sessions/{session_id}",
        response_model=GenericResponse,
        summary="Delete session",
        description="Deletes an existing session",
    )
    async def delete_session(
        request: Request,
        session_id: str = Path(..., description="Session ID"),
        user=Depends(requires_write),
    ) -> GenericResponse:
        """Delete an existing session."""
        # Check if auth is enabled
        if not config.auth.enabled or not config.auth.session.enabled:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "sessions_disabled",
                    "Sessions are disabled",
                    None,
                ),
            )
        
        # Get the session from the database
        session = Session.get_or_none(Session.id == session_id)
        
        if session is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "session_not_found",
                    f"Session {session_id} not found",
                    None,
                ),
            )
        
        # Check if the session belongs to the user
        if str(session.user.id) != user["id"]:
            raise HTTPException(
                status_code=403,
                detail=create_error_response(
                    "forbidden",
                    "You don't have permission to delete this session",
                    None,
                ),
            )
        
        # Delete the session
        session.is_active = False
        session.save()
        
        return GenericResponse(
            success=True,
            message="Session deleted",
        )
    
    return router
