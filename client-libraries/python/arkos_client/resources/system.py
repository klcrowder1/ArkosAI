"""
System resource for the Arkos client library.
"""

from .base import Resource


class SystemResource(Resource):
    """System resource."""

    def get_info(self):
        """
        Get system information.

        Returns:
            dict: System information
        """
        return self._request("GET", "/api/v1/system/info")

    def get_stats(self):
        """
        Get system statistics.

        Returns:
            dict: System statistics
        """
        return self._request("GET", "/api/v1/system/stats")

    def get_config(self):
        """
        Get system configuration.

        Returns:
            dict: System configuration
        """
        return self._request("GET", "/api/v1/system/config")

    def update_config(self, config_data, requires_restart=True):
        """
        Update system configuration.

        Args:
            config_data (dict): Configuration data
            requires_restart (bool, optional): Whether the update requires a restart

        Returns:
            dict: Response data
        """
        return self._request(
            "PUT",
            "/api/v1/config/set",
            json={"requires_restart": 1 if requires_restart else 0, **config_data},
        )

    def restart(self):
        """
        Restart the system.

        Returns:
            dict: Response data
        """
        return self._request("POST", "/api/v1/restart")

    def get_logs(self, service, **kwargs):
        """
        Get system logs.

        Args:
            service (str): Service name (arkos, nginx, go2rtc)
            **kwargs: Additional parameters (download, stream, start, end)

        Returns:
            str: Logs
        """
        return self._request("GET", f"/api/v1/logs/{service}", params=kwargs)

    def get_version(self):
        """
        Get version.

        Returns:
            str: Version
        """
        return self._request("GET", "/api/v1/version")

    def get_config_schema(self):
        """
        Get configuration schema.

        Returns:
            dict: Configuration schema
        """
        return self._request("GET", "/api/v1/config/schema.json")

    def get_raw_config(self):
        """
        Get raw configuration.

        Returns:
            dict: Raw configuration
        """
        return self._request("GET", "/api/v1/config/raw")

    def save_config(self, config_content, save_option):
        """
        Save configuration.

        Args:
            config_content (str): Configuration content
            save_option (str): Save option

        Returns:
            dict: Response data
        """
        return self._request(
            "POST",
            "/api/v1/config/save",
            params={"save_option": save_option},
            data=config_content,
            headers={"Content-Type": "text/plain"},
        )

    def get_labels(self, camera=None):
        """
        Get labels.

        Args:
            camera (str, optional): Camera name

        Returns:
            list: Labels
        """
        params = {}
        if camera:
            params["camera"] = camera
        return self._request("GET", "/api/v1/labels", params=params)

    def get_sub_labels(self, split_joined=None):
        """
        Get sub-labels.

        Args:
            split_joined (int, optional): Split joined sub-labels

        Returns:
            list: Sub-labels
        """
        params = {}
        if split_joined is not None:
            params["split_joined"] = split_joined
        return self._request("GET", "/api/v1/sub_labels", params=params)

    def get_recognized_license_plates(self, split_joined=None):
        """
        Get recognized license plates.

        Args:
            split_joined (int, optional): Split joined license plates

        Returns:
            list: Recognized license plates
        """
        params = {}
        if split_joined is not None:
            params["split_joined"] = split_joined
        return self._request("GET", "/api/v1/recognized_license_plates", params=params)

    def get_timeline(self, camera="all", limit=100, source_id=None):
        """
        Get timeline.

        Args:
            camera (str, optional): Camera name or "all"
            limit (int, optional): Maximum number of items to return
            source_id (str, optional): Source ID

        Returns:
            list: Timeline
        """
        params = {"camera": camera, "limit": limit}
        if source_id:
            params["source_id"] = source_id
        return self._request("GET", "/api/v1/timeline", params=params)

    def get_hourly_timeline(self, **kwargs):
        """
        Get hourly timeline.

        Args:
            **kwargs: Query parameters
                cameras (str, optional): Comma-separated list of cameras or "all"
                labels (str, optional): Comma-separated list of labels or "all"
                after (float, optional): Filter events after this timestamp
                before (float, optional): Filter events before this timestamp
                limit (int, optional): Maximum number of items to return
                timezone (str, optional): Timezone

        Returns:
            dict: Hourly timeline
        """
        return self._request("GET", "/api/v1/timeline/hourly", params=kwargs)
