"""
Authentication for the Arkos client library.
"""

import time
import requests
import jwt

from .exceptions import ArkosAuthError


class Auth:
    """Base authentication class."""

    def get_headers(self):
        """
        Get authentication headers.

        Returns:
            dict: Authentication headers
        """
        return {}


class ApiKeyAuth(Auth):
    """API key authentication."""

    def __init__(self, api_key):
        """
        Initialize API key authentication.

        Args:
            api_key (str): API key
        """
        self.api_key = api_key

    def get_headers(self):
        """
        Get authentication headers.

        Returns:
            dict: Authentication headers
        """
        return {"X-API-Key": self.api_key}


class JwtAuth(Auth):
    """JWT authentication."""

    def __init__(self, host, username, password):
        """
        Initialize JWT authentication.

        Args:
            host (str): API host
            username (str): Username
            password (str): Password
        """
        self.host = host
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0

    def login(self):
        """
        Login to get JWT tokens.

        Raises:
            ArkosAuthError: If authentication fails
        """
        try:
            response = requests.post(
                f"{self.host}/api/v1/auth/login",
                json={"username": self.username, "password": self.password},
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            
            # Decode token to get expiry time
            decoded = jwt.decode(
                self.access_token, 
                options={"verify_signature": False}
            )
            self.token_expiry = decoded.get("exp", 0)
        except requests.RequestException as e:
            raise ArkosAuthError(f"Login failed: {str(e)}")

    def refresh(self):
        """
        Refresh JWT tokens.

        Raises:
            ArkosAuthError: If refresh fails
        """
        try:
            response = requests.post(
                f"{self.host}/api/v1/auth/refresh",
                headers={"Authorization": f"Bearer {self.refresh_token}"},
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            
            # Decode token to get expiry time
            decoded = jwt.decode(
                self.access_token, 
                options={"verify_signature": False}
            )
            self.token_expiry = decoded.get("exp", 0)
        except requests.RequestException as e:
            # If refresh fails, try to login again
            self.login()

    def get_headers(self):
        """
        Get authentication headers.

        Returns:
            dict: Authentication headers
        """
        # If no token or token is about to expire, login
        if not self.access_token or time.time() > self.token_expiry - 60:
            if not self.access_token:
                self.login()
            else:
                self.refresh()

        return {"Authorization": f"Bearer {self.access_token}"}
