"""
Detector Registry for Arkos AI object detection pipeline.

This module provides a registry for detector implementations, allowing for
dynamic registration and creation of detectors.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Dict, List, Optional, Type

from arkos.detectors.detector_config import BaseDetectorConfig
from arkos.detectors.detection_api import DetectionApi

logger = logging.getLogger(__name__)


class DetectorRegistry:
    """
    Registry for detector implementations.
    
    This class manages the registration of detector implementations and provides
    factory methods for creating detector instances.
    """
    
    _instance = None
    _detectors: Dict[str, Type[DetectionApi]] = {}
    _initialized = False
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DetectorRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        # Only initialize once
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    def register(cls, detector_type: str, detector_class: Type[DetectionApi]) -> None:
        """
        Register a detector implementation.
        
        Args:
            detector_type: The type identifier for the detector
            detector_class: The detector class to register
        """
        if not issubclass(detector_class, DetectionApi):
            raise TypeError(f"Detector class must inherit from DetectionApi: {detector_class.__name__}")
        
        cls._detectors[detector_type] = detector_class
        logger.debug(f"Registered detector: {detector_type} -> {detector_class.__name__}")
    
    @classmethod
    def unregister(cls, detector_type: str) -> None:
        """
        Unregister a detector implementation.
        
        Args:
            detector_type: The type identifier for the detector to unregister
        """
        if detector_type in cls._detectors:
            del cls._detectors[detector_type]
            logger.debug(f"Unregistered detector: {detector_type}")
    
    @classmethod
    def get_detector_class(cls, detector_type: str) -> Optional[Type[DetectionApi]]:
        """
        Get the detector class for a given type.
        
        Args:
            detector_type: The type identifier for the detector
            
        Returns:
            The detector class or None if not found
        """
        return cls._detectors.get(detector_type)
    
    @classmethod
    def create_detector(cls, detector_config: BaseDetectorConfig, **kwargs) -> DetectionApi:
        """
        Create a detector instance based on configuration.
        
        Args:
            detector_config: The detector configuration
            **kwargs: Additional arguments to pass to the detector constructor
            
        Returns:
            An instance of the detector
            
        Raises:
            ValueError: If the detector type is not registered
        """
        detector_type = detector_config.type
        detector_class = cls.get_detector_class(detector_type)
        
        if detector_class is None:
            raise ValueError(f"Detector type not registered: {detector_type}")
        
        try:
            return detector_class(detector_config=detector_config, **kwargs)
        except Exception as e:
            logger.error(f"Error creating detector of type {detector_type}: {str(e)}")
            raise
    
    @classmethod
    def get_available_detectors(cls) -> List[str]:
        """
        Get a list of available detector types.
        
        Returns:
            List of registered detector type identifiers
        """
        return list(cls._detectors.keys())
    
    @classmethod
    def discover_detectors(cls, package_path: str = None) -> None:
        """
        Discover and register detector implementations from a package.
        
        This method scans the specified package for detector implementations
        and registers them automatically.
        
        Args:
            package_path: The package path to scan for detectors
        """
        if package_path is None:
            # Default to the detectors plugins package
            from arkos.detectors import plugins
            package_path = plugins.__path__
            package_name = plugins.__name__
        else:
            # Get the package name from the path
            package_name = os.path.basename(package_path)
        
        logger.debug(f"Discovering detectors in package: {package_name}")
        
        # Iterate through modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules(package_path, f"{package_name}."):
            if is_pkg:
                # Skip packages
                continue
            
            try:
                # Import the module
                module = importlib.import_module(module_name)
                
                # Find detector classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, DetectionApi) and 
                        obj != DetectionApi):
                        
                        # Get the detector type from the class
                        if hasattr(obj, 'type_key'):
                            detector_type = obj.type_key
                            cls.register(detector_type, obj)
                        else:
                            logger.warning(f"Detector class {obj.__name__} has no type_key attribute")
                
            except ImportError as e:
                logger.error(f"Error importing detector module {module_name}: {str(e)}")
            except Exception as e:
                logger.error(f"Error discovering detectors in {module_name}: {str(e)}")
        
        logger.info(f"Discovered {len(cls._detectors)} detector implementations")


# Decorator for registering detector implementations
def register_detector(detector_type: str):
    """
    Decorator for registering detector implementations.
    
    Example:
        @register_detector('my_detector')
        class MyDetector(DetectionApi):
            ...
    
    Args:
        detector_type: The type identifier for the detector
    """
    def decorator(cls):
        DetectorRegistry.register(detector_type, cls)
        return cls
    return decorator
