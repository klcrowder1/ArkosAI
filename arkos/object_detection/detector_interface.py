"""
Detector Interface for Arkos AI object detection pipeline.

This module defines the core interface for all object detectors in the Arkos AI system.
It provides a standardized contract that all detector implementations must follow.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from arkos.detectors.detector_config import BaseDetectorConfig, ModelConfig
from arkos.detectors.detection_api import DetectionApi
from arkos.util.builtin import EventsPerSecond, load_labels

logger = logging.getLogger(__name__)


class DetectorInterface(ABC):
    """
    Abstract interface for all object detectors in Arkos AI.
    
    This class defines the contract that all detector implementations must follow.
    It provides common functionality through default implementations and requires
    specific methods to be implemented by subclasses.
    """

    def __init__(
        self,
        detector_config: BaseDetectorConfig = None,
        labels_path: str = None,
        custom_labels: Dict[int, str] = None,
    ):
        """
        Initialize the detector with configuration and labels.
        
        Args:
            detector_config: Configuration for the detector
            labels_path: Path to the labels file
            custom_labels: Custom label mapping to override defaults
        """
        self.fps = EventsPerSecond()
        self.detector_config = detector_config
        
        # Initialize labels
        if custom_labels is not None:
            self.labels = custom_labels
        elif labels_path is not None:
            self.labels = load_labels(labels_path)
        else:
            self.labels = {}
        
        # Track initialization time for performance monitoring
        self.initialization_time = None
        
        # Initialize detector
        self._initialize_detector()
        
    def _initialize_detector(self) -> None:
        """
        Initialize detector-specific resources.
        
        This method should be overridden by subclasses to initialize
        any detector-specific resources such as models, runtime environments, etc.
        The default implementation does nothing.
        """
        pass
    
    @abstractmethod
    def detect(
        self, 
        tensor_input: np.ndarray, 
        purpose: str = "general",
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection on the input tensor.
        
        This method should be implemented by subclasses to perform detection
        using a model with the specified purpose.
        
        Args:
            tensor_input: Input tensor
            purpose: Purpose of the model to use
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        pass
    
    @abstractmethod
    def detect_with_all_models(
        self, 
        tensor_input: np.ndarray, 
        threshold: float = 0.4
    ) -> Dict[str, List[Tuple[str, float, Tuple[float, float, float, float]]]]:
        """
        Perform detection using all available models.
        
        This method should be implemented by subclasses to run detection
        using all models and return the results organized by model purpose.
        
        Args:
            tensor_input: Input tensor
            threshold: Confidence threshold for filtering detections
            
        Returns:
            Dictionary mapping purpose to list of detections
        """
        pass
    
    def cleanup(self) -> None:
        """
        Clean up resources used by the detector.
        
        This method should be called when the detector is no longer needed.
        It should release any resources held by the detector.
        """
        # Default implementation does nothing
        pass
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the models used by this detector.
        
        Returns:
            Dictionary containing model information
        """
        if not self.detector_config or not self.detector_config.models:
            return {"status": "No models configured"}
        
        models_info = {}
        
        for model_config in self.detector_config.models:
            purpose = model_config.purpose
            
            if purpose not in models_info:
                models_info[purpose] = []
            
            models_info[purpose].append({
                "width": model_config.width,
                "height": model_config.height,
                "type": model_config.model_type,
                "path": model_config.path,
                "priority": model_config.priority
            })
        
        return models_info
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.cleanup()


class DetectorAdapter:
    """
    Adapter for DetectionApi implementations.
    
    This class adapts DetectionApi implementations to the DetectorInterface.
    It provides a bridge between the two interfaces, allowing DetectionApi
    implementations to be used with the DetectorInterface.
    """
    
    def __init__(
        self,
        detector: DetectionApi,
        labels_path: str = None,
        custom_labels: Dict[int, str] = None,
    ):
        """
        Initialize the detector adapter.
        
        Args:
            detector: The DetectionApi implementation to adapt
            labels_path: Path to the labels file
            custom_labels: Custom label mapping to override defaults
        """
        self.detector = detector
        self.fps = EventsPerSecond()
        
        # Initialize labels
        if custom_labels is not None:
            self.labels = custom_labels
        elif labels_path is not None:
            self.labels = load_labels(labels_path)
        else:
            self.labels = {}
    
    def detect(
        self, 
        tensor_input: np.ndarray, 
        purpose: str = "general",
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection on the input tensor.
        
        Args:
            tensor_input: Input tensor
            purpose: Purpose of the model to use
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        start_time = time.time()
        
        # Perform detection
        detections = self.detector.detect_with_purpose(tensor_input, purpose, threshold)
        
        # Update FPS counter
        self.fps.update()
        
        # Log detection time if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            detection_time = time.time() - start_time
            logger.debug(f"Detection took {detection_time:.4f} seconds, found {len(detections)} objects")
        
        return detections
    
    def detect_with_all_models(
        self, 
        tensor_input: np.ndarray, 
        threshold: float = 0.4
    ) -> Dict[str, List[Tuple[str, float, Tuple[float, float, float, float]]]]:
        """
        Perform detection using all available models.
        
        Args:
            tensor_input: Input tensor
            threshold: Confidence threshold for filtering detections
            
        Returns:
            Dictionary mapping purpose to list of detections
        """
        start_time = time.time()
        
        # Perform detection
        results = self.detector.detect_with_all_models(tensor_input, threshold)
        
        # Update FPS counter
        self.fps.update()
        
        # Log detection time if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            detection_time = time.time() - start_time
            total_detections = sum(len(detections) for detections in results.values())
            logger.debug(f"Detection with all models took {detection_time:.4f} seconds, found {total_detections} objects")
        
        return results
    
    def cleanup(self) -> None:
        """Clean up resources used by the detector."""
        self.detector.cleanup()
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the models used by this detector.
        
        Returns:
            Dictionary containing model information
        """
        return self.detector.get_model_info()
