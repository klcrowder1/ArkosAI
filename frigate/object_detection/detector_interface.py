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

from frigate.detectors.detector_config import BaseDetectorConfig, ModelConfig
from frigate.util.builtin import EventsPerSecond, load_labels

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
        self.model_config = detector_config.model if detector_config else None
        
        # Initialize labels
        if custom_labels is not None:
            self.labels = custom_labels
        elif labels_path is not None:
            self.labels = load_labels(labels_path)
        else:
            self.labels = {}
        
        # Track initialization time for performance monitoring
        self.initialization_time = None
        
        # Initialize detector-specific resources
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
    def detect_raw(self, tensor_input: np.ndarray) -> np.ndarray:
        """
        Perform raw detection on the input tensor.
        
        This is the core detection method that must be implemented by all detectors.
        It should return the raw detection results in a standardized format.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            
        Returns:
            numpy array of shape (N, 6) where each row contains:
            [class_id, confidence, x1, y1, x2, y2]
        """
        pass
    
    def detect(self, tensor_input: np.ndarray, threshold: float = 0.4) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection and return processed results.
        
        This method calls detect_raw and processes the results into a standardized format.
        It filters results based on the confidence threshold and converts class IDs to labels.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        start_time = time.time()
        detections = []
        
        try:
            # Get raw detections
            raw_detections = self.detect_raw(tensor_input)
            
            # Process raw detections
            for d in raw_detections:
                # Skip invalid class IDs
                if int(d[0]) < 0 or int(d[0]) >= len(self.labels):
                    logger.warning(f"Raw detection returned invalid label ID: {d[0]}")
                    continue
                
                # Skip detections below threshold
                if d[1] < threshold:
                    break
                
                # Add to processed detections
                detections.append(
                    (self.labels[int(d[0])], float(d[1]), (d[2], d[3], d[4], d[5]))
                )
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
        
        # Update FPS counter
        self.fps.update()
        
        # Log detection time if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            detection_time = time.time() - start_time
            logger.debug(f"Detection took {detection_time:.4f} seconds, found {len(detections)} objects")
        
        return detections
    
    def preprocess_input(self, tensor_input: np.ndarray) -> np.ndarray:
        """
        Preprocess the input tensor for the detector.
        
        This method handles common preprocessing steps like normalization,
        channel ordering, and data type conversion.
        
        Args:
            tensor_input: Raw input tensor
            
        Returns:
            Preprocessed tensor ready for the detector
        """
        # Default implementation does nothing
        return tensor_input
    
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
        Get information about the model used by this detector.
        
        Returns:
            Dictionary containing model information
        """
        if not self.model_config:
            return {"status": "No model configured"}
        
        return {
            "width": self.model_config.width,
            "height": self.model_config.height,
            "type": self.model_config.model_type,
            "path": self.model_config.path,
            "fps": self.fps.value()
        }
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.cleanup()
