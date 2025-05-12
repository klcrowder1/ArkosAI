"""Backup system for Arkos AI."""

import datetime
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tarfile
import threading
import time
import uuid
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from arkos.config import ArkosConfig
from arkos.const import RECORD_DIR, CLIPS_DIR, EXPORT_DIR
from arkos.models import Event, Recordings, Export
from arkos.notifications.types import NotificationLevel
from arkos.storage.monitor import StorageHealthStatus

logger = logging.getLogger(__name__)


class BackupDestinationType(str, Enum):
    """Backup destination types."""

    LOCAL = "local"
    REMOTE = "remote"
    CLOUD = "cloud"


class BackupContentType(str, Enum):
    """Backup content types."""

    CONFIG = "config"
    DATABASE = "database"
    RECORDINGS = "recordings"
    EVENTS = "events"
    EXPORTS = "exports"
    ALL = "all"


class BackupStatus(str, Enum):
    """Backup status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class BackupVerificationResult:
    """Result of backup verification."""

    def __init__(self) -> None:
        """Initialize backup verification result."""
        self.success = True
        self.errors = []
        self.verified_files = 0
        self.total_files = 0
        self.verified_size = 0
        self.total_size = 0

    def add_error(self, error: str) -> None:
        """Add an error to the verification result."""
        self.errors.append(error)
        self.success = False

    def to_dict(self) -> Dict:
        """Convert verification result to dictionary."""
        return {
            "success": self.success,
            "errors": self.errors,
            "verified_files": self.verified_files,
            "total_files": self.total_files,
            "verified_size": self.verified_size,
            "total_size": self.total_size,
        }


class BackupDestination:
    """Base class for backup destinations."""

    def __init__(
        self,
        name: str,
        path: str,
        destination_type: BackupDestinationType,
        retention_days: int = 30,
        max_backups: int = 10,
    ) -> None:
        """Initialize backup destination.

        Args:
            name: Name of the backup destination
            path: Path to the backup location
            destination_type: Type of backup destination
            retention_days: Number of days to retain backups
            max_backups: Maximum number of backups to keep
        """
        self.name = name
        self.path = path
        self.destination_type = destination_type
        self.retention_days = retention_days
        self.max_backups = max_backups

    def prepare(self) -> bool:
        """Prepare the backup destination.

        Returns:
            Whether the preparation was successful
        """
        try:
            os.makedirs(self.path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to prepare backup destination {self.name}: {e}")
            return False

    def store_backup(self, backup_file: str, metadata: Dict) -> bool:
        """Store a backup file at the destination.

        Args:
            backup_file: Path to the backup file
            metadata: Backup metadata

        Returns:
            Whether the storage was successful
        """
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(self.path, exist_ok=True)

            # Copy the backup file to the destination
            destination_file = os.path.join(self.path, os.path.basename(backup_file))
            shutil.copy2(backup_file, destination_file)

            # Write metadata file
            metadata_file = f"{destination_file}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Failed to store backup at destination {self.name}: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """List all backups at the destination.

        Returns:
            List of backup metadata
        """
        backups = []
        try:
            for file in os.listdir(self.path):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(self.path, file), 'r') as f:
                            metadata = json.load(f)
                            backups.append(metadata)
                    except Exception as e:
                        logger.error(f"Failed to read backup metadata {file}: {e}")
        except Exception as e:
            logger.error(f"Failed to list backups at destination {self.name}: {e}")

        return backups

    def get_backup_file(self, backup_id: str) -> Optional[str]:
        """Get the path to a backup file.

        Args:
            backup_id: ID of the backup

        Returns:
            Path to the backup file, or None if not found
        """
        try:
            for file in os.listdir(self.path):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(self.path, file), 'r') as f:
                            metadata = json.load(f)
                            if metadata.get('id') == backup_id:
                                backup_file = os.path.join(self.path, file.replace('.json', ''))
                                if os.path.exists(backup_file):
                                    return backup_file
                    except Exception as e:
                        logger.error(f"Failed to read backup metadata {file}: {e}")
        except Exception as e:
            logger.error(f"Failed to get backup file at destination {self.name}: {e}")

        return None

    def cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy."""
        try:
            backups = self.list_backups()
            
            # Sort backups by creation time (newest first)
            backups.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            
            # Keep only the most recent max_backups
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    backup_id = backup.get('id')
                    if backup_id:
                        self.delete_backup(backup_id)
            
            # Delete backups older than retention_days
            cutoff_time = datetime.datetime.now().timestamp() - (self.retention_days * 86400)
            for backup in backups:
                if backup.get('created_at', 0) < cutoff_time:
                    backup_id = backup.get('id')
                    if backup_id:
                        self.delete_backup(backup_id)
        except Exception as e:
            logger.error(f"Failed to clean up old backups at destination {self.name}: {e}")

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup.

        Args:
            backup_id: ID of the backup to delete

        Returns:
            Whether the deletion was successful
        """
        try:
            for file in os.listdir(self.path):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(self.path, file), 'r') as f:
                            metadata = json.load(f)
                            if metadata.get('id') == backup_id:
                                # Delete backup file
                                backup_file = os.path.join(self.path, file.replace('.json', ''))
                                if os.path.exists(backup_file):
                                    os.remove(backup_file)
                                
                                # Delete metadata file
                                os.remove(os.path.join(self.path, file))
                                return True
                    except Exception as e:
                        logger.error(f"Failed to read backup metadata {file}: {e}")
        except Exception as e:
            logger.error(f"Failed to delete backup at destination {self.name}: {e}")

        return False


class RemoteBackupDestination(BackupDestination):
    """Remote backup destination using rsync."""

    def __init__(
        self,
        name: str,
        path: str,
        host: str,
        user: str,
        ssh_key: Optional[str] = None,
        retention_days: int = 30,
        max_backups: int = 10,
    ) -> None:
        """Initialize remote backup destination.

        Args:
            name: Name of the backup destination
            path: Path on the remote server
            host: Remote host
            user: Remote user
            ssh_key: Path to SSH key file
            retention_days: Number of days to retain backups
            max_backups: Maximum number of backups to keep
        """
        super().__init__(name, path, BackupDestinationType.REMOTE, retention_days, max_backups)
        self.host = host
        self.user = user
        self.ssh_key = ssh_key

    def prepare(self) -> bool:
        """Prepare the remote backup destination.

        Returns:
            Whether the preparation was successful
        """
        try:
            # Create remote directory
            ssh_cmd = ["ssh"]
            if self.ssh_key:
                ssh_cmd.extend(["-i", self.ssh_key])
            ssh_cmd.extend([f"{self.user}@{self.host}", f"mkdir -p {self.path}"])
            
            process = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to prepare remote backup destination {self.name}: {e}")
            return False

    def store_backup(self, backup_file: str, metadata: Dict) -> bool:
        """Store a backup file at the remote destination.

        Args:
            backup_file: Path to the backup file
            metadata: Backup metadata

        Returns:
            Whether the storage was successful
        """
        try:
            # Write metadata file locally
            metadata_file = f"{backup_file}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Use rsync to copy files to remote destination
            rsync_cmd = ["rsync", "-avz"]
            if self.ssh_key:
                rsync_cmd.extend(["-e", f"ssh -i {self.ssh_key}"])
            
            rsync_cmd.extend([
                backup_file,
                metadata_file,
                f"{self.user}@{self.host}:{self.path}/"
            ])
            
            process = subprocess.run(
                rsync_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up local metadata file
            os.remove(metadata_file)
            
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to store backup at remote destination {self.name}: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """List all backups at the remote destination.

        Returns:
            List of backup metadata
        """
        backups = []
        try:
            # Get list of metadata files from remote server
            ssh_cmd = ["ssh"]
            if self.ssh_key:
                ssh_cmd.extend(["-i", self.ssh_key])
            ssh_cmd.extend([f"{self.user}@{self.host}", f"ls -1 {self.path}/*.json"])
            
            process = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                metadata_files = process.stdout.strip().split('\n')
                for file in metadata_files:
                    if not file:
                        continue
                    
                    # Get metadata content
                    ssh_cmd = ["ssh"]
                    if self.ssh_key:
                        ssh_cmd.extend(["-i", self.ssh_key])
                    ssh_cmd.extend([f"{self.user}@{self.host}", f"cat {file}"])
                    
                    process = subprocess.run(
                        ssh_cmd,
                        capture_output=True,
                        text=True
                    )
                    
                    if process.returncode == 0:
                        try:
                            metadata = json.loads(process.stdout)
                            backups.append(metadata)
                        except Exception as e:
                            logger.error(f"Failed to parse backup metadata {file}: {e}")
        except Exception as e:
            logger.error(f"Failed to list backups at remote destination {self.name}: {e}")

        return backups

    def get_backup_file(self, backup_id: str) -> Optional[str]:
        """Get a backup file from the remote destination.

        Args:
            backup_id: ID of the backup

        Returns:
            Path to the local copy of the backup file, or None if not found
        """
        try:
            # Find the backup metadata file
            for metadata in self.list_backups():
                if metadata.get('id') == backup_id:
                    backup_filename = metadata.get('filename')
                    if backup_filename:
                        # Create a temporary directory for the backup
                        temp_dir = os.path.join('/tmp', f"arkos_backup_{backup_id}")
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # Download the backup file
                        rsync_cmd = ["rsync", "-avz"]
                        if self.ssh_key:
                            rsync_cmd.extend(["-e", f"ssh -i {self.ssh_key}"])
                        
                        remote_path = os.path.join(self.path, backup_filename)
                        local_path = os.path.join(temp_dir, backup_filename)
                        
                        rsync_cmd.extend([
                            f"{self.user}@{self.host}:{remote_path}",
                            local_path
                        ])
                        
                        process = subprocess.run(
                            rsync_cmd,
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode == 0 and os.path.exists(local_path):
                            return local_path
        except Exception as e:
            logger.error(f"Failed to get backup file from remote destination {self.name}: {e}")

        return None

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup from the remote destination.

        Args:
            backup_id: ID of the backup to delete

        Returns:
            Whether the deletion was successful
        """
        try:
            # Find the backup metadata file
            for metadata in self.list_backups():
                if metadata.get('id') == backup_id:
                    backup_filename = metadata.get('filename')
                    if backup_filename:
                        # Delete the backup and metadata files
                        ssh_cmd = ["ssh"]
                        if self.ssh_key:
                            ssh_cmd.extend(["-i", self.ssh_key])
                        
                        backup_path = os.path.join(self.path, backup_filename)
                        metadata_path = f"{backup_path}.json"
                        
                        ssh_cmd.extend([
                            f"{self.user}@{self.host}",
                            f"rm -f {backup_path} {metadata_path}"
                        ])
                        
                        process = subprocess.run(
                            ssh_cmd,
                            capture_output=True,
                            text=True
                        )
                        
                        return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to delete backup from remote destination {self.name}: {e}")

        return False


