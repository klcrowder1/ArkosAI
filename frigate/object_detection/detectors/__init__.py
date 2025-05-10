"""
Detector implementations for Arkos AI object detection.

This package contains implementations of the DetectorInterface for various
detector types.
"""

import importlib
import logging
import pkgutil
from typing import List

from frigate.object_detection.detector_registry import DetectorRegistry

logger = logging.getLogger(__name__)


def discover_and_register_detectors() -> List[str]:
    """
    Discover and register all detector implementations in this package.
    
    Returns:
        List of registered detector types
    """
    # Import all modules in this package to trigger registration
    for _, name, _ in pkgutil.iter_modules(__path__, __name__ + "."):
        try:
            importlib.import_module(name)
        except ImportError as e:
            logger.error(f"Error importing detector module {name}: {str(e)}")
    
    # Return list of registered detectors
    return DetectorRegistry.get_available_detectors()


# Automatically discover and register detectors when the package is imported
registered_detectors = discover_and_register_detectors()
logger.info(f"Registered detectors: {', '.join(registered_detectors)}")
