"""
Exceptions for the Arkos client library.
"""


class ArkosError(Exception):
    """Base exception for all Arkos client errors."""
    pass


class ArkosApiError(ArkosError):
    """Exception raised for API errors."""

    def __init__(self, status_code, error_code, message, details=None):
        """
        Initialize the exception.

        Args:
            status_code (int): HTTP status code
            error_code (str): Error code returned by the API
            message (str): Error message
            details (dict, optional): Additional error details
        """
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(f"{status_code} {error_code}: {message}")


class ArkosAuthError(ArkosApiError):
    """Exception raised for authentication errors."""

    def __init__(self, message="Authentication failed", details=None):
        """
        Initialize the exception.

        Args:
            message (str): Error message
            details (dict, optional): Additional error details
        """
        super().__init__(401, "unauthorized", message, details)


class ArkosRateLimitError(ArkosApiError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, reset_time=None, details=None):
        """
        Initialize the exception.

        Args:
            reset_time (int, optional): Time when the rate limit resets
            details (dict, optional): Additional error details
        """
        self.reset_time = reset_time
        message = "Rate limit exceeded"
        if reset_time:
            message += f", resets at {reset_time}"
        super().__init__(429, "rate_limit_exceeded", message, details)


class ArkosConnectionError(ArkosError):
    """Exception raised for connection errors."""

    def __init__(self, message="Connection error", details=None):
        """
        Initialize the exception.

        Args:
            message (str): Error message
            details (dict, optional): Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ArkosTimeoutError(ArkosConnectionError):
    """Exception raised for timeout errors."""

    def __init__(self, message="Request timed out", details=None):
        """
        Initialize the exception.

        Args:
            message (str): Error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
