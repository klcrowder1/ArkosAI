"""Types for event management."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import datetime


class EventTypeEnum(str, Enum):
    """Types of events that can be detected."""

    TRACKED_OBJECT = "tracked_object"
    AUDIO = "audio"
    API = "api"
    MOTION = "motion"
    CUSTOM = "custom"


class EventStateEnum(str, Enum):
    """States that an event can be in."""

    START = "start"
    UPDATE = "update"
    END = "end"


class EventSeverityEnum(str, Enum):
    """Severity levels for events."""

    ALERT = "alert"
    DETECTION = "detection"
    INFO = "info"


class EventCategoryEnum(str, Enum):
    """Categories for events."""

    SECURITY = "security"
    MONITORING = "monitoring"
    ANALYTICS = "analytics"
    SYSTEM = "system"
    CUSTOM = "custom"


class EventConfidenceEnum(str, Enum):
    """Confidence levels for events."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RegenerateDescriptionEnum(str, Enum):
    """Types of regeneration for event descriptions."""

    THUMBNAILS = "thumbnails"
    SNAPSHOT = "snapshot"


class EventData:
    """Base class for event data."""

    def __init__(
        self,
        id: str,
        camera: str,
        label: str,
        start_time: float,
        end_time: Optional[float] = None,
        has_clip: bool = False,
        has_snapshot: bool = False,
        thumbnail: Optional[str] = None,
        sub_label: Optional[Tuple[str, float]] = None,
        severity: Optional[str] = None,
        zones: List[str] = None,
        data: Dict[str, Any] = None,
        category: Optional[str] = None,
        confidence: Optional[str] = None,
        tags: List[str] = None,
        description: Optional[str] = None,
        source: Optional[str] = None,
        related_events: List[str] = None,
        retention_days: Optional[int] = None,
        metadata: Dict[str, Any] = None,
    ):
        self.id = id
        self.camera = camera
        self.label = label
        self.start_time = start_time
        self.end_time = end_time
        self.has_clip = has_clip
        self.has_snapshot = has_snapshot
        self.thumbnail = thumbnail
        self.sub_label = sub_label
        self.severity = severity
        self.zones = zones or []
        self.data = data or {}
        self.category = category
        self.confidence = confidence
        self.tags = tags or []
        self.description = description
        self.source = source or "arkos"
        self.related_events = related_events or []
        self.retention_days = retention_days
        self.metadata = metadata or {}

        # Add creation timestamp to metadata
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event data to dictionary."""
        return {
            "id": self.id,
            "camera": self.camera,
            "label": self.label,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "has_clip": self.has_clip,
            "has_snapshot": self.has_snapshot,
            "thumbnail": self.thumbnail,
            "sub_label": self.sub_label,
            "severity": self.severity,
            "zones": self.zones,
            "data": self.data,
            "category": self.category,
            "confidence": self.confidence,
            "tags": self.tags,
            "description": self.description,
            "source": self.source,
            "related_events": self.related_events,
            "retention_days": self.retention_days,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventData':
        """Create event data from dictionary."""
        return cls(
            id=data["id"],
            camera=data["camera"],
            label=data["label"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            has_clip=data.get("has_clip", False),
            has_snapshot=data.get("has_snapshot", False),
            thumbnail=data.get("thumbnail"),
            sub_label=data.get("sub_label"),
            severity=data.get("severity"),
            zones=data.get("zones", []),
            data=data.get("data", {}),
            category=data.get("category"),
            confidence=data.get("confidence"),
            tags=data.get("tags", []),
            description=data.get("description"),
            source=data.get("source", "arkos"),
            related_events=data.get("related_events", []),
            retention_days=data.get("retention_days"),
            metadata=data.get("metadata", {}),
        )

    def add_tag(self, tag: str) -> None:
        """Add a tag to the event."""
        if tag not in self.tags:
            self.tags.append(tag)

    def add_related_event(self, event_id: str) -> None:
        """Add a related event to the event."""
        if event_id not in self.related_events:
            self.related_events.append(event_id)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata for the event."""
        self.metadata[key] = value


