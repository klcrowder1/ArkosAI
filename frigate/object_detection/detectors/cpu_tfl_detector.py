"""
CPU TensorFlow Lite Detector for Arkos AI.

This module provides an implementation of the DetectorInterface for CPU-based
TensorFlow Lite object detection.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from frigate.detectors.detector_config import BaseDetectorConfig, InputDTypeEnum
from frigate.object_detection.detector_interface import DetectorInterface
from frigate.object_detection.detector_registry import register_detector
from frigate.object_detection.preprocessing import PreprocessingUtils

# Try to import TFLite runtime, fall back to TensorFlow if not available
try:
    from tflite_runtime.interpreter import Interpreter
except ModuleNotFoundError:
    from tensorflow.lite.python.interpreter import Interpreter

logger = logging.getLogger(__name__)


@register_detector("cpu")
class CpuTflDetector(DetectorInterface):
    """
    CPU-based TensorFlow Lite detector implementation.
    
    This class implements the DetectorInterface for CPU-based TensorFlow Lite
    object detection models.
    """
    
    def __init__(
        self,
        detector_config: BaseDetectorConfig = None,
        labels_path: str = None,
        custom_labels: Dict[int, str] = None,
    ):
        """
        Initialize the CPU TensorFlow Lite detector.
        
        Args:
            detector_config: Configuration for the detector
            labels_path: Path to the labels file
            custom_labels: Custom label mapping to override defaults
        """
        # Call parent constructor
        super().__init__(detector_config, labels_path, custom_labels)
        
        # Store initialization time
        self.initialization_time = time.time()
    
    def _initialize_detector(self) -> None:
        """Initialize the TensorFlow Lite interpreter."""
        try:
            # Get number of threads from config
            num_threads = getattr(self.detector_config, "num_threads", 3)
            
            # Create interpreter
            self.interpreter = Interpreter(
                model_path=self.model_config.path,
                num_threads=num_threads,
            )
            
            # Allocate tensors
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.tensor_input_details = self.interpreter.get_input_details()
            self.tensor_output_details = self.interpreter.get_output_details()
            
            logger.info(
                f"Initialized CPU TFLite detector with model: {self.model_config.path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize CPU TFLite detector: {str(e)}")
            raise
    
    def preprocess_input(self, tensor_input: np.ndarray) -> np.ndarray:
        """
        Preprocess the input tensor for the detector.
        
        Args:
            tensor_input: Raw input tensor
            
        Returns:
            Preprocessed tensor ready for the detector
        """
        # Apply preprocessing based on model configuration
        if self.model_config:
            return PreprocessingUtils.preprocess(
                tensor_input,
                self.model_config.width,
                self.model_config.height,
                self.model_config.input_tensor,
                self.model_config.input_pixel_format,
                self.model_config.input_dtype,
            )
        else:
            # Default preprocessing if no model config is available
            return tensor_input
    
    def detect_raw(self, tensor_input: np.ndarray) -> np.ndarray:
        """
        Perform raw detection on the input tensor.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            
        Returns:
            numpy array of shape (N, 6) where each row contains:
            [class_id, confidence, x1, y1, x2, y2]
        """
        try:
            # Preprocess input if needed
            processed_input = self.preprocess_input(tensor_input)
            
            # Set input tensor
            self.interpreter.set_tensor(
                self.tensor_input_details[0]["index"], processed_input
            )
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output tensors
            boxes = self.interpreter.tensor(self.tensor_output_details[0]["index"])()[0]
            class_ids = self.interpreter.tensor(self.tensor_output_details[1]["index"])()[0]
            scores = self.interpreter.tensor(self.tensor_output_details[2]["index"])()[0]
            count = int(
                self.interpreter.tensor(self.tensor_output_details[3]["index"])()[0]
            )
            
            # Format detections
            detections = np.zeros((20, 6), np.float32)
            
            for i in range(min(count, 20)):
                if scores[i] < 0.4:  # Skip low confidence detections
                    break
                
                detections[i] = [
                    class_ids[i],
                    float(scores[i]),
                    boxes[i][0],
                    boxes[i][1],
                    boxes[i][2],
                    boxes[i][3],
                ]
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            # Return empty detections on error
            return np.zeros((20, 6), np.float32)
    
    def cleanup(self) -> None:
        """Clean up resources used by the detector."""
        # TFLite doesn't require explicit cleanup, but we'll log it
        logger.debug("Cleaning up CPU TFLite detector")
        
        # Clear references to interpreter
        self.interpreter = None
        self.tensor_input_details = None
        self.tensor_output_details = None
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the model used by this detector.
        
        Returns:
            Dictionary containing model information
        """
        info = super().get_model_info()
        
        # Add TFLite-specific information
        if hasattr(self, "interpreter") and self.interpreter is not None:
            input_shape = self.tensor_input_details[0]["shape"]
            info.update({
                "input_shape": input_shape.tolist(),
                "input_type": str(self.tensor_input_details[0]["dtype"]),
                "num_threads": getattr(self.detector_config, "num_threads", 3),
            })
        
        return info
