"""
Base resource class for the Arkos client library.
"""

import requests
import time
from urllib.parse import urljoin

from ..exceptions import (
    ArkosApiError,
    ArkosAuthError,
    ArkosRateLimitError,
    ArkosConnectionError,
    ArkosTimeoutError,
)


class Resource:
    """Base resource class."""

    def __init__(self, client):
        """
        Initialize the resource.

        Args:
            client: The Arkos client
        """
        self.client = client

    def _make_url(self, path):
        """
        Make a URL from a path.

        Args:
            path (str): Path

        Returns:
            str: URL
        """
        return urljoin(self.client.host, path)

    def _handle_response(self, response):
        """
        Handle a response.

        Args:
            response (requests.Response): Response

        Returns:
            dict: Response data

        Raises:
            ArkosAuthError: If authentication fails
            ArkosRateLimitError: If rate limit is exceeded
            ArkosApiError: If API returns an error
        """
        if response.status_code == 401:
            raise ArkosAuthError(
                message=response.json().get("message", "Authentication failed"),
                details=response.json(),
            )
        elif response.status_code == 429:
            reset_time = response.headers.get("X-RateLimit-Reset")
            raise ArkosRateLimitError(reset_time=reset_time, details=response.json())
        elif response.status_code >= 400:
            error_data = response.json()
            error_code = error_data.get("error", {}).get("code", "unknown_error")
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_details = error_data.get("error", {}).get("details", {})
            raise ArkosApiError(
                response.status_code, error_code, error_message, error_details
            )

        return response.json()

    def _request(self, method, path, params=None, data=None, json=None, headers=None, files=None, retry_count=3):
        """
        Make a request.

        Args:
            method (str): HTTP method
            path (str): Path
            params (dict, optional): Query parameters
            data (dict, optional): Form data
            json (dict, optional): JSON data
            headers (dict, optional): Headers
            files (dict, optional): Files
            retry_count (int, optional): Number of retries

        Returns:
            dict: Response data

        Raises:
            ArkosConnectionError: If connection fails
            ArkosTimeoutError: If request times out
            ArkosAuthError: If authentication fails
            ArkosRateLimitError: If rate limit is exceeded
            ArkosApiError: If API returns an error
        """
        url = self._make_url(path)
        headers = headers or {}
        headers.update(self.client.auth.get_headers())

        for i in range(retry_count):
            try:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    files=files,
                    timeout=self.client.timeout,
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        sleep_time = int(reset_time) - time.time()
                        if sleep_time > 0:
                            time.sleep(min(sleep_time, 60))  # Sleep at most 60 seconds
                    else:
                        # If no reset time, use exponential backoff
                        time.sleep(2 ** i)
                    continue
                
                return self._handle_response(response)
            
            except requests.exceptions.Timeout:
                if i == retry_count - 1:
                    raise ArkosTimeoutError()
                time.sleep(2 ** i)
            
            except requests.exceptions.RequestException as e:
                if i == retry_count - 1:
                    raise ArkosConnectionError(str(e))
                time.sleep(2 ** i)
