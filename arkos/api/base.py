"""
Base module for the Arkos AI API.

This module provides the base router and common functionality for the API.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from arkos.api.auth import requires_auth

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Error response model."""
    
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginationMetadata(BaseModel):
    """Pagination metadata model."""
    
    total: int
    limit: int
    offset: int
    next: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    
    items: List[Any]
    pagination: PaginationMetadata


class GenericResponse(BaseModel):
    """Generic response model."""
    
    success: bool
    message: str


def create_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        code: Error code
        message: Error message
        details: Additional error details
        
    Returns:
        Dict: Error response
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }


def create_paginated_response(
    items: List[Any],
    total: int,
    limit: int,
    offset: int,
    base_url: str
) -> Dict[str, Any]:
    """
    Create a standardized paginated response.
    
    Args:
        items: List of items
        total: Total number of items
        limit: Maximum number of items per page
        offset: Number of items to skip
        base_url: Base URL for next page link
        
    Returns:
        Dict: Paginated response
    """
    next_url = None
    if offset + limit < total:
        next_url = f"{base_url}?limit={limit}&offset={offset + limit}"
        
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "next": next_url
        }
    }


def create_api_router(prefix: str, tags: List[str]) -> APIRouter:
    """
    Create a new API router with the given prefix and tags.
    
    Args:
        prefix: API route prefix
        tags: API route tags
        
    Returns:
        APIRouter: Configured API router
    """
    return APIRouter(prefix=prefix, tags=tags)
