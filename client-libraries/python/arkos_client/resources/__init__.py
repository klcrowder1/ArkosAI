"""
Resources for the Arkos client library.
"""

from .cameras import CamerasResource
from .events import EventsResource
from .recordings import RecordingsResource
from .health import HealthResource
from .storage import StorageResource
from .system import SystemResource

__all__ = [
    "CamerasResource",
    "EventsResource",
    "RecordingsResource",
    "HealthResource",
    "StorageResource",
    "SystemResource",
]
