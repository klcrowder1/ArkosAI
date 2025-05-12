"""
Storage resource for the Arkos client library.
"""

from .base import Resource


class StorageResource(Resource):
    """Storage resource."""

    def get(self):
        """
        Get storage information.

        Returns:
            dict: Storage information
        """
        return self._request("GET", "/api/v1/storage")

    def get_usage(self):
        """
        Get storage usage statistics.

        Returns:
            dict: Storage usage statistics
        """
        return self._request("GET", "/api/v1/storage/usage")

    def get_backups(self):
        """
        List backups.

        Returns:
            list: List of backups
        """
        return self._request("GET", "/api/v1/storage/backups")

    def create_backup(self, **kwargs):
        """
        Create a new backup.

        Args:
            **kwargs: Backup options

        Returns:
            dict: Backup information
        """
        return self._request("POST", "/api/v1/storage/backups", json=kwargs)

    def get_backup(self, backup_id):
        """
        Get backup details.

        Args:
            backup_id (str): Backup ID

        Returns:
            dict: Backup details
        """
        return self._request("GET", f"/api/v1/storage/backups/{backup_id}")

    def delete_backup(self, backup_id):
        """
        Delete a backup.

        Args:
            backup_id (str): Backup ID

        Returns:
            dict: Response data
        """
        return self._request("DELETE", f"/api/v1/storage/backups/{backup_id}")

    def restore(self, **kwargs):
        """
        Restore from a backup.

        Args:
            **kwargs: Restore options

        Returns:
            dict: Restore information
        """
        return self._request("POST", "/api/v1/storage/restore", json=kwargs)

    def get_restore_status(self, restore_id):
        """
        Get restore status.

        Args:
            restore_id (str): Restore ID

        Returns:
            dict: Restore status
        """
        return self._request("GET", f"/api/v1/storage/restore/{restore_id}")
