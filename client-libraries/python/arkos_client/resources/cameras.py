"""
Cameras resource for the Arkos client library.
"""

from .base import Resource


class CamerasResource(Resource):
    """Cameras resource."""

    def list(self):
        """
        List all cameras.

        Returns:
            list: List of cameras
        """
        return self._request("GET", "/api/v1/cameras")

    def get(self, camera_id):
        """
        Get camera details.

        Args:
            camera_id (str): Camera ID

        Returns:
            dict: Camera details
        """
        return self._request("GET", f"/api/v1/cameras/{camera_id}")

    def create(self, camera_data):
        """
        Create a new camera.

        Args:
            camera_data (dict): Camera data

        Returns:
            dict: Created camera
        """
        return self._request("POST", "/api/v1/cameras", json=camera_data)

    def update(self, camera_id, camera_data):
        """
        Update an existing camera.

        Args:
            camera_id (str): Camera ID
            camera_data (dict): Camera data

        Returns:
            dict: Updated camera
        """
        return self._request("PUT", f"/api/v1/cameras/{camera_id}", json=camera_data)

    def delete(self, camera_id):
        """
        Delete an existing camera.

        Args:
            camera_id (str): Camera ID

        Returns:
            dict: Response data
        """
        return self._request("DELETE", f"/api/v1/cameras/{camera_id}")

    def get_connection_status(self, camera_id=None):
        """
        Get connection status for cameras.

        Args:
            camera_id (str, optional): Camera ID. If not provided, get status for all cameras.

        Returns:
            dict: Connection status
        """
        if camera_id:
            return self._request("GET", f"/api/v1/cameras/{camera_id}/connection/status")
        return self._request("GET", "/api/v1/cameras/connection/status")

    def reset_connection(self, camera_id):
        """
        Reset connection for a specific camera.

        Args:
            camera_id (str): Camera ID

        Returns:
            dict: Response data
        """
        return self._request("POST", f"/api/v1/cameras/{camera_id}/connection/reset")

    def get_latest_frame(self, camera_id, format="jpg", **kwargs):
        """
        Get the latest frame from a camera.

        Args:
            camera_id (str): Camera ID
            format (str, optional): Image format (jpg, png, webp). Defaults to "jpg".
            **kwargs: Additional parameters (bbox, timestamp, zones, mask, motion, regions, quality, height)

        Returns:
            bytes: Image data
        """
        valid_formats = ["jpg", "jpeg", "png", "webp"]
        if format not in valid_formats:
            format = "jpg"

        return self._request(
            "GET", f"/api/v1/{camera_id}/latest.{format}", params=kwargs, headers={"Accept": "image/*"}
        )

    def get_mjpeg_feed(self, camera_id, **kwargs):
        """
        Get MJPEG feed URL for a camera.

        Args:
            camera_id (str): Camera ID
            **kwargs: Additional parameters (fps, height, bbox, timestamp, zones, mask, motion, regions)

        Returns:
            str: MJPEG feed URL
        """
        params = "&".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{self.client.host}/api/v1/{camera_id}?{params}"

    def get_ptz_info(self, camera_id):
        """
        Get PTZ information for a camera.

        Args:
            camera_id (str): Camera ID

        Returns:
            dict: PTZ information
        """
        return self._request("GET", f"/api/v1/{camera_id}/ptz/info")