class CloudBackupDestination(BackupDestination):
    """Cloud backup destination using rclone."""

    def __init__(
        self,
        name: str,
        path: str,
        provider: str,
        rclone_config: str,
        retention_days: int = 30,
        max_backups: int = 10,
    ) -> None:
        """Initialize cloud backup destination.

        Args:
            name: Name of the backup destination
            path: Path in the cloud storage
            provider: Cloud provider name (as configured in rclone)
            rclone_config: Path to rclone config file
            retention_days: Number of days to retain backups
            max_backups: Maximum number of backups to keep
        """
        super().__init__(name, path, BackupDestinationType.CLOUD, retention_days, max_backups)
        self.provider = provider
        self.rclone_config = rclone_config

    def prepare(self) -> bool:
        """Prepare the cloud backup destination.

        Returns:
            Whether the preparation was successful
        """
        try:
            # Check if rclone is installed
            process = subprocess.run(
                ["which", "rclone"],
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                logger.error("rclone is not installed. Please install rclone to use cloud backup destinations.")
                return False
            
            # Check if the provider is configured
            process = subprocess.run(
                ["rclone", "--config", self.rclone_config, "listremotes"],
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0 or self.provider not in process.stdout:
                logger.error(f"Cloud provider {self.provider} is not configured in rclone.")
                return False
            
            # Create the destination directory
            process = subprocess.run(
                ["rclone", "--config", self.rclone_config, "mkdir", f"{self.provider}:{self.path}"],
                capture_output=True,
                text=True
            )
            
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to prepare cloud backup destination {self.name}: {e}")
            return False

    def store_backup(self, backup_file: str, metadata: Dict) -> bool:
        """Store a backup file in the cloud destination.

        Args:
            backup_file: Path to the backup file
            metadata: Backup metadata

        Returns:
            Whether the storage was successful
        """
        try:
            # Write metadata file locally
            metadata_file = f"{backup_file}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Upload backup file
            process = subprocess.run(
                [
                    "rclone", "--config", self.rclone_config,
                    "copy", backup_file, f"{self.provider}:{self.path}/"
                ],
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                logger.error(f"Failed to upload backup file to cloud: {process.stderr}")
                return False
            
            # Upload metadata file
            process = subprocess.run(
                [
                    "rclone", "--config", self.rclone_config,
                    "copy", metadata_file, f"{self.provider}:{self.path}/"
                ],
                capture_output=True,
                text=True
            )
            
            # Clean up local metadata file
            os.remove(metadata_file)
            
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to store backup at cloud destination {self.name}: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """List all backups in the cloud destination.

        Returns:
            List of backup metadata
        """
        backups = []
        try:
            # Create a temporary directory for metadata files
            temp_dir = os.path.join('/tmp', f"arkos_backup_metadata_{int(time.time())}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # List all files in the cloud path
            process = subprocess.run(
                [
                    "rclone", "--config", self.rclone_config,
                    "ls", f"{self.provider}:{self.path}"
                ],
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                # Find metadata files
                for line in process.stdout.strip().split('\n'):
                    if line and '.json' in line:
                        filename = line.split()[-1]
                        
                        # Download metadata file
                        process = subprocess.run(
                            [
                                "rclone", "--config", self.rclone_config,
                                "copy", f"{self.provider}:{self.path}/{filename}", temp_dir
                            ],
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode == 0:
                            # Read metadata
                            local_path = os.path.join(temp_dir, filename)
                            try:
                                with open(local_path, 'r') as f:
                                    metadata = json.load(f)
                                    backups.append(metadata)
                            except Exception as e:
                                logger.error(f"Failed to read backup metadata {filename}: {e}")
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to list backups at cloud destination {self.name}: {e}")

        return backups

    def get_backup_file(self, backup_id: str) -> Optional[str]:
        """Get a backup file from the cloud destination.

        Args:
            backup_id: ID of the backup

        Returns:
            Path to the local copy of the backup file, or None if not found
        """
        try:
            # Find the backup metadata
            for metadata in self.list_backups():
                if metadata.get('id') == backup_id:
                    backup_filename = metadata.get('filename')
                    if backup_filename:
                        # Create a temporary directory for the backup
                        temp_dir = os.path.join('/tmp', f"arkos_backup_{backup_id}")
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # Download the backup file
                        process = subprocess.run(
                            [
                                "rclone", "--config", self.rclone_config,
                                "copy", f"{self.provider}:{self.path}/{backup_filename}", temp_dir
                            ],
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode == 0:
                            local_path = os.path.join(temp_dir, backup_filename)
                            if os.path.exists(local_path):
                                return local_path
        except Exception as e:
            logger.error(f"Failed to get backup file from cloud destination {self.name}: {e}")

        return None

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup from the cloud destination.

        Args:
            backup_id: ID of the backup to delete

        Returns:
            Whether the deletion was successful
        """
        try:
            # Find the backup metadata
            for metadata in self.list_backups():
                if metadata.get('id') == backup_id:
                    backup_filename = metadata.get('filename')
                    if backup_filename:
                        # Delete the backup file
                        process = subprocess.run(
                            [
                                "rclone", "--config", self.rclone_config,
                                "delete", f"{self.provider}:{self.path}/{backup_filename}"
                            ],
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode != 0:
                            logger.error(f"Failed to delete backup file: {process.stderr}")
                            return False
                        
                        # Delete the metadata file
                        process = subprocess.run(
                            [
                                "rclone", "--config", self.rclone_config,
                                "delete", f"{self.provider}:{self.path}/{backup_filename}.json"
                            ],
                            capture_output=True,
                            text=True
                        )
                        
                        return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to delete backup from cloud destination {self.name}: {e}")

        return False


class BackupManager(threading.Thread):
    """Manage backups for Arkos AI."""

    def __init__(
        self,
        config: ArkosConfig,
        stop_event,
        notification_manager = None,
        check_interval: int = 3600,
    ) -> None:
        """Initialize backup manager.

        Args:
            config: Arkos configuration
            stop_event: Event to signal thread to stop
            notification_manager: Notification manager instance
            check_interval: Interval in seconds to check for scheduled backups
        """
        super().__init__(name="backup_manager")
        self.config = config
        self.stop_event = stop_event
        self.notification_manager = notification_manager
        self.check_interval = check_interval
        self.destinations: Dict[str, BackupDestination] = {}
        self.scheduled_backups: List[Dict] = []
        self.backup_history: List[Dict] = []
        self.max_history_entries = 100
        self._initialize_destinations()
        self._initialize_schedules()

    def _initialize_destinations(self) -> None:
        """Initialize backup destinations from configuration."""
        # Add destinations from configuration
        backup_config = self.config.storage.get("backup", {})
        destinations = backup_config.get("destinations", [])
        
        for dest_config in destinations:
            dest_type = dest_config.get("type", "local")
            name = dest_config.get("name", "unnamed")
            path = dest_config.get("path", "")
            retention_days = dest_config.get("retention_days", 30)
            max_backups = dest_config.get("max_backups", 10)
            
            if dest_type == BackupDestinationType.LOCAL:
                destination = BackupDestination(
                    name=name,
                    path=path,
                    destination_type=BackupDestinationType.LOCAL,
                    retention_days=retention_days,
                    max_backups=max_backups,
                )
                self.destinations[name] = destination
            
            elif dest_type == BackupDestinationType.REMOTE:
                host = dest_config.get("host", "")
                user = dest_config.get("user", "")
                ssh_key = dest_config.get("ssh_key")
                
                destination = RemoteBackupDestination(
                    name=name,
                    path=path,
                    host=host,
                    user=user,
                    ssh_key=ssh_key,
                    retention_days=retention_days,
                    max_backups=max_backups,
                )
                self.destinations[name] = destination
            
            elif dest_type == BackupDestinationType.CLOUD:
                provider = dest_config.get("provider", "")
                rclone_config = dest_config.get("rclone_config", "")
                
                destination = CloudBackupDestination(
                    name=name,
                    path=path,
                    provider=provider,
                    rclone_config=rclone_config,
                    retention_days=retention_days,
                    max_backups=max_backups,
                )
                self.destinations[name] = destination
        
        logger.info(f"Initialized {len(self.destinations)} backup destinations")

    def _initialize_schedules(self) -> None:
        """Initialize backup schedules from configuration."""
        backup_config = self.config.storage.get("backup", {})
        schedules = backup_config.get("schedules", [])
        
        for schedule_config in schedules:
            name = schedule_config.get("name", "unnamed")
            destination = schedule_config.get("destination", "")
            content_type = schedule_config.get("content_type", BackupContentType.ALL)
            frequency = schedule_config.get("frequency", "daily")  # daily, weekly, monthly
            time = schedule_config.get("time", "02:00")  # HH:MM format
            day = schedule_config.get("day", 1)  # Day of week (0-6) or day of month (1-31)
            enabled = schedule_config.get("enabled", True)
            
            if enabled and destination in self.destinations:
                self.scheduled_backups.append({
                    "name": name,
                    "destination": destination,
                    "content_type": content_type,
                    "frequency": frequency,
                    "time": time,
                    "day": day,
                    "enabled": enabled,
                    "last_run": 0,
                })
        
        logger.info(f"Initialized {len(self.scheduled_backups)} backup schedules")

    def add_destination(self, destination: BackupDestination) -> None:
        """Add a backup destination.

        Args:
            destination: Backup destination to add
        """
        self.destinations[destination.name] = destination
        logger.info(f"Added backup destination: {destination.name}")

    def remove_destination(self, name: str) -> bool:
        """Remove a backup destination.

        Args:
            name: Name of the destination to remove

        Returns:
            Whether the removal was successful
        """
        if name in self.destinations:
            del self.destinations[name]
            logger.info(f"Removed backup destination: {name}")
            return True
        return False

    def add_schedule(self, schedule: Dict) -> None:
        """Add a backup schedule.

        Args:
            schedule: Backup schedule to add
        """
        self.scheduled_backups.append(schedule)
        logger.info(f"Added backup schedule: {schedule['name']}")

    def remove_schedule(self, name: str) -> bool:
        """Remove a backup schedule.

        Args:
            name: Name of the schedule to remove

        Returns:
            Whether the removal was successful
        """
        for i, schedule in enumerate(self.scheduled_backups):
            if schedule["name"] == name:
                del self.scheduled_backups[i]
                logger.info(f"Removed backup schedule: {name}")
                return True
        return False

    def should_run_schedule(self, schedule: Dict) -> bool:
        """Check if a schedule should be run.

        Args:
            schedule: Backup schedule to check

        Returns:
            Whether the schedule should be run
        """
        now = datetime.datetime.now()
        
        # Parse schedule time
        hour, minute = map(int, schedule["time"].split(":"))
        schedule_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Check if it's time to run the schedule
        if schedule["frequency"] == "daily":
            # Run daily at the specified time
            return (
                now >= schedule_time and
                now < schedule_time + datetime.timedelta(minutes=5) and
                schedule["last_run"] < schedule_time.timestamp()
            )
        
        elif schedule["frequency"] == "weekly":
            # Run weekly on the specified day at the specified time
            if now.weekday() == schedule["day"]:
                return (
                    now >= schedule_time and
                    now < schedule_time + datetime.timedelta(minutes=5) and
                    schedule["last_run"] < schedule_
