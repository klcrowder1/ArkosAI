"""
API version management module for Arkos AI.

This module provides functionality for managing API versions and routing.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable, Set, Tuple

from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VersionStatus(str, Enum):
    """API version status enum."""
    
    CURRENT = "current"      # Current stable version
    BETA = "beta"            # Beta version, may have breaking changes
    DEPRECATED = "deprecated"  # Deprecated version, will be removed in the future
    SUNSET = "sunset"        # Sunset version, no longer supported


class APIVersionInfo(BaseModel):
    """API version information."""
    
    version: str = Field(..., description="Version identifier (e.g., 'v1')")
    status: VersionStatus = Field(..., description="Version status")
    release_date: datetime = Field(..., description="Version release date")
    sunset_date: Optional[datetime] = Field(None, description="Version sunset date (if applicable)")
    deprecated_by: Optional[str] = Field(None, description="Version that deprecates this version")
    description: str = Field("", description="Version description")


class APIVersion(str, Enum):
    """API version enum."""
    
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    
    @classmethod
    def from_string(cls, version_str: str) -> Optional["APIVersion"]:
        """
        Convert a string to an APIVersion enum value.
        
        Args:
            version_str: Version string (e.g., 'v1')
            
        Returns:
            APIVersion: Corresponding APIVersion enum value, or None if not found
        """
        try:
            return cls(version_str.lower())
        except ValueError:
            return None
    
    @classmethod
    def from_request(cls, request: Request) -> Optional["APIVersion"]:
        """
        Extract API version from a request.
        
        Args:
            request: FastAPI request
            
        Returns:
            APIVersion: Extracted APIVersion, or None if not found
        """
        # Try to extract version from URL path
        path = request.url.path
        match = re.match(r"^/api/(v[0-9]+)/.*$", path)
        if match:
            version_str = match.group(1)
            return cls.from_string(version_str)
        
        # Try to extract version from Accept header
        accept_header = request.headers.get("Accept")
        if accept_header:
            match = re.search(r"application/json;\s*version=(v[0-9]+)", accept_header)
            if match:
                version_str = match.group(1)
                return cls.from_string(version_str)
        
        # Try to extract version from X-API-Version header
        version_header = request.headers.get("X-API-Version")
        if version_header:
            return cls.from_string(version_header)
        
        return None


class VersionedAPIRouter(APIRouter):
    """
    Router that supports API versioning.
    
    This router extends FastAPI's APIRouter to add support for API versioning.
    Routes can be registered with specific API versions, and the router will
    handle routing requests to the appropriate version.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the versioned API router."""
        super().__init__(*args, **kwargs)
        self.version_routes: Dict[APIVersion, List[APIRoute]] = {
            version: [] for version in APIVersion
        }
        self.version_info: Dict[APIVersion, APIVersionInfo] = {}
        
    def include_router(self, router: APIRouter, version: APIVersion = APIVersion.V1, **kwargs):
        """
        Include a router for a specific API version.
        
        Args:
            router: Router to include
            version: API version to include the router for
            **kwargs: Additional arguments to pass to the parent include_router method
        """
        # Add version prefix to the router
        prefix = kwargs.get("prefix", "")
        kwargs["prefix"] = f"/api/{version}{prefix}"
        
        # Include the router
        super().include_router(router, **kwargs)
        
        # Store the routes for this version
        self.version_routes[version].extend(router.routes)
        
        logger.info(f"Registered {len(router.routes)} routes for API version {version}")
    
    def set_version_info(self, version: APIVersion, info: APIVersionInfo):
        """
        Set information for an API version.
        
        Args:
            version: API version
            info: Version information
        """
        self.version_info[version] = info
        logger.info(f"Set version info for API version {version}: {info.status}")


class APIVersionConfig(BaseModel):
    """API versioning configuration."""
    
    default_version: APIVersion = Field(APIVersion.V1, description="Default API version")
    current_version: APIVersion = Field(APIVersion.V1, description="Current API version")
    supported_versions: Set[APIVersion] = Field(
        {APIVersion.V1}, description="Supported API versions"
    )
    version_info: Dict[APIVersion, APIVersionInfo] = Field(
        default_factory=dict, description="Version information"
    )
    redirect_deprecated: bool = Field(
        True, description="Whether to redirect deprecated versions to the current version"
    )
    allow_version_override: bool = Field(
        True, description="Whether to allow version override via headers"
    )


def create_default_version_config() -> APIVersionConfig:
    """
    Create a default API version configuration.
    
    Returns:
        APIVersionConfig: Default API version configuration
    """
    now = datetime.now()
    one_year_from_now = now + timedelta(days=365)
    
    return APIVersionConfig(
        default_version=APIVersion.V1,
        current_version=APIVersion.V1,
        supported_versions={APIVersion.V1, APIVersion.V2},
        version_info={
            APIVersion.V1: APIVersionInfo(
                version=APIVersion.V1.value,
                status=VersionStatus.CURRENT,
                release_date=now - timedelta(days=30),
                description="Initial API version",
            ),
            APIVersion.V2: APIVersionInfo(
                version=APIVersion.V2.value,
                status=VersionStatus.BETA,
                release_date=now,
                description="Beta API version with enhanced features",
            ),
            APIVersion.V3: APIVersionInfo(
                version=APIVersion.V3.value,
                status=VersionStatus.BETA,
                release_date=now + timedelta(days=30),
                description="Future API version (not yet implemented)",
            ),
        },
    )


def register_api_versions(
    app: FastAPI, 
    router: VersionedAPIRouter, 
    config: Optional[APIVersionConfig] = None
):
    """
    Register API versions with the FastAPI application.
    
    Args:
        app: FastAPI application
        router: Versioned API router
        config: API version configuration (optional)
    """
    # Use default config if none is provided
    if config is None:
        config = create_default_version_config()
    
    # Set version info in the router
    for version, info in config.version_info.items():
        router.set_version_info(version, info)
    
    # Include the versioned router
    app.include_router(router)
    
    # Add a middleware to handle API version deprecation and redirects
    @app.middleware("http")
    async def api_version_middleware(request: Request, call_next: Callable):
        """
        Middleware to handle API version deprecation and redirects.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or route handler
            
        Returns:
            Response: FastAPI response
        """
        # Extract API version from the request
        version = APIVersion.from_request(request)
        
        # If no version is specified, use the default version
        if version is None:
            version = config.default_version
        
        # Check if the version is supported
        if version not in config.supported_versions:
            return Response(
                content=f"API version {version} is not supported. Supported versions: {', '.join([v.value for v in config.supported_versions])}",
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="text/plain",
            )
        
        # Check if the version is deprecated or sunset
        if version in config.version_info:
            version_info = config.version_info[version]
            
            # If the version is sunset, return a 410 Gone response
            if version_info.status == VersionStatus.SUNSET:
                return Response(
                    content=f"API version {version} is no longer supported. Please use version {config.current_version}.",
                    status_code=status.HTTP_410_GONE,
                    media_type="text/plain",
                )
            
            # If the version is deprecated and redirect_deprecated is enabled, redirect to the current version
            if version_info.status == VersionStatus.DEPRECATED and config.redirect_deprecated:
                # Get the current path and replace the version
                path = request.url.path
                new_path = re.sub(
                    r"^/api/v[0-9]+/", f"/api/{config.current_version}/", path
                )
                
                # Redirect to the current version
                return RedirectResponse(
                    url=new_path,
                    status_code=status.HTTP_301_MOVED_PERMANENTLY,
                )
        
        # Process the request
        response = await call_next(request)
        
        # Add API version headers
        response.headers["X-API-Version"] = version.value
        response.headers["X-API-Current-Version"] = config.current_version.value
        response.headers["X-API-Supported-Versions"] = ",".join([v.value for v in config.supported_versions])
        
        # Add version status header if available
        if version in config.version_info:
            version_info = config.version_info[version]
            response.headers["X-API-Version-Status"] = version_info.status.value
            
            # Add deprecation headers if the version is deprecated
            if version_info.status == VersionStatus.DEPRECATED:
                if version_info.sunset_date:
                    response.headers["Sunset"] = version_info.sunset_date.isoformat()
                if version_info.deprecated_by:
                    response.headers["Deprecation"] = version_info.deprecated_by
                response.headers["Link"] = f'</api/{config.current_version}>; rel="successor-version"'
        
        return response
    
    # Add API version endpoint
    @app.get("/api/versions", tags=["api"])
    async def get_api_versions():
        """Get information about API versions."""
        return {
            "versions": {
                version.value: info.model_dump() for version, info in config.version_info.items()
                if version in config.supported_versions
            },
            "current_version": config.current_version.value,
            "default_version": config.default_version.value,
        }
