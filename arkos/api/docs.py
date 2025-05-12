"""
API documentation module for Arkos AI.

This module provides functionality for generating API documentation.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)


def setup_api_docs(app: FastAPI, title: str, description: str, version: str):
    """
    Set up API documentation for the FastAPI application.
    
    Args:
        app: FastAPI application
        title: API title
        description: API description
        version: API version
    """
    # Mount static files for documentation
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=title,
            description=description,
            version=version,
            routes=app.routes,
        )
        
        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
            },
        }
        
        # Apply security to all routes
        openapi_schema["security"] = [
            {"bearerAuth": []},
            {"apiKeyAuth": []},
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    # Custom documentation routes
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
    
    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()
    
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )
    
    logger.info("API documentation set up")


def generate_openapi_spec(app: FastAPI, output_path: str):
    """
    Generate OpenAPI specification file.
    
    Args:
        app: FastAPI application
        output_path: Output file path
    """
    import json
    
    with open(output_path, "w") as f:
        json.dump(app.openapi(), f, indent=2)
    
    logger.info(f"OpenAPI specification generated at {output_path}")
