from enum import Enum
from typing import TypedDict

from arkos.camera import CameraMetrics
from arkos.data_processing.types import DataProcessorMetrics
from arkos.object_detection.base import ObjectDetectProcess


class StatsTrackingTypes(TypedDict):
    camera_metrics: dict[str, CameraMetrics]
    embeddings_metrics: DataProcessorMetrics | None
    detectors: dict[str, ObjectDetectProcess]
    started: int
    latest_arkos_version: str
    last_updated: int
    processes: dict[str, int]


class ModelStatusTypesEnum(str, Enum):
    not_downloaded = "not_downloaded"
    downloading = "downloading"
    downloaded = "downloaded"
    error = "error"


class TrackedObjectUpdateTypesEnum(str, Enum):
    description = "description"
    face = "face"
    lpr = "lpr"
