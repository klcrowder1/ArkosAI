"""Recovery system for Arkos AI."""

import datetime
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tarfile
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from arkos.config import ArkosConfig
from arkos.const import RECORD_DIR, CLIPS_DIR, EXPORT_DIR
from arkos.models import Event, Recordings, Export
from arkos.notifications.types import NotificationLevel
from arkos.storage.backup import BackupManager, BackupStatus, BackupContentType

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Manage recovery operations for Arkos AI."""

    def __init__(
        self,
        config: ArkosConfig,
        backup_manager: BackupManager,
        notification_manager = None,
    ) -> None:
        """Initialize recovery manager.

        Args:
            config: Arkos configuration
            backup_manager: Backup manager instance
            notification_manager: Notification manager instance
        """
        self.config = config
        self.backup_manager = backup_manager
        self.notification_manager = notification_manager

    def list_available_backups(self) -> Dict[str, List[Dict]]:
        """List all available backups from all destinations.

        Returns:
            Dictionary of backups by destination
        """
        backups_by_destination = {}
        
        for name, destination in self.backup_manager.destinations.items():
            backups = destination.list_backups()
            backups_by_destination[name] = backups
        
        return backups_by_destination

    def get_backup_details(self, backup_id: str) -> Optional[Tuple[Dict, str]]:
        """Get details of a backup.

        Args:
            backup_id: ID of the backup

        Returns:
            Tuple of backup metadata and destination name, or None if not found
        """
        for name, destination in self.backup_manager.destinations.items():
            backups = destination.list_backups()
            for backup in backups:
                if backup.get('id') == backup_id:
                    return (backup, name)
        
        return None

    def restore_backup(
        self,
        backup_id: str,
        content_types: List[BackupContentType] = None,
        restore_path: Optional[str] = None,
    ) -> bool:
        """Restore a backup.

        Args:
            backup_id: ID of the backup to restore
            content_types: List of content types to restore, or None for all
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        # Find the backup
        backup_details = self.get_backup_details(backup_id)
        if not backup_details:
            logger.error(f"Backup {backup_id} not found")
            return False
        
        backup, destination_name = backup_details
        destination = self.backup_manager.destinations[destination_name]
        
        # Get the backup file
        backup_file = destination.get_backup_file(backup_id)
        if not backup_file:
            logger.error(f"Failed to get backup file for {backup_id}")
            return False
        
        # Create a temporary directory for extraction
        temp_dir = os.path.join('/tmp', f"arkos_restore_{backup_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extract the backup
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(path=temp_dir)
            
            # Read the manifest
            manifest_path = os.path.join(temp_dir, 'manifest.json')
            if not os.path.exists(manifest_path):
                logger.error(f"Backup manifest not found in {backup_id}")
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Determine content types to restore
            if content_types is None:
                content_types = [BackupContentType(ct) for ct in manifest.get('content_types', [])]
            
            # Restore each content type
            success = True
            for content_type in content_types:
                if content_type == BackupContentType.CONFIG:
                    success = success and self._restore_config(temp_dir, manifest, restore_path)
                elif content_type == BackupContentType.DATABASE:
                    success = success and self._restore_database(temp_dir, manifest, restore_path)
                elif content_type == BackupContentType.RECORDINGS:
                    success = success and self._restore_recordings(temp_dir, manifest, restore_path)
                elif content_type == BackupContentType.EVENTS:
                    success = success and self._restore_events(temp_dir, manifest, restore_path)
                elif content_type == BackupContentType.EXPORTS:
                    success = success and self._restore_exports(temp_dir, manifest, restore_path)
            
            # Send notification
            if self.notification_manager:
                if success:
                    self.notification_manager.send(
                        "backup_restored",
                        f"Backup {backup.get('name', backup_id)} restored successfully",
                        {"backup_id": backup_id, "content_types": [ct.value for ct in content_types]},
                        level=NotificationLevel.INFO
                    )
                else:
                    self.notification_manager.send(
                        "backup_restore_failed",
                        f"Failed to restore backup {backup.get('name', backup_id)}",
                        {"backup_id": backup_id, "content_types": [ct.value for ct in content_types]},
                        level=NotificationLevel.ERROR
                    )
            
            return success
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}: {e}")
            
            # Send notification
            if self.notification_manager:
                self.notification_manager.send(
                    "backup_restore_failed",
                    f"Failed to restore backup {backup.get('name', backup_id)}: {e}",
                    {"backup_id": backup_id, "error": str(e)},
                    level=NotificationLevel.ERROR
                )
            
            return False
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _restore_config(self, temp_dir: str, manifest: Dict, restore_path: Optional[str] = None) -> bool:
        """Restore configuration files.

        Args:
            temp_dir: Path to the extracted backup
            manifest: Backup manifest
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        try:
            config_dir = os.path.join(temp_dir, 'config')
            if not os.path.exists(config_dir):
                logger.error("Config directory not found in backup")
                return False
            
            # Determine destination path
            dest_path = restore_path or os.path.join(os.path.dirname(self.config.config_file), 'config')
            os.makedirs(dest_path, exist_ok=True)
            
            # Copy configuration files
            for file in os.listdir(config_dir):
                src_file = os.path.join(config_dir, file)
                dst_file = os.path.join(dest_path, file)
                
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, dst_file)
            
            logger.info(f"Restored configuration files to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore configuration files: {e}")
            return False

    def _restore_database(self, temp_dir: str, manifest: Dict, restore_path: Optional[str] = None) -> bool:
        """Restore database.

        Args:
            temp_dir: Path to the extracted backup
            manifest: Backup manifest
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        try:
            db_file = os.path.join(temp_dir, 'database', 'arkos.db')
            if not os.path.exists(db_file):
                logger.error("Database file not found in backup")
                return False
            
            # Determine destination path
            dest_path = restore_path or self.config.database.path
            
            # Stop services that use the database
            # TODO: Implement service stopping
            
            # Copy database file
            shutil.copy2(db_file, dest_path)
            
            # Restart services
            # TODO: Implement service restarting
            
            logger.info(f"Restored database to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False

    def _restore_recordings(self, temp_dir: str, manifest: Dict, restore_path: Optional[str] = None) -> bool:
        """Restore recordings.

        Args:
            temp_dir: Path to the extracted backup
            manifest: Backup manifest
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        try:
            recordings_dir = os.path.join(temp_dir, 'recordings')
            if not os.path.exists(recordings_dir):
                logger.error("Recordings directory not found in backup")
                return False
            
            # Determine destination path
            dest_path = restore_path or RECORD_DIR
            
            # Copy recordings
            for root, dirs, files in os.walk(recordings_dir):
                rel_path = os.path.relpath(root, recordings_dir)
                dest_dir = os.path.join(dest_path, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, file)
                    
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
            
            logger.info(f"Restored recordings to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore recordings: {e}")
            return False

    def _restore_events(self, temp_dir: str, manifest: Dict, restore_path: Optional[str] = None) -> bool:
        """Restore events.

        Args:
            temp_dir: Path to the extracted backup
            manifest: Backup manifest
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        try:
            events_dir = os.path.join(temp_dir, 'events')
            if not os.path.exists(events_dir):
                logger.error("Events directory not found in backup")
                return False
            
            # Determine destination path
            dest_path = restore_path or CLIPS_DIR
            
            # Copy events
            for root, dirs, files in os.walk(events_dir):
                rel_path = os.path.relpath(root, events_dir)
                dest_dir = os.path.join(dest_path, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, file)
                    
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
            
            logger.info(f"Restored events to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore events: {e}")
            return False

    def _restore_exports(self, temp_dir: str, manifest: Dict, restore_path: Optional[str] = None) -> bool:
        """Restore exports.

        Args:
            temp_dir: Path to the extracted backup
            manifest: Backup manifest
            restore_path: Path to restore to, or None for default

        Returns:
            Whether the restoration was successful
        """
        try:
            exports_dir = os.path.join(temp_dir, 'exports')
            if not os.path.exists(exports_dir):
                logger.error("Exports directory not found in backup")
                return False
            
            # Determine destination path
            dest_path = restore_path or EXPORT_DIR
            
            # Copy exports
            for root, dirs, files in os.walk(exports_dir):
                rel_path = os.path.relpath(root, exports_dir)
                dest_dir = os.path.join(dest_path, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, file)
                    
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
            
            logger.info(f"Restored exports to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore exports: {e}")
            return False

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify the integrity of a backup.

        Args:
            backup_id: ID of the backup to verify

        Returns:
            Whether the backup is valid
        """
        # Find the backup
        backup_details = self.get_backup_details(backup_id)
        if not backup_details:
            logger.error(f"Backup {backup_id} not found")
            return False
        
        backup, destination_name = backup_details
        destination = self.backup_manager.destinations[destination_name]
        
        # Get the backup file
        backup_file = destination.get_backup_file(backup_id)
        if not backup_file:
            logger.error(f"Failed to get backup file for {backup_id}")
            return False
        
        try:
            # Check if the file is a valid tarfile
            if not tarfile.is_tarfile(backup_file):
                logger.error(f"Backup file {backup_file} is not a valid tar file")
                return False
            
            # Try to open the tarfile
            with tarfile.open(backup_file, 'r:gz') as tar:
                # Check if the manifest exists
                try:
                    manifest_info = tar.getmember('manifest.json')
                except KeyError:
                    logger.error(f"Backup file {backup_file} does not contain a manifest")
                    return False
                
                # Extract and parse the manifest
                manifest_file = tar.extractfile(manifest_info)
                if not manifest_file:
                    logger.error(f"Failed to extract manifest from {backup_file}")
                    return False
                
                try:
                    manifest = json.loads(manifest_file.read().decode('utf-8'))
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse manifest from {backup_file}")
                    return False
                
                # Check if the manifest contains the required fields
                required_fields = ['id', 'created_at', 'content_types']
                for field in required_fields:
                    if field not in manifest:
                        logger.error(f"Manifest in {backup_file} is missing required field: {field}")
                        return False
                
                # Check if the backup ID matches
                if manifest['id'] != backup_id:
                    logger.error(f"Backup ID in manifest ({manifest['id']}) does not match expected ID ({backup_id})")
                    return False
                
                # Check if the content types are valid
                for content_type in manifest['content_types']:
                    try:
                        BackupContentType(content_type)
                    except ValueError:
                        logger.error(f"Invalid content type in manifest: {content_type}")
                        return False
                
                # Check if the files listed in the manifest exist in the tarfile
                for content_type in manifest['content_types']:
                    if content_type == BackupContentType.CONFIG.value:
                        if not self._verify_directory_exists(tar, 'config'):
                            return False
                    elif content_type == BackupContentType.DATABASE.value:
                        if not self._verify_file_exists(tar, 'database/arkos.db'):
                            return False
                    elif content_type == BackupContentType.RECORDINGS.value:
                        if not self._verify_directory_exists(tar, 'recordings'):
                            return False
                    elif content_type == BackupContentType.EVENTS.value:
                        if not self._verify_directory_exists(tar, 'events'):
                            return False
                    elif content_type == BackupContentType.EXPORTS.value:
                        if not self._verify_directory_exists(tar, 'exports'):
                            return False
            
            # All checks passed
            return True
        except Exception as e:
            logger.error(f"Failed to verify backup {backup_id}: {e}")
            return False

    def _verify_file_exists(self, tar: tarfile.TarFile, path: str) -> bool:
        """Verify that a file exists in a tarfile.

        Args:
            tar: Tarfile to check
            path: Path to the file

        Returns:
            Whether the file exists
        """
        try:
            tar.getmember(path)
            return True
        except KeyError:
            logger.error(f"File {path} not found in backup")
            return False

    def _verify_directory_exists(self, tar: tarfile.TarFile, path: str) -> bool:
        """Verify that a directory exists in a tarfile.

        Args:
            tar: Tarfile to check
            path: Path to the directory

        Returns:
            Whether the directory exists
        """
        for member in tar.getnames():
            if member.startswith(path + '/'):
                return True
        
        logger.error(f"Directory {path} not found in backup")
        return False
