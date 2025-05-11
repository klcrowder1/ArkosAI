"""Tiered storage management for Arkos AI."""

import datetime
import logging
import os
import shutil
import threading
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from peewee import fn

from arkos.config import ArkosConfig, RetainModeEnum
from arkos.const import RECORD_DIR
from arkos.models import Event, Recordings
from arkos.util.builtin import clear_and_unlink

logger = logging.getLogger(__name__)


class StorageTierType(str, Enum):
    """Storage tier types."""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class StorageTier:
    """Storage tier configuration."""

    def __init__(
        self,
        name: str,
        path: str,
        tier_type: StorageTierType,
        priority: int,
        min_age_days: int = 0,
        max_age_days: Optional[int] = None,
        min_free_space_mb: int = 1000,
        readonly: bool = False,
        events_only: bool = False,
    ) -> None:
        """Initialize a storage tier.

        Args:
            name: Name of the storage tier
            path: Path to the storage location
            tier_type: Type of storage tier
            priority: Priority of the tier (lower is higher priority)
            min_age_days: Minimum age of recordings in days to be stored in this tier
            max_age_days: Maximum age of recordings in days to be stored in this tier
            min_free_space_mb: Minimum free space in MB to maintain on this tier
            readonly: Whether this tier is read-only
            events_only: Whether this tier should only store event recordings
        """
        self.name = name
        self.path = path
        self.tier_type = tier_type
        self.priority = priority
        self.min_age_days = min_age_days
        self.max_age_days = max_age_days
        self.min_free_space_mb = min_free_space_mb
        self.readonly = readonly
        self.events_only = events_only

        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)

    def get_free_space_mb(self) -> float:
        """Get the free space in MB for this tier."""
        try:
            return round(shutil.disk_usage(self.path).free / pow(2, 20), 1)
        except FileNotFoundError:
            logger.error(f"Storage tier path not found: {self.path}")
            return 0

    def get_total_space_mb(self) -> float:
        """Get the total space in MB for this tier."""
        try:
            return round(shutil.disk_usage(self.path).total / pow(2, 20), 1)
        except FileNotFoundError:
            logger.error(f"Storage tier path not found: {self.path}")
            return 0

    def get_used_space_mb(self) -> float:
        """Get the used space in MB for this tier."""
        try:
            usage = shutil.disk_usage(self.path)
            return round((usage.total - usage.free) / pow(2, 20), 1)
        except FileNotFoundError:
            logger.error(f"Storage tier path not found: {self.path}")
            return 0

    def get_usage_percent(self) -> float:
        """Get the usage percentage for this tier."""
        try:
            usage = shutil.disk_usage(self.path)
            return round((usage.total - usage.free) / usage.total * 100, 1)
        except FileNotFoundError:
            logger.error(f"Storage tier path not found: {self.path}")
            return 0
        except ZeroDivisionError:
            return 0

    def needs_cleanup(self) -> bool:
        """Check if this tier needs cleanup."""
        return self.get_free_space_mb() < self.min_free_space_mb

    def can_store(self, recording_age_days: float, is_event: bool = False) -> bool:
        """Check if this tier can store a recording of the given age.

        Args:
            recording_age_days: Age of the recording in days
            is_event: Whether the recording is an event recording

        Returns:
            Whether this tier can store the recording
        """
        if self.readonly:
            return False

        if self.events_only and not is_event:
            return False

        if self.min_age_days > recording_age_days:
            return False

        if self.max_age_days is not None and recording_age_days > self.max_age_days:
            return False

        return True

    def __str__(self) -> str:
        return f"StorageTier({self.name}, {self.tier_type}, {self.path}, priority={self.priority})"

    def __repr__(self) -> str:
        return self.__str__()


