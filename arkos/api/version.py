"""
API version management module for Arkos AI.

This module provides functionality for managing API versions and routing.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


class APIVersion(str, Enum):
    """API version enum."""
    
    V1 = "v1"
    V2 = "v2"


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


def register_api_versions(app: FastAPI, router: VersionedAPIRouter):
    """
    Register API versions with the FastAPI application.
    
    Args:
        app: FastAPI application
        router: Versioned API router
    """
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
        # Process the request
        response = await call_next(request)
        
        # Add API version headers
        response.headers["X-API-Version"] = APIVersion.V1.value
        response.headers["X-API-Supported-Versions"] = ",".join([v.value for v in APIVersion])
        
        return response
