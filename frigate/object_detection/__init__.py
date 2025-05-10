"""
Object Detection Package for Arkos AI.

This package provides a modular and extensible framework for object detection
in the Arkos AI system.
"""

import logging

from frigate.object_detection.detector_interface import DetectorInterface
from frigate.object_detection.detector_registry import (
    DetectorRegistry,
    register_detector,
)
from frigate.object_detection.detection_pipeline import (
    DetectionPipeline,
    DetectionProcess,
    RemoteDetectionClient,
)
from frigate.object_detection.preprocessing import PreprocessingUtils
from frigate.object_detection.postprocessing import PostprocessingUtils

# Import detectors package to trigger registration
from frigate.object_detection import detectors

logger = logging.getLogger(__name__)

__all__ = [
    "DetectorInterface",
    "DetectorRegistry",
    "register_detector",
    "DetectionPipeline",
    "DetectionProcess",
    "RemoteDetectionClient",
    "PreprocessingUtils",
    "PostprocessingUtils",
    "create_detector",
]


def create_detector(detector_config, labels_path=None, custom_labels=None):
    """
    Create a detector instance based on configuration.
    
    This is a convenience function that uses the DetectorRegistry to create
    a detector instance.
    
    Args:
        detector_config: The detector configuration
        labels_path: Path to the labels file
        custom_labels: Custom label mapping to override defaults
        
    Returns:
        An instance of the detector
        
    Raises:
        ValueError: If the detector type is not registered
    """
    return DetectorRegistry.create_detector(
        detector_config=detector_config,
        labels_path=labels_path,
        custom_labels=custom_labels,
    )


# Log available detectors
available_detectors = DetectorRegistry.get_available_detectors()
if available_detectors:
    logger.info(f"Available detectors: {', '.join(available_detectors)}")
else:
    logger.warning("No detectors available. Check detector implementations.")
