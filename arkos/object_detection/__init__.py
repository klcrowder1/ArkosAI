"""
Object Detection module for Arkos AI.

This module provides the object detection functionality for Arkos AI,
including the detection pipeline, detector registry, and detector interface.
"""

from arkos.object_detection.detector_interface import DetectorInterface, DetectorAdapter
from arkos.object_detection.detector_registry import DetectorRegistry, register_detector
from arkos.object_detection.detection_pipeline import DetectionPipeline, DetectionProcess

__all__ = [
    'DetectorInterface',
    'DetectorAdapter',
    'DetectorRegistry',
    'register_detector',
    'DetectionPipeline',
    'DetectionProcess',
]
