"""
API configuration module for Arkos AI.

This module provides configuration models for the Arkos AI API.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union

from pydantic import Field

from arkos.api.version import APIVersion, APIVersionInfo, VersionStatus
from arkos.config.base import ArkosBaseModel


class RateLimitConfig(ArkosBaseModel):
    """Rate limit configuration."""
    
    rate: int = Field(100, description="Number of requests allowed per time period")
    per: int = Field(60, description="Time period in seconds")
    burst: int = Field(200, description="Maximum burst size")


class APIVersioningConfig(ArkosBaseModel):
    """API versioning configuration."""
    
    default_version: APIVersion = Field(APIVersion.V1, description="Default API version")
    current_version: APIVersion = Field(APIVersion.V1, description="Current API version")
    supported_versions: Set[APIVersion] = Field(
        {APIVersion.V1, APIVersion.V2}, description="Supported API versions"
    )
    redirect_deprecated: bool = Field(
        True, description="Whether to redirect deprecated versions to the current version"
    )
    allow_version_override: bool = Field(
        True, description="Whether to allow version override via headers"
    )


class APIConfig(ArkosBaseModel):
    """API configuration."""
    
    enabled: bool = Field(True, description="Whether the API is enabled")
    host: str = Field("0.0.0.0", description="API host")
    port: int = Field(5001, description="API port")
    base_path: str = Field("/api", description="API base path")
    cors_origins: List[str] = Field(["*"], description="CORS allowed origins")
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig, description="Rate limit configuration"
    )
    versioning: APIVersioningConfig = Field(
        default_factory=APIVersioningConfig, description="API versioning configuration"
    )
    docs_url: str = Field("/api/docs", description="API documentation URL")
    redoc_url: str = Field("/api/redoc", description="ReDoc documentation URL")
    openapi_url: str = Field("/api/openapi.json", description="OpenAPI specification URL")
    debug: bool = Field(False, description="Whether to enable debug mode")
