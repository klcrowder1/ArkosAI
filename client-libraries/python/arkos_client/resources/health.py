"""
Health resource for the Arkos client library.
"""

from .base import Resource


class HealthResource(Resource):
    """Health resource."""

    def get(self):
        """
        Get health status of the system, cameras, and storage.

        Returns:
            dict: Health status
        """
        return self._request("GET", "/api/v1/health")

    def get_system(self):
        """
        Get system health.

        Returns:
            dict: System health
        """
        return self._request("GET", "/api/v1/health/system")

    def get_cameras(self):
        """
        Get camera health.

        Returns:
            dict: Camera health
        """
        return self._request("GET", "/api/v1/health/cameras")

    def get_storage(self):
        """
        Get storage health.

        Returns:
            dict: Storage health
        """
        return self._request("GET", "/api/v1/health/storage")

    def get_stats(self):
        """
        Get system statistics.

        Returns:
            dict: System statistics
        """
        return self._request("GET", "/api/v1/stats")

    def get_stats_history(self, keys=None):
        """
        Get system statistics history.

        Args:
            keys (str, optional): Comma-separated list of keys to include

        Returns:
            dict: System statistics history
        """
        params = {}
        if keys:
            params["keys"] = keys
        return self._request("GET", "/api/v1/stats/history", params=params)

    def get_metrics(self):
        """
        Get system metrics.

        Returns:
            dict: System metrics
        """
        return self._request("GET", "/api/v1/metrics")

    def get_ffprobe(self, paths=None):
        """
        Get ffprobe information.

        Args:
            paths (str, optional): Comma-separated list of paths to probe

        Returns:
            dict: FFprobe information
        """
        params = {}
        if paths:
            params["paths"] = paths
        return self._request("GET", "/api/v1/ffprobe", params=params)

    def get_vainfo(self):
        """
        Get VA-API information.

        Returns:
            dict: VA-API information
        """
        return self._request("GET", "/api/v1/vainfo")

    def get_nvinfo(self):
        """
        Get NVIDIA information.

        Returns:
            dict: NVIDIA information
        """
        return self._request("GET", "/api/v1/nvinfo")

    def get_logs(self, service, download=None, stream=False, start=0, end=None):
        """
        Get logs for a service.

        Args:
            service (str): Service name (arkos, nginx, go2rtc)
            download (str, optional): Download filename
            stream (bool, optional): Stream logs
            start (int, optional): Start line
            end (int, optional): End line

        Returns:
            str: Logs
        """
        params = {"stream": stream, "start": start}
        if download:
            params["download"] = download
        if end is not None:
            params["end"] = end
        return self._request("GET", f"/api/v1/logs/{service}", params=params)