class TieredStorageManager(threading.Thread):
    """Manage tiered storage for recordings."""

    def __init__(
        self, config: ArkosConfig, stop_event, check_interval: int = 3600
    ) -> None:
        """Initialize the tiered storage manager.

        Args:
            config: Arkos configuration
            stop_event: Event to signal thread to stop
            check_interval: Interval in seconds to check for recordings to move
        """
        super().__init__(name="tiered_storage_manager")
        self.config = config
        self.stop_event = stop_event
        self.check_interval = check_interval
        self.tiers: List[StorageTier] = []
        self._initialize_tiers()

    def _initialize_tiers(self) -> None:
        """Initialize storage tiers from configuration."""
        # Always add the default tier
        default_tier = StorageTier(
            name="default",
            path=RECORD_DIR,
            tier_type=StorageTierType.HOT,
            priority=0,
            min_age_days=0,
            max_age_days=None,
            min_free_space_mb=1000,
            readonly=False,
            events_only=False,
        )
        self.tiers.append(default_tier)

        # Add tiers from configuration
        global_tiers = self.config.record.tiered_storage.get("tiers", [])
        for tier_config in global_tiers:
            tier = StorageTier(
                name=tier_config.get("name", "unnamed"),
                path=tier_config.get("path", ""),
                tier_type=StorageTierType(tier_config.get("type", "warm")),
                priority=tier_config.get("priority", 100),
                min_age_days=tier_config.get("min_age_days", 7),
                max_age_days=tier_config.get("max_age_days"),
                min_free_space_mb=tier_config.get("min_free_space_mb", 1000),
                readonly=tier_config.get("readonly", False),
                events_only=tier_config.get("events_only", False),
            )
            self.tiers.append(tier)

        # Sort tiers by priority
        self.tiers.sort(key=lambda t: t.priority)
        logger.info(f"Initialized {len(self.tiers)} storage tiers")

    def get_tier_for_recording(
        self, recording_age_days: float, is_event: bool = False
    ) -> Optional[StorageTier]:
        """Get the appropriate tier for a recording of the given age.

        Args:
            recording_age_days: Age of the recording in days
            is_event: Whether the recording is an event recording

        Returns:
            The appropriate storage tier, or None if no tier is suitable
        """
        for tier in self.tiers:
            if tier.can_store(recording_age_days, is_event):
                return tier
        return None

    def get_tier_for_path(self, path: str) -> Optional[StorageTier]:
        """Get the tier that contains the given path.

        Args:
            path: Path to check

        Returns:
            The storage tier containing the path, or None if not found
        """
        for tier in self.tiers:
            if path.startswith(tier.path):
                return tier
        return None

    def move_recording_to_tier(
        self, recording: Recordings, tier: StorageTier
    ) -> Optional[str]:
        """Move a recording to a different storage tier.

        Args:
            recording: Recording to move
            tier: Tier to move the recording to

        Returns:
            New path of the recording, or None if the move failed
        """
        if not os.path.exists(recording.path):
            logger.warning(f"Recording path not found: {recording.path}")
            return None

        # Get the relative path from the base recording directory
        rel_path = os.path.relpath(recording.path, RECORD_DIR)
        new_path = os.path.join(tier.path, rel_path)

        # Create the directory structure if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        try:
            # Copy the file to the new location
            shutil.copy2(recording.path, new_path)

            # Verify the copy was successful
            if os.path.exists(new_path) and os.path.getsize(new_path) == os.path.getsize(
                recording.path
            ):
                # Remove the original file
                os.remove(recording.path)
                logger.debug(
                    f"Moved recording {recording.id} from {recording.path} to {new_path}"
                )
                return new_path
            else:
                logger.error(
                    f"Failed to copy recording {recording.id} to {new_path}: size mismatch"
                )
                # Clean up the partial copy
                if os.path.exists(new_path):
                    os.remove(new_path)
                return None
        except Exception as e:
            logger.error(f"Failed to move recording {recording.id} to {tier.name}: {e}")
            # Clean up the partial copy
            if os.path.exists(new_path):
                os.remove(new_path)
            return None

    def process_recordings(self) -> None:
        """Process recordings and move them to appropriate tiers."""
        logger.debug("Processing recordings for tiered storage")

        # Get all recordings
        recordings = (
            Recordings.select(
                Recordings.id,
                Recordings.camera,
                Recordings.path,
                Recordings.start_time,
                Recordings.end_time,
                Recordings.segment_size,
            )
            .order_by(Recordings.start_time.asc())
            .namedtuples()
        )

        # Get all events with retain_indefinitely=True
        events = (
            Event.select(Event.id, Event.start_time, Event.end_time, Event.camera)
            .where(Event.retain_indefinitely == True)
            .namedtuples()
        )

        # Create a lookup of event recordings by camera and time range
        event_recordings: Dict[str, List[Tuple[float, float]]] = {}
        for event in events:
            if event.camera not in event_recordings:
                event_recordings[event.camera] = []
            event_recordings[event.camera].append((event.start_time, event.end_time))

        now = datetime.datetime.now().timestamp()
        moved_count = 0
        error_count = 0

        for recording in recordings:
            # Skip recordings that don't exist
            if not os.path.exists(recording.path):
                continue

            # Calculate the age of the recording in days
            age_days = (now - recording.end_time) / (24 * 60 * 60)

            # Check if this is an event recording
            is_event = False
            if recording.camera in event_recordings:
                for start_time, end_time in event_recordings[recording.camera]:
                    # If the recording overlaps with an event, it's an event recording
                    if (
                        end_time is None
                        or end_time >= recording.start_time
                        and start_time <= recording.end_time
                    ):
                        is_event = True
                        break

            # Get the current tier for this recording
            current_tier = self.get_tier_for_path(recording.path)
            if current_tier is None:
                logger.warning(
                    f"Recording {recording.id} is not in any known tier: {recording.path}"
                )
                continue

            # Get the appropriate tier for this recording
            target_tier = self.get_tier_for_recording(age_days, is_event)
            if target_tier is None:
                logger.warning(
                    f"No suitable tier found for recording {recording.id} with age {age_days} days"
                )
                continue

            # If the recording is already in the right tier, skip it
            if current_tier == target_tier:
                continue

            # If the target tier has higher priority (lower number), skip it
            # We only want to move recordings to lower priority tiers as they age
            if target_tier.priority < current_tier.priority:
                continue

            # Move the recording to the target tier
            new_path = self.move_recording_to_tier(recording, target_tier)
            if new_path:
                # Update the recording path in the database
                Recordings.update(path=new_path).where(
                    Recordings.id == recording.id
                ).execute()
                moved_count += 1
            else:
                error_count += 1

        logger.info(
            f"Tiered storage processing complete: moved {moved_count} recordings, {error_count} errors"
        )

    def cleanup_tiers(self) -> None:
        """Clean up storage tiers that are running low on space."""
        for tier in self.tiers:
            if tier.needs_cleanup():
                logger.info(
                    f"Storage tier {tier.name} needs cleanup: {tier.get_free_space_mb()} MB free, minimum {tier.min_free_space_mb} MB"
                )
                self.cleanup_tier(tier)

    def cleanup_tier(self, tier: StorageTier) -> None:
        """Clean up a specific storage tier.

        Args:
            tier: Tier to clean up
        """
        # Get recordings in this tier, ordered by start time (oldest first)
        recordings = (
            Recordings.select(
                Recordings.id,
                Recordings.camera,
                Recordings.path,
                Recordings.start_time,
                Recordings.end_time,
                Recordings.segment_size,
            )
            .where(fn.substr(Recordings.path, 1, len(tier.path)) == tier.path)
            .order_by(Recordings.start_time.asc())
            .namedtuples()
        )

        # Get all events with retain_indefinitely=True
        events = (
            Event.select(Event.id, Event.start_time, Event.end_time, Event.camera)
            .where(Event.retain_indefinitely == True)
            .namedtuples()
        )

        # Create a lookup of event recordings by camera and time range
        event_recordings: Dict[str, List[Tuple[float, float]]] = {}
        for event in events:
            if event.camera not in event_recordings:
                event_recordings[event.camera] = []
            event_recordings[event.camera].append((event.start_time, event.end_time))

        # Calculate how much space we need to free up
        free_space = tier.get_free_space_mb()
        target_free_space = tier.min_free_space_mb
        space_to_free = max(0, target_free_space - free_space)

        logger.info(
            f"Cleaning up tier {tier.name}: need to free {space_to_free} MB to reach target of {target_free_space} MB"
        )

        # If we don't need to free any space, we're done
        if space_to_free <= 0:
            return

        freed_space = 0
        deleted_recordings = set()

        for recording in recordings:
            # Skip recordings that don't exist
            if not os.path.exists(recording.path):
                continue

            # Check if this is an event recording that should be retained
            is_retained_event = False
            if recording.camera in event_recordings:
                for start_time, end_time in event_recordings[recording.camera]:
                    # If the recording overlaps with an event, it's an event recording
                    if (
                        end_time is None
                        or end_time >= recording.start_time
                        and start_time <= recording.end_time
                    ):
                        is_retained_event = True
                        break

            # Skip retained event recordings
            if is_retained_event:
                continue

            # Try to move the recording to a lower priority tier
            current_tier_index = next(
                (i for i, t in enumerate(self.tiers) if t == tier), -1
            )
            if current_tier_index == -1:
                logger.error(f"Tier {tier.name} not found in tier list")
                continue

            # Look for a lower priority tier that can accept this recording
            now = datetime.datetime.now().timestamp()
            age_days = (now - recording.end_time) / (24 * 60 * 60)
            moved = False

            for i in range(current_tier_index + 1, len(self.tiers)):
                target_tier = self.tiers[i]
                if target_tier.can_store(age_days, is_retained_event):
                    new_path = self.move_recording_to_tier(recording, target_tier)
                    if new_path:
                        # Update the recording path in the database
                        Recordings.update(path=new_path).where(
                            Recordings.id == recording.id
                        ).execute()
                        moved = True
                        break

            # If we couldn't move the recording, delete it
            if not moved:
                try:
                    clear_and_unlink(Path(recording.path), missing_ok=False)
                    deleted_recordings.add(recording.id)
                    freed_space += recording.segment_size
                except FileNotFoundError:
                    # File not found, just mark it for deletion from the database
                    deleted_recordings.add(recording.id)

            # If we've freed enough space, we're done
            if freed_space >= space_to_free:
                break

        # Delete the recordings from the database
        if deleted_recordings:
            logger.info(
                f"Deleting {len(deleted_recordings)} recordings from tier {tier.name}, freed {freed_space} MB"
            )
            # Delete in batches to avoid memory issues
            max_deletes = 100000
            deleted_recordings_list = list(deleted_recordings)
            for i in range(0, len(deleted_recordings_list), max_deletes):
                Recordings.delete().where(
                    Recordings.id << deleted_recordings_list[i : i + max_deletes]
                ).execute()

    def run(self) -> None:
        """Run the tiered storage manager."""
        logger.info("Starting tiered storage manager")

        while not self.stop_event.wait(self.check_interval):
            try:
                # Clean up tiers that are running low on space
                self.cleanup_tiers()

                # Process recordings and move them to appropriate tiers
                self.process_recordings()
            except Exception as e:
                logger.error(f"Error in tiered storage manager: {e}")

        logger.info("Exiting tiered storage manager")
