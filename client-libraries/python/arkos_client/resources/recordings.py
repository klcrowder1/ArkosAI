"""
Recordings resource for the Arkos client library.
"""

from .base import Resource


class RecordingsResource(Resource):
    """Recordings resource."""

    def list(self, camera_name, after=None, before=None):
        """
        List recordings for a camera.

        Args:
            camera_name (str): Camera name
            after (float, optional): Filter recordings after this timestamp
            before (float, optional): Filter recordings before this timestamp

        Returns:
            list: List of recordings
        """
        params = {}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        return self._request(
            "GET", f"/api/v1/{camera_name}/recordings", params=params
        )

    def get_storage_usage(self):
        """
        Get recordings storage usage.

        Returns:
            dict: Storage usage information
        """
        return self._request("GET", "/api/v1/recordings/storage")

    def get_summary(self, timezone="utc", cameras="all"):
        """
        Get recordings summary.

        Args:
            timezone (str, optional): Timezone
            cameras (str, optional): Comma-separated list of cameras or "all"

        Returns:
            dict: Recordings summary
        """
        params = {"timezone": timezone, "cameras": cameras}
        return self._request("GET", "/api/v1/recordings/summary", params=params)

    def get_camera_summary(self, camera_name, timezone="utc"):
        """
        Get recordings summary for a specific camera.

        Args:
            camera_name (str): Camera name
            timezone (str, optional): Timezone

        Returns:
            dict: Camera recordings summary
        """
        params = {"timezone": timezone}
        return self._request(
            "GET", f"/api/v1/{camera_name}/recordings/summary", params=params
        )

    def get_clip(self, camera_name, start_ts, end_ts):
        """
        Get recording clip.

        Args:
            camera_name (str): Camera name
            start_ts (float): Start timestamp
            end_ts (float): End timestamp

        Returns:
            bytes: Video data
        """
        return self._request(
            "GET",
            f"/api/v1/{camera_name}/start/{start_ts}/end/{end_ts}/clip.mp4",
            headers={"Accept": "video/mp4"},
        )

    def get_snapshot(self, camera_name, frame_time, format="jpg", height=None):
        """
        Get snapshot from recording.

        Args:
            camera_name (str): Camera name
            frame_time (float): Frame timestamp
            format (str, optional): Image format (jpg, png)
            height (int, optional): Image height

        Returns:
            bytes: Image data
        """
        params = {}
        if height is not None:
            params["height"] = height
        return self._request(
            "GET",
            f"/api/v1/{camera_name}/recordings/{frame_time}/snapshot.{format}",
            params=params,
            headers={"Accept": "image/*"},
        )

    def export(self, camera_name, start_time, end_time, **kwargs):
        """
        Export recording.

        Args:
            camera_name (str): Camera name
            start_time (float): Start timestamp
            end_time (float): End timestamp
            **kwargs: Additional parameters
                playback (str, optional): Playback factor (realtime, timelapse_25x)
                source (str, optional): Playback source (recordings, preview)
                name (str, optional): Friendly name
                image_path (str, optional): Image path

        Returns:
            dict: Export information
        """
        return self._request(
            "POST",
            f"/api/v1/export/{camera_name}/start/{start_time}/end/{end_time}",
            json=kwargs,
        )

    def get_exports(self):
        """
        Get exports.

        Returns:
            list: List of exports
        """
        return self._request("GET", "/api/v1/exports")

    def get_export(self, export_id):
        """
        Get export details.

        Args:
            export_id (str): Export ID

        Returns:
            dict: Export details
        """
        return self._request("GET", f"/api/v1/exports/{export_id}")

    def rename_export(self, export_id, name):
        """
        Rename export.

        Args:
            export_id (str): Export ID
            name (str): New name

        Returns:
            dict: Response data
        """
        return self._request(
            "PATCH", f"/api/v1/export/{export_id}/rename", json={"name": name}
        )

    def delete_export(self, export_id):
        """
        Delete export.

        Args:
            export_id (str): Export ID

        Returns:
            dict: Response data
        """
        return self._request("DELETE", f"/api/v1/export/{export_id}")

    def get_preview(self, camera_name, start_ts, end_ts, format="gif"):
        """
        Get preview.

        Args:
            camera_name (str): Camera name
            start_ts (float): Start timestamp
            end_ts (float): End timestamp
            format (str, optional): Preview format (gif, mp4)

        Returns:
            bytes: Preview data
        """
        content_type = "image/gif" if format == "gif" else "video/mp4"
        return self._request(
            "GET",
            f"/api/v1/{camera_name}/start/{start_ts}/end/{end_ts}/preview.{format}",
            headers={"Accept": content_type},
        )
