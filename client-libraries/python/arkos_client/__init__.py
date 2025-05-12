"""
Arkos client library.
"""

from .client import ArkosClient
from .exceptions import (
    ArkosError,
    ArkosApiError,
    ArkosAuthError,
    ArkosRateLimitError,
    ArkosConnectionError,
    ArkosTimeoutError,
)

__version__ = "0.1.0"

__all__ = [
    "ArkosClient",
    "ArkosError",
    "ArkosApiError",
    "ArkosAuthError",
    "ArkosRateLimitError",
    "ArkosConnectionError",
    "ArkosTimeoutError",
]
