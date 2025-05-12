"""
Rate limiting module for Arkos AI API.

This module provides rate limiting functionality for the Arkos AI API.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter for API requests.
    
    This class implements a token bucket algorithm for rate limiting.
    Each client (identified by IP address or API key) has a bucket of tokens.
    Tokens are added to the bucket at a fixed rate, up to a maximum capacity.
    Each request consumes one token from the bucket.
    If the bucket is empty, the request is rejected.
    """
    
    def __init__(self, rate: int = 100, per: int = 60, burst: int = 200):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Number of tokens to add per time period
            per: Time period in seconds
            burst: Maximum number of tokens in the bucket
        """
        self.rate = rate  # tokens per time period
        self.per = per  # time period in seconds
        self.burst = burst  # maximum bucket size
        self.tokens = {}  # token buckets for each client
        self.last_refill = {}  # last refill time for each client
        
    def get_client_id(self, request: Request) -> str:
        """
        Get the client ID from the request.
        
        Args:
            request: FastAPI request
            
        Returns:
            str: Client ID
        """
        # Try to get the API key from the request
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Try to get the JWT token from the request
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return f"jwt:{auth_header[7:]}"
        
        # Fall back to the client IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def refill_bucket(self, client_id: str) -> None:
        """
        Refill the token bucket for the given client.
        
        Args:
            client_id: Client ID
        """
        now = time.time()
        
        # Initialize the bucket if it doesn't exist
        if client_id not in self.tokens:
            self.tokens[client_id] = self.burst
            self.last_refill[client_id] = now
            return
        
        # Calculate the number of tokens to add
        time_passed = now - self.last_refill[client_id]
        tokens_to_add = time_passed * (self.rate / self.per)
        
        # Add tokens to the bucket, up to the maximum capacity
        self.tokens[client_id] = min(self.tokens[client_id] + tokens_to_add, self.burst)
        self.last_refill[client_id] = now
    
    def take_token(self, client_id: str) -> bool:
        """
        Take a token from the bucket for the given client.
        
        Args:
            client_id: Client ID
            
        Returns:
            bool: True if a token was taken, False if the bucket is empty
        """
        self.refill_bucket(client_id)
        
        if self.tokens[client_id] < 1:
            return False
        
        self.tokens[client_id] -= 1
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.
    
    This middleware applies rate limiting to all API requests.
    """
    
    def __init__(
        self,
        app: FastAPI,
        rate: int = 100,
        per: int = 60,
        burst: int = 200,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: FastAPI application
            rate: Number of tokens to add per time period
            per: Time period in seconds
            burst: Maximum number of tokens in the bucket
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(rate, per, burst)
        self.exclude_paths = exclude_paths or []
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Dispatch the request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or route handler
            
        Returns:
            Response: FastAPI response
        """
        # Skip rate limiting for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Get the client ID
        client_id = self.rate_limiter.get_client_id(request)
        
        # Check if the client has a token available
        if not self.rate_limiter.take_token(client_id):
            # Return a 429 Too Many Requests response
            return Response(
                content='{"error": {"code": "rate_limit_exceeded", "message": "Rate limit exceeded"}}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(self.rate_limiter.per),
                    "X-RateLimit-Limit": str(self.rate_limiter.rate),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.rate_limiter.per)),
                },
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.rate)
        response.headers["X-RateLimit-Remaining"] = str(int(self.rate_limiter.tokens[client_id]))
        response.headers["X-RateLimit-Reset"] = str(
            int(
                self.rate_limiter.last_refill[client_id]
                + self.rate_limiter.per
                - ((self.rate_limiter.burst - self.rate_limiter.tokens[client_id]) / self.rate_limiter.rate)
                * self.rate_limiter.per
            )
        )
        
        return response


def setup_rate_limiting(
    app: FastAPI,
    rate: int = 100,
    per: int = 60,
    burst: int = 200,
    exclude_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application
        rate: Number of tokens to add per time period
        per: Time period in seconds
        burst: Maximum number of tokens in the bucket
        exclude_paths: Paths to exclude from rate limiting
    """
    app.add_middleware(
        RateLimitMiddleware,
        rate=rate,
        per=per,
        burst=burst,
        exclude_paths=exclude_paths,
    )
    
    logger.info(f"Rate limiting set up: {rate} requests per {per} seconds, burst {burst}")
