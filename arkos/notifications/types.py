"""Types for notification system."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
import datetime


class NotificationPriorityEnum(str, Enum):
    """Priority levels for notifications."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationTypeEnum(str, Enum):
    """Types of notifications."""

    EVENT = "event"
    ALERT = "alert"
    SYSTEM = "system"
    INFO = "info"


class NotificationData:
    """Base class for notification data."""

    def __init__(
        self,
        id: str,
        title: str,
        message: str,
        timestamp: float,
        notification_type: str,
        priority: str = NotificationPriorityEnum.MEDIUM,
        source: str = "arkos",
        camera: Optional[str] = None,
        event_id: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        clip_path: Optional[str] = None,
        preview_path: Optional[str] = None,
        data: Dict[str, Any] = None,
        recipients: List[str] = None,
        services: List[str] = None,
    ):
        """Initialize notification data.
        
        Args:
            id: Unique identifier for the notification
            title: Title of the notification
            message: Message content of the notification
            timestamp: Timestamp when the notification was created
            notification_type: Type of notification
            priority: Priority level of the notification
            source: Source of the notification
            camera: Camera name if applicable
            event_id: Event ID if applicable
            snapshot_path: Path to snapshot image if available
            clip_path: Path to video clip if available
            preview_path: Path to preview image if available
            data: Additional data for the notification
            recipients: List of recipient identifiers
            services: List of notification services to use
        """
        self.id = id
        self.title = title
        self.message = message
        self.timestamp = timestamp
        self.notification_type = notification_type
        self.priority = priority
        self.source = source
        self.camera = camera
        self.event_id = event_id
        self.snapshot_path = snapshot_path
        self.clip_path = clip_path
        self.preview_path = preview_path
        self.data = data or {}
        self.recipients = recipients or []
        self.services = services or []
        
        # Add creation timestamp to data
        if "created_at" not in self.data:
            self.data["created_at"] = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification data to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "source": self.source,
            "camera": self.camera,
            "event_id": self.event_id,
            "snapshot_path": self.snapshot_path,
            "clip_path": self.clip_path,
            "preview_path": self.preview_path,
            "data": self.data,
            "recipients": self.recipients,
            "services": self.services,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationData':
        """Create notification data from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            timestamp=data["timestamp"],
            notification_type=data["notification_type"],
            priority=data.get("priority", NotificationPriorityEnum.MEDIUM),
            source=data.get("source", "arkos"),
            camera=data.get("camera"),
            event_id=data.get("event_id"),
            snapshot_path=data.get("snapshot_path"),
            clip_path=data.get("clip_path"),
            preview_path=data.get("preview_path"),
            data=data.get("data", {}),
            recipients=data.get("recipients", []),
            services=data.get("services", []),
        )


class EventNotificationData(NotificationData):
    """Notification data for events."""

    def __init__(
        self,
        id: str,
        title: str,
        message: str,
        timestamp: float,
        event_id: str,
        event_type: str,
        camera: str,
        label: str,
        score: float,
        priority: str = NotificationPriorityEnum.MEDIUM,
        snapshot_path: Optional[str] = None,
        clip_path: Optional[str] = None,
        preview_path: Optional[str] = None,
        zones: List[str] = None,
        **kwargs
    ):
        """Initialize event notification data.
        
        Args:
            id: Unique identifier for the notification
            title: Title of the notification
            message: Message content of the notification
            timestamp: Timestamp when the notification was created
            event_id: Event ID
            event_type: Type of event
            camera: Camera name
            label: Object label
            score: Confidence score
            priority: Priority level of the notification
            snapshot_path: Path to snapshot image if available
            clip_path: Path to video clip if available
            preview_path: Path to preview image if available
            zones: List of zones the event occurred in
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            id=id,
            title=title,
            message=message,
            timestamp=timestamp,
            notification_type=NotificationTypeEnum.EVENT,
            priority=priority,
            camera=camera,
            event_id=event_id,
            snapshot_path=snapshot_path,
            clip_path=clip_path,
            preview_path=preview_path,
            data=kwargs.get("data", {}),
            recipients=kwargs.get("recipients", []),
            services=kwargs.get("services", []),
        )
        
        self.event_type = event_type
        self.label = label
        self.score = score
        self.zones = zones or []
        
        # Update data dictionary with event-specific fields
        self.data.update({
            "event_type": event_type,
            "label": label,
            "score": score,
            "zones": zones or [],
            "detection_time": datetime.datetime.fromtimestamp(timestamp).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert event notification data to dictionary."""
        result = super().to_dict()
        result.update({
            "event_type": self.event_type,
            "label": self.label,
            "score": self.score,
            "zones": self.zones,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventNotificationData':
        """Create event notification data from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            timestamp=data["timestamp"],
            event_id=data["event_id"],
            event_type=data["event_type"],
            camera=data["camera"],
            label=data["label"],
            score=data["score"],
            priority=data.get("priority", NotificationPriorityEnum.MEDIUM),
            snapshot_path=data.get("snapshot_path"),
            clip_path=data.get("clip_path"),
            preview_path=data.get("preview_path"),
            zones=data.get("zones", []),
            data=data.get("data", {}),
            recipients=data.get("recipients", []),
            services=data.get("services", []),
        )


class AlertNotificationData(NotificationData):
    """Notification data for alerts."""

    def __init__(
        self,
        id: str,
        title: str,
        message: str,
        timestamp: float,
        alert_type: str,
        severity: str,
        source: str,
        priority: str = NotificationPriorityEnum.HIGH,
        camera: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        **kwargs
    ):
        """Initialize alert notification data.
        
        Args:
            id: Unique identifier for the notification
            title: Title of the notification
            message: Message content of the notification
            timestamp: Timestamp when the notification was created
            alert_type: Type of alert
            severity: Severity of the alert
            source: Source of the alert
            priority: Priority level of the notification
            camera: Camera name if applicable
            snapshot_path: Path to snapshot image if available
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            id=id,
            title=title,
            message=message,
            timestamp=timestamp,
            notification_type=NotificationTypeEnum.ALERT,
            priority=priority,
            source=source,
            camera=camera,
            snapshot_path=snapshot_path,
            data=kwargs.get("data", {}),
            recipients=kwargs.get("recipients", []),
            services=kwargs.get("services", []),
        )
        
        self.alert_type = alert_type
        self.severity = severity
        
        # Update data dictionary with alert-specific fields
        self.data.update({
            "alert_type": alert_type,
            "severity": severity,
            "alert_time": datetime.datetime.fromtimestamp(timestamp).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert notification data to dictionary."""
        result = super().to_dict()
        result.update({
            "alert_type": self.alert_type,
            "severity": self.severity,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertNotificationData':
        """Create alert notification data from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            timestamp=data["timestamp"],
            alert_type=data["alert_type"],
            severity=data["severity"],
            source=data.get("source", "arkos"),
            priority=data.get("priority", NotificationPriorityEnum.HIGH),
            camera=data.get("camera"),
            snapshot_path=data.get("snapshot_path"),
            data=data.get("data", {}),
            recipients=data.get("recipients", []),
            services=data.get("services", []),
        )


class SystemNotificationData(NotificationData):
    """Notification data for system notifications."""

    def __init__(
        self,
        id: str,
        title: str,
        message: str,
        timestamp: float,
        system_type: str,
        component: str,
        priority: str = NotificationPriorityEnum.MEDIUM,
        **kwargs
    ):
        """Initialize system notification data.
        
        Args:
            id: Unique identifier for the notification
            title: Title of the notification
            message: Message content of the notification
            timestamp: Timestamp when the notification was created
            system_type: Type of system notification
            component: System component
            priority: Priority level of the notification
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            id=id,
            title=title,
            message=message,
            timestamp=timestamp,
            notification_type=NotificationTypeEnum.SYSTEM,
            priority=priority,
            source="system",
            data=kwargs.get("data", {}),
            recipients=kwargs.get("recipients", []),
            services=kwargs.get("services", []),
        )
        
        self.system_type = system_type
        self.component = component
        
        # Update data dictionary with system-specific fields
        self.data.update({
            "system_type": system_type,
            "component": component,
            "system_time": datetime.datetime.fromtimestamp(timestamp).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert system notification data to dictionary."""
        result = super().to_dict()
        result.update({
            "system_type": self.system_type,
            "component": self.component,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemNotificationData':
        """Create system notification data from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            timestamp=data["timestamp"],
            system_type=data["system_type"],
            component=data["component"],
            priority=data.get("priority", NotificationPriorityEnum.MEDIUM),
            data=data.get("data", {}),
            recipients=data.get("recipients", []),
            services=data.get("services", []),
        )


# Factory function to create the appropriate notification data object
def create_notification_data(notification_type: str, data: Dict[str, Any]) -> NotificationData:
    """Create notification data object based on notification type."""
    if notification_type == NotificationTypeEnum.EVENT:
        return EventNotificationData.from_dict(data)
    elif notification_type == NotificationTypeEnum.ALERT:
        return AlertNotificationData.from_dict(data)
    elif notification_type == NotificationTypeEnum.SYSTEM:
        return SystemNotificationData.from_dict(data)
    else:
        return NotificationData.from_dict(data)
