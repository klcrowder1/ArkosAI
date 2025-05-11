"""
CPU TensorFlow Lite detector for Arkos AI.

This module provides a detector implementation that uses TensorFlow Lite
on the CPU for object detection, with support for multiple models.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import Field
from typing_extensions import Literal

from arkos.detectors.detection_api import DetectionApi
from arkos.detectors.detector_config import BaseDetectorConfig, ModelConfig, ModelTypeEnum
from arkos.object_detection.detector_registry import register_detector

try:
    from tflite_runtime.interpreter import Interpreter
except ModuleNotFoundError:
    from tensorflow.lite.python.interpreter import Interpreter


logger = logging.getLogger(__name__)

DETECTOR_KEY = "cpu"


class CpuDetectorConfig(BaseDetectorConfig):
    """Configuration for CPU TensorFlow Lite detector."""
    
    type: Literal[DETECTOR_KEY]
    num_threads: int = Field(default=3, title="Number of detection threads")


@register_detector(DETECTOR_KEY)
class CpuTflDetector(DetectionApi):
    """
    CPU TensorFlow Lite detector implementation.
    
    This class implements the DetectionApi interface for running object detection
    using TensorFlow Lite on the CPU, with support for multiple models.
    """
    
    type_key = DETECTOR_KEY
    supported_models = [
        ModelTypeEnum.ssd,
        ModelTypeEnum.yolox,
        ModelTypeEnum.yolonas,
        ModelTypeEnum.yologeneric,
    ]

    def __init__(self, detector_config: CpuDetectorConfig, **kwargs):
        """
        Initialize the CPU TensorFlow Lite detector.
        
        Args:
            detector_config: Configuration for the detector
            **kwargs: Additional arguments to pass to the parent class
        """
        # Initialize parent class
        super().__init__(detector_config)
        
        # Store configuration
        self.detector_config = detector_config
        self.num_threads = detector_config.num_threads or 3
        
        # Initialize interpreters for each model
        self.interpreters: Dict[str, Dict] = {}
        self._initialize_interpreters()
    
    def _initialize_interpreters(self) -> None:
        """Initialize TensorFlow Lite interpreters for each model."""
        for model_config in self.detector_config.models:
            if not model_config.path:
                logger.warning(f"No model path specified for model with purpose '{model_config.purpose}'")
                continue
            
            try:
                # Create interpreter
                interpreter = Interpreter(
                    model_path=model_config.path,
                    num_threads=self.num_threads,
                )
                
                # Allocate tensors
                interpreter.allocate_tensors()
                
                # Get input and output details
                input_details = interpreter.get_input_details()
                output_details = interpreter.get_output_details()
                
                # Store interpreter and details
                self.interpreters[model_config.purpose] = {
                    "interpreter": interpreter,
                    "input_details": input_details,
                    "output_details": output_details,
                    "model_config": model_config,
                }
                
                logger.info(f"Initialized TensorFlow Lite interpreter for model with purpose '{model_config.purpose}'")
            except Exception as e:
                logger.error(f"Failed to initialize TensorFlow Lite interpreter for model with purpose '{model_config.purpose}': {str(e)}")
    
    def detect_raw(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """
        Perform raw detection on the input tensor using the specified model.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            model_config: Configuration for the model to use
            
        Returns:
            numpy array of shape (N, 6) where each row contains:
            [class_id, confidence, x1, y1, x2, y2]
        """
        # Get interpreter for the model
        interpreter_data = self.interpreters.get(model_config.purpose)
        
        # If no interpreter for this purpose, try to use the general one
        if interpreter_data is None and model_config.purpose != "general":
            logger.warning(f"No interpreter found for model with purpose '{model_config.purpose}', trying general")
            interpreter_data = self.interpreters.get("general")
        
        # If still no interpreter, return empty detections
        if interpreter_data is None:
            logger.error(f"No interpreter found for model with purpose '{model_config.purpose}'")
            return np.zeros((20, 6), np.float32)
        
        # Get interpreter and details
        interpreter = interpreter_data["interpreter"]
        input_details = interpreter_data["input_details"]
        output_details = interpreter_data["output_details"]
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]["index"], tensor_input)
        
        # Run inference
        interpreter.invoke()
        
        # Get output tensors
        boxes = interpreter.tensor(output_details[0]["index"])()[0]
        class_ids = interpreter.tensor(output_details[1]["index"])()[0]
        scores = interpreter.tensor(output_details[2]["index"])()[0]
        count = int(interpreter.tensor(output_details[3]["index"])()[0])
        
        # Create detections array
        detections = np.zeros((20, 6), np.float32)
        
        # Fill detections array
        for i in range(count):
            if scores[i] < 0.4 or i == 20:
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
    
    def preprocess_input(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """
        Preprocess the input tensor for the detector.
        
        Args:
            tensor_input: Raw input tensor
            model_config: Configuration for the model
            
        Returns:
            Preprocessed tensor ready for the detector
        """
        # Resize input if needed
        if tensor_input.shape[1] != model_config.height or tensor_input.shape[2] != model_config.width:
            # Resize to model input size
            from cv2 import resize, INTER_LINEAR
            tensor_input = resize(
                tensor_input[0], 
                (model_config.width, model_config.height), 
                interpolation=INTER_LINEAR
            )
            tensor_input = np.expand_dims(tensor_input, axis=0)
        
        return tensor_input
    
    def cleanup(self) -> None:
        """Clean up resources used by the detector."""
        # Clear interpreters
        self.interpreters.clear()
        
        logger.info("Cleaned up CPU TensorFlow Lite detector")
