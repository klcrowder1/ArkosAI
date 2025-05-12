"""
Events resource for the Arkos client library.
"""

from .base import Resource


class EventsResource(Resource):
    """Events resource."""

    def list(self, **kwargs):
        """
        List events.

        Args:
            **kwargs: Query parameters
                camera (str, optional): Filter by camera
                cameras (str, optional): Filter by multiple cameras (comma-separated)
                label (str, optional): Filter by label
                labels (str, optional): Filter by multiple labels (comma-separated)
                sub_label (str, optional): Filter by sub-label
                sub_labels (str, optional): Filter by multiple sub-labels (comma-separated)
                zone (str, optional): Filter by zone
                zones (str, optional): Filter by multiple zones (comma-separated)
                limit (int, optional): Maximum number of events to return
                after (float, optional): Filter events after this timestamp
                before (float, optional): Filter events before this timestamp
                time_range (str, optional): Filter events by time range (format: "HH:MM,HH:MM")
                has_clip (int, optional): Filter events with clips (1) or without clips (0)
                has_snapshot (int, optional): Filter events with snapshots (1) or without snapshots (0)
                in_progress (int, optional): Filter in-progress events (1) or completed events (0)
                include_thumbnails (int, optional): Include thumbnails in response (1) or not (0)
                favorites (int, optional): Filter favorite events (1) or non-favorite events (0)
                min_score (float, optional): Filter events with score >= min_score
                max_score (float, optional): Filter events with score <= max_score
                min_speed (float, optional): Filter events with speed >= min_speed
                max_speed (float, optional): Filter events with speed <= max_speed
                recognized_license_plate (str, optional): Filter by recognized license plate
                is_submitted (int, optional): Filter submitted events (1) or non-submitted events (0)
                min_length (float, optional): Filter events with length >= min_length
                max_length (float, optional): Filter events with length <= max_length
                event_id (str, optional): Filter by event ID
                sort (str, optional): Sort events (format: "field:direction")
                timezone (str, optional): Timezone for time-based filtering

        Returns:
            list: List of events
        """
        return self._request("GET", "/api/v1/events", params=kwargs)

    def get(self, event_id):
        """
        Get event details.

        Args:
            event_id (str): Event ID

        Returns:
            dict: Event details
        """
        return self._request("GET", f"/api/v1/events/{event_id}")

    def delete(self, event_id):
        """
        Delete an event.

        Args:
            event_id (str): Event ID

        Returns:
            dict: Response data
        """
        return self._request("DELETE", f"/api/v1/events/{event_id}")

    def create(self, camera_name, label, **kwargs):
        """
        Create a new event.

        Args:
            camera_name (str): Camera name
            label (str): Event label
            **kwargs: Additional parameters
                source_type (str, optional): Source type (default: "api")
                sub_label (str, optional): Sub-label
                score (float, optional): Score (default: 0)
                duration (int, optional): Duration in seconds (default: 30)
                include_recording (bool, optional): Include recording (default: True)
                draw (dict, optional): Drawing options (default: {})

        Returns:
            dict: Created event
        """
        return self._request(
            "POST", f"/api/v1/events/{camera_name}/{label}/create", json=kwargs
        )

    def end(self, event_id, end_time=None):
        """
        End an event.

        Args:
            event_id (str): Event ID
            end_time (float, optional): End time

        Returns:
            dict: Response data
        """
        data = {}
        if end_time is not None:
            data["end_time"] = end_time
        return self._request("PUT", f"/api/v1/events/{event_id}/end", json=data)

    def set_retain(self, event_id):
        """
        Set retain flag for an event.

        Args:
            event_id (str): Event ID

        Returns:
            dict: Response data
        """
        return self._request("POST", f"/api/v1/events/{event_id}/retain")

    def delete_retain(self, event_id):
        """
        Delete retain flag for an event.

        Args:
            event_id (str): Event ID

        Returns:
            dict: Response data
        """
        return self._request("DELETE", f"/api/v1/events/{event_id}/retain")

    def set_sub_label(self, event_id, sub_label, sub_label_score=None, camera=None):
        """
        Set sub-label for an event.

        Args:
            event_id (str): Event ID
            sub_label (str): Sub-label
            sub_label_score (float, optional): Sub-label score
            camera (str, optional): Camera name

        Returns:
            dict: Response data
        """
        data = {"subLabel": sub_label}
        if sub_label_score is not None:
            data["subLabelScore"] = sub_label_score
        if camera is not None:
            data["camera"] = camera
        return self._request("POST", f"/api/v1/events/{event_id}/sub_label", json=data)

    def set_description(self, event_id, description):
        """
        Set description for an event.

        Args:
            event_id (str): Event ID
            description (str): Description

        Returns:
            dict: Response data
        """
        return self._request(
            "POST",
            f"/api/v1/events/{event_id}/description",
            json={"description": description},
        )

    def regenerate_description(self, event_id, source="thumbnails"):
        """
        Regenerate description for an event.

        Args:
            event_id (str): Event ID
            source (str, optional): Source for description generation (thumbnails or snapshot)

        Returns:
            dict: Response data
        """
        return self._request(
            "PUT", f"/api/v1/events/{event_id}/description/regenerate", params={"source": source}
        )

    def delete_multiple(self, event_ids):
        """
        Delete multiple events.

        Args:
            event_ids (list): List of event IDs

        Returns:
            dict: Response data
        """
        return self._request("DELETE", "/api/v1/events/", json={"event_ids": event_ids})

    def get_snapshot(self, event_id, **kwargs):
        """
        Get event snapshot.

        Args:
            event_id (str): Event ID
            **kwargs: Additional parameters
                download (bool, optional): Download snapshot
                timestamp (int, optional): Include timestamp
                bbox (int, optional): Include bounding box
                crop (int, optional): Crop to object
                height (int, optional): Image height
                quality (int, optional): Image quality (default: 70)

        Returns:
            bytes: Image data
        """
        return self._request(
            "GET", f"/api/v1/events/{event_id}/snapshot.jpg", params=kwargs, headers={"Accept": "image/*"}
        )

    def get_thumbnail(self, event_id, extension="jpg", **kwargs):
        """
        Get event thumbnail.

        Args:
            event_id (str): Event ID
            extension (str, optional): Image extension (jpg, png)
            **kwargs: Additional parameters
                max_cache_age (int, optional): Maximum cache age in seconds
                format (str, optional): Format (ios, android)

        Returns:
            bytes: Image data
        """
        return self._request(
            "GET", f"/api/v1/events/{event_id}/thumbnail.{extension}", params=kwargs, headers={"Accept": "image/*"}
        )

    def get_clip(self, event_id):
        """
        Get event clip.

        Args:
            event_id (str): Event ID

        Returns:
            bytes: Video data
        """
        return self._request(
            "GET", f"/api/v1/events/{event_id}/clip.mp4", headers={"Accept": "video/mp4"}
        )

    def search(self, **kwargs):
        """
        Search events.

        Args:
            **kwargs: Query parameters
                query (str, optional): Search query
                event_id (str, optional): Event ID for similarity search
                search_type (str, optional): Search type (default: "thumbnail")
                include_thumbnails (int, optional): Include thumbnails in response (default: 1)
                limit (int, optional): Maximum number of events to return (default: 50)
                cameras (str, optional): Filter by cameras (comma-separated)
                labels (str, optional): Filter by labels (comma-separated)
                zones (str, optional): Filter by zones (comma-separated)
                after (float, optional): Filter events after this timestamp
                before (float, optional): Filter events before this timestamp
                time_range (str, optional): Filter events by time range (format: "HH:MM,HH:MM")
                has_clip (bool, optional): Filter events with clips
                has_snapshot (bool, optional): Filter events with snapshots
                is_submitted (bool, optional): Filter submitted events
                timezone (str, optional): Timezone for time-based filtering (default: "utc")
                min_score (float, optional): Filter events with score >= min_score
                max_score (float, optional): Filter events with score <= max_score
                min_speed (float, optional): Filter events with speed >= min_speed
                max_speed (float, optional): Filter events with speed <= max_speed
                recognized_license_plate (str, optional): Filter by recognized license plate
                sort (str, optional): Sort events (format: "field:direction")

        Returns:
            dict: Search results
        """
        return self._request("GET", "/api/v1/events/search", params=kwargs)

    def get_summary(self, **kwargs):
        """
        Get events summary.

        Args:
            **kwargs: Query parameters
                timezone (str, optional): Timezone (default: "utc")
                has_clip (int, optional): Filter events with clips (1) or without clips (0)
                has_snapshot (int, optional): Filter events with snapshots (1) or without snapshots (0)

        Returns:
            dict: Events summary
        """
        return self._request("GET", "/api/v1/events/summary", params=kwargs)
