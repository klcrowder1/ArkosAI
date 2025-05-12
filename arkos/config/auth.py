"""
Authentication configuration module for Arkos AI.

This module provides configuration models for authentication and authorization.
"""

from typing import Dict, List, Optional, Set, Union, Any
from datetime import timedelta

from pydantic import Field, field_validator

from arkos.config.base import ArkosBaseModel


class JWTConfig(ArkosBaseModel):
    """JWT configuration."""
    
    secret_key: str = Field(
        "arkos_secret_key", 
        description="Secret key for JWT token signing (should be set via environment variable)"
    )
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        1440, description="Access token expiration time in minutes (default: 24 hours)"
    )
    refresh_token_expire_minutes: int = Field(
        10080, description="Refresh token expiration time in minutes (default: 7 days)"
    )
    
    @property
    def access_token_expire_delta(self) -> timedelta:
        """Get access token expiration delta."""
        return timedelta(minutes=self.access_token_expire_minutes)
    
    @property
    def refresh_token_expire_delta(self) -> timedelta:
        """Get refresh token expiration delta."""
        return timedelta(minutes=self.refresh_token_expire_minutes)


class APIKeyConfig(ArkosBaseModel):
    """API key configuration."""
    
    enabled: bool = Field(True, description="Whether API key authentication is enabled")
    expiration_days: int = Field(
        365, description="API key expiration time in days (default: 1 year)"
    )
    key_length: int = Field(32, description="API key length in characters")
    
    @field_validator("key_length")
    @classmethod
    def validate_key_length(cls, v: int) -> int:
        """Validate key length."""
        if v < 16:
            raise ValueError("API key length must be at least 16 characters")
        return v


class RoleConfig(ArkosBaseModel):
    """Role configuration."""
    
    name: str = Field(..., description="Role name")
    description: str = Field("", description="Role description")
    permissions: Set[str] = Field(default_factory=set, description="Role permissions")


class RolesConfig(ArkosBaseModel):
    """Roles configuration."""
    
    admin: RoleConfig = Field(
        default_factory=lambda: RoleConfig(
            name="admin",
            description="Administrator with full access",
            permissions={"read", "write", "admin"},
        ),
        description="Admin role configuration",
    )
    operator: RoleConfig = Field(
        default_factory=lambda: RoleConfig(
            name="operator",
            description="Operator with read and write access",
            permissions={"read", "write"},
        ),
        description="Operator role configuration",
    )
    viewer: RoleConfig = Field(
        default_factory=lambda: RoleConfig(
            name="viewer",
            description="Viewer with read-only access",
            permissions={"read"},
        ),
        description="Viewer role configuration",
    )
    custom_roles: Dict[str, RoleConfig] = Field(
        default_factory=dict, description="Custom roles configuration"
    )
    
    def get_role(self, role_name: str) -> Optional[RoleConfig]:
        """Get role by name."""
        if role_name == "admin":
            return self.admin
        elif role_name == "operator":
            return self.operator
        elif role_name == "viewer":
            return self.viewer
        else:
            return self.custom_roles.get(role_name)
    
    def get_permissions(self, role_name: str) -> Set[str]:
        """Get permissions for a role."""
        role = self.get_role(role_name)
        if role:
            return role.permissions
        return set()


class SessionConfig(ArkosBaseModel):
    """Session configuration."""
    
    enabled: bool = Field(True, description="Whether session management is enabled")
    max_sessions_per_user: int = Field(
        5, description="Maximum number of active sessions per user"
    )
    session_timeout_minutes: int = Field(
        60, description="Session timeout in minutes (default: 1 hour)"
    )


class AuthConfig(ArkosBaseModel):
    """Authentication configuration."""
    
    enabled: bool = Field(True, description="Whether authentication is enabled")
    jwt: JWTConfig = Field(
        default_factory=JWTConfig, description="JWT configuration"
    )
    api_key: APIKeyConfig = Field(
        default_factory=APIKeyConfig, description="API key configuration"
    )
    roles: RolesConfig = Field(
        default_factory=RolesConfig, description="Roles configuration"
    )
    session: SessionConfig = Field(
        default_factory=SessionConfig, description="Session configuration"
    )
    default_admin_username: str = Field(
        "admin", description="Default admin username"
    )
    default_admin_password: str = Field(
        "admin", description="Default admin password (should be changed)"
    )
    allow_default_admin: bool = Field(
        True, description="Whether to allow the default admin user"
    )
    password_min_length: int = Field(
        8, description="Minimum password length"
    )
    password_require_uppercase: bool = Field(
        True, description="Whether passwords require uppercase letters"
    )
    password_require_lowercase: bool = Field(
        True, description="Whether passwords require lowercase letters"
    )
    password_require_numbers: bool = Field(
        True, description="Whether passwords require numbers"
    )
    password_require_special: bool = Field(
        True, description="Whether passwords require special characters"
    )
    failed_login_attempts: int = Field(
        5, description="Number of failed login attempts before lockout"
    )
    lockout_duration_minutes: int = Field(
        30, description="Account lockout duration in minutes"
    )