class TrackedObjectEventData(EventData):
    """Event data for tracked objects."""

    def __init__(
        self,
        id: str,
        camera: str,
        label: str,
        start_time: float,
        box: List[int],
        area: int,
        region: List[int],
        score: float,
        top_score: float,
        frame_time: float,
        current_zones: List[str] = None,
        entered_zones: List[str] = None,
        attributes: Dict[str, float] = None,
        position_changes: int = 0,
        motionless_count: int = 0,
        stationary: bool = False,
        end_time: Optional[float] = None,
        has_clip: bool = False,
        has_snapshot: bool = False,
        thumbnail: Optional[str] = None,
        sub_label: Optional[Tuple[str, float]] = None,
        severity: Optional[str] = None,
        current_estimated_speed: float = 0.0,
        average_estimated_speed: float = 0.0,
        velocity_angle: float = 0.0,
        path_data: List[Tuple[Tuple[float, float], float]] = None,
        recognized_license_plate: Optional[Tuple[str, float]] = None,
        **kwargs
    ):
        super().__init__(
            id=id,
            camera=camera,
            label=label,
            start_time=start_time,
            end_time=end_time,
            has_clip=has_clip,
            has_snapshot=has_snapshot,
            thumbnail=thumbnail,
            sub_label=sub_label,
            severity=severity,
            zones=entered_zones or [],
            data=kwargs.get("data", {}),
        )

        self.box = box
        self.area = area
        self.region = region
        self.score = score
        self.top_score = top_score
        self.frame_time = frame_time
        self.current_zones = current_zones or []
        self.entered_zones = entered_zones or []
        self.attributes = attributes or {}
        self.position_changes = position_changes
        self.motionless_count = motionless_count
        self.stationary = stationary
        self.current_estimated_speed = current_estimated_speed
        self.average_estimated_speed = average_estimated_speed
        self.velocity_angle = velocity_angle
        self.path_data = path_data or []
        self.recognized_license_plate = recognized_license_plate

        # Update data dictionary with object-specific fields
        self.data.update({
            "box": box,
            "region": region,
            "score": score,
            "top_score": top_score,
            "attributes": attributes or {},
            "average_estimated_speed": average_estimated_speed,
            "velocity_angle": velocity_angle,
            "type": "object",
            "path_data": path_data or [],
            "detection_time": datetime.datetime.fromtimestamp(start_time).isoformat(),
            "duration": 0 if end_time is None else end_time - start_time,
        })

        if recognized_license_plate:
            self.data["recognized_license_plate"] = recognized_license_plate[0]
            self.data["recognized_license_plate_score"] = recognized_license_plate[1]

    def to_dict(self) -> Dict[str, Any]:
        """Convert tracked object event data to dictionary."""
        result = super().to_dict()
        result.update({
            "box": self.box,
            "area": self.area,
            "region": self.region,
            "score": self.score,
            "top_score": self.top_score,
            "frame_time": self.frame_time,
            "current_zones": self.current_zones,
            "entered_zones": self.entered_zones,
            "attributes": self.attributes,
            "position_changes": self.position_changes,
            "motionless_count": self.motionless_count,
            "stationary": self.stationary,
            "current_estimated_speed": self.current_estimated_speed,
            "average_estimated_speed": self.average_estimated_speed,
            "velocity_angle": self.velocity_angle,
            "path_data": self.path_data,
            "recognized_license_plate": self.recognized_license_plate,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackedObjectEventData':
        """Create tracked object event data from dictionary."""
        return cls(
            id=data["id"],
            camera=data["camera"],
            label=data["label"],
            start_time=data["start_time"],
            box=data["box"],
            area=data["area"],
            region=data["region"],
            score=data["score"],
            top_score=data["top_score"],
            frame_time=data["frame_time"],
            current_zones=data.get("current_zones", []),
            entered_zones=data.get("entered_zones", []),
            attributes=data.get("attributes", {}),
            position_changes=data.get("position_changes", 0),
            motionless_count=data.get("motionless_count", 0),
            stationary=data.get("stationary", False),
            end_time=data.get("end_time"),
            has_clip=data.get("has_clip", False),
            has_snapshot=data.get("has_snapshot", False),
            thumbnail=data.get("thumbnail"),
            sub_label=data.get("sub_label"),
            severity=data.get("severity"),
            current_estimated_speed=data.get("current_estimated_speed", 0.0),
            average_estimated_speed=data.get("average_estimated_speed", 0.0),
            velocity_angle=data.get("velocity_angle", 0.0),
            path_data=data.get("path_data", []),
            recognized_license_plate=data.get("recognized_license_plate"),
            data=data.get("data", {}),
        )


class AudioEventData(EventData):
    """Event data for audio events."""

    def __init__(
        self,
        id: str,
        camera: str,
        label: str,
        start_time: float,
        score: float,
        end_time: Optional[float] = None,
        has_clip: bool = False,
        has_snapshot: bool = False,
        thumbnail: Optional[str] = None,
        sub_label: Optional[Tuple[str, float]] = None,
        severity: Optional[str] = None,
        dBFS: float = 0.0,
        **kwargs
    ):
        super().__init__(
            id=id,
            camera=camera,
            label=label,
            start_time=start_time,
            end_time=end_time,
            has_clip=has_clip,
            has_snapshot=has_snapshot,
            thumbnail=thumbnail,
            sub_label=sub_label,
            severity=severity,
            data=kwargs.get("data", {}),
        )

        self.score = score
        self.dBFS = dBFS

        # Update data dictionary with audio-specific fields
        self.data.update({
            "type": "audio",
            "score": score,
            "top_score": score,
            "dBFS": dBFS,
            "detection_time": datetime.datetime.fromtimestamp(start_time).isoformat(),
            "duration": 0 if end_time is None else end_time - start_time,
            "audio_type": label,
            "frequency_range": kwargs.get("frequency_range"),
            "audio_source": kwargs.get("audio_source", "microphone"),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert audio event data to dictionary."""
        result = super().to_dict()
        result.update({
            "score": self.score,
            "dBFS": self.dBFS,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioEventData':
        """Create audio event data from dictionary."""
        return cls(
            id=data["id"],
            camera=data["camera"],
            label=data["label"],
            start_time=data["start_time"],
            score=data["score"],
            end_time=data.get("end_time"),
            has_clip=data.get("has_clip", False),
            has_snapshot=data.get("has_snapshot", False),
            thumbnail=data.get("thumbnail"),
            sub_label=data.get("sub_label"),
            severity=data.get("severity"),
            dBFS=data.get("dBFS", 0.0),
            data=data.get("data", {}),
        )


class ApiEventData(EventData):
    """Event data for API-triggered events."""

    def __init__(
        self,
        id: str,
        camera: str,
        label: str,
        start_time: float,
        score: float,
        event_type: str = "api",
        end_time: Optional[float] = None,
        has_clip: bool = False,
        has_snapshot: bool = False,
        thumbnail: Optional[str] = None,
        sub_label: Optional[Tuple[str, float]] = None,
        severity: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            id=id,
            camera=camera,
            label=label,
            start_time=start_time,
            end_time=end_time,
            has_clip=has_clip,
            has_snapshot=has_snapshot,
            thumbnail=thumbnail,
            sub_label=sub_label,
            severity=severity,
            data=kwargs.get("data", {}),
        )

        self.score = score
        self.event_type = event_type

        # Update data dictionary with API-specific fields
        self.data.update({
            "type": event_type,
            "score": score,
            "top_score": score,
            "detection_time": datetime.datetime.fromtimestamp(start_time).isoformat(),
            "duration": 0 if end_time is None else end_time - start_time,
            "api_source": kwargs.get("api_source", "external"),
            "user_id": kwargs.get("user_id"),
            "request_id": kwargs.get("request_id"),
            "trigger_type": kwargs.get("trigger_type", "manual"),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert API event data to dictionary."""
        result = super().to_dict()
        result.update({
            "score": self.score,
            "event_type": self.event_type,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApiEventData':
        """Create API event data from dictionary."""
        return cls(
            id=data["id"],
            camera=data["camera"],
            label=data["label"],
            start_time=data["start_time"],
            score=data["score"],
            event_type=data.get("event_type", "api"),
            end_time=data.get("end_time"),
            has_clip=data.get("has_clip", False),
            has_snapshot=data.get("has_snapshot", False),
            thumbnail=data.get("thumbnail"),
            sub_label=data.get("sub_label"),
            severity=data.get("severity"),
            data=data.get("data", {}),
        )


# Factory function to create the appropriate event data object
def create_event_data(event_type: str, data: Dict[str, Any]) -> EventData:
    """Create event data object based on event type."""
    if event_type == EventTypeEnum.TRACKED_OBJECT:
        return TrackedObjectEventData.from_dict(data)
    elif event_type == EventTypeEnum.AUDIO:
        return AudioEventData.from_dict(data)
    elif event_type == EventTypeEnum.API:
        return ApiEventData.from_dict(data)
    else:
        return EventData.from_dict(data)
