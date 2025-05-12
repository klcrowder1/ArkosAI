"""
Authentication API router for Arkos AI.

This module provides the API router for authentication-related endpoints.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from pydantic import BaseModel, Field

from arkos.api.auth_enhanced import (
    create_jwt_token,
    requires_admin,
    UserRole,
)
from arkos.api.base import create_api_router, create_error_response, GenericResponse
from arkos.config import ArkosConfig
from arkos.models import User

logger = logging.getLogger(__name__)


# Request and response models
class LoginRequest(BaseModel):
    """Login request model."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response model."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User information")


class UserCreateRequest(BaseModel):
    """User create request model."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    role: UserRole = Field(UserRole.VIEWER, description="User role")


class UserUpdateRequest(BaseModel):
    """User update request model."""
    
    password: Optional[str] = Field(None, description="Password")
    role: Optional[UserRole] = Field(None, description="User role")


class UserResponse(BaseModel):
    """User response model."""
    
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: UserRole = Field(..., description="User role")


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
        description="Authenticates a user and returns a JWT token",
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
                token_type="bearer",
                user={
                    "id": "admin",
                    "username": "admin",
                    "role": UserRole.ADMIN,
                },
            )
        
        # Get the user from the database
        user = User.get_or_none(User.username == login_data.username)
        
        if user is None or not user.verify_password(login_data.password):
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    "invalid_credentials",
                    "Invalid username or password",
                    None,
                ),
            )
        
        # Create a JWT token
        token = create_jwt_token(
            user_id=str(user.id),
            username=user.username,
            role=user.role,
        )
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "username": user.username,
                "role": user.role,
            },
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
                ),
            ]
        
        # Get all users from the database
        users = User.select()
        
        return [
            UserResponse(
                id=str(user.id),
                username=user.username,
                role=user.role,
            )
            for user in users
        ]
    
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
        
        # Create the user
        new_user = User.create(
            username=user_data.username,
            role=user_data.role,
        )
        new_user.set_password(user_data.password)
        new_user.save()
        
        return UserResponse(
            id=str(new_user.id),
            username=new_user.username,
            role=new_user.role,
        )
    
    @router.put(
        "/users/{username}",
        response_model=UserResponse,
        summary="Update user",
        description="Updates an existing user",
    )
    async def update_user(
        request: Request,
        username: str = Path(..., description="Username"),
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
        db_user = User.get_or_none(User.username == username)
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {username} not found",
                    None,
                ),
            )
        
        # Update the user
        if user_data.password is not None:
            db_user.set_password(user_data.password)
        
        if user_data.role is not None:
            db_user.role = user_data.role
        
        db_user.save()
        
        return UserResponse(
            id=str(db_user.id),
            username=db_user.username,
            role=db_user.role,
        )
    
    @router.delete(
        "/users/{username}",
        response_model=GenericResponse,
        summary="Delete user",
        description="Deletes an existing user",
    )
    async def delete_user(
        request: Request,
        username: str = Path(..., description="Username"),
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
        db_user = User.get_or_none(User.username == username)
        
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "user_not_found",
                    f"User {username} not found",
                    None,
                ),
            )
        
        # Delete the user
        db_user.delete_instance()
        
        return GenericResponse(
            success=True,
            message=f"User {username} deleted",
        )
    
    return router
