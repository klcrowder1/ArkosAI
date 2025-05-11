"""
Custom Model detector for Arkos AI.

This module provides a detector implementation that supports custom-trained models
with various formats and configurations.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import Field
from typing_extensions import Literal

from arkos.detectors.detection_api import DetectionApi
from arkos.detectors.detector_config import BaseDetectorConfig, ModelConfig, ModelTypeEnum
from arkos.object_detection.detector_registry import register_detector

logger = logging.getLogger(__name__)

DETECTOR_KEY = "custom"


class CustomModelConfig(BaseDetectorConfig):
    """Configuration for Custom Model detector."""
    
    type: Literal[DETECTOR_KEY]
    num_threads: int = Field(default=3, title="Number of detection threads")
    # Custom model specific configuration
    model_format: str = Field(default="tflite", title="Format of the custom model (tflite, onnx, pytorch)")
    custom_preprocessing: Optional[Dict[str, any]] = Field(
        default=None, title="Custom preprocessing configuration"
    )
    custom_postprocessing: Optional[Dict[str, any]] = Field(
        default=None, title="Custom postprocessing configuration"
    )


@register_detector(DETECTOR_KEY)
class CustomModelDetector(DetectionApi):
    """
    Custom Model detector implementation.
    
    This class implements the DetectionApi interface for running object detection
    using custom-trained models in various formats.
    """
    
    type_key = DETECTOR_KEY
    supported_models = [
        ModelTypeEnum.ssd,
        ModelTypeEnum.yolox,
        ModelTypeEnum.yolonas,
        ModelTypeEnum.yologeneric,
        ModelTypeEnum.dfine,
        ModelTypeEnum.rfdetr,
    ]

    def __init__(self, detector_config: CustomModelConfig, **kwargs):
        """
        Initialize the Custom Model detector.
        
        Args:
            detector_config: Configuration for the detector
            **kwargs: Additional arguments to pass to the parent class
        """
        # Initialize parent class
        super().__init__(detector_config)
        
        # Store configuration
        self.detector_config = detector_config
        self.num_threads = detector_config.num_threads or 3
        self.model_format = detector_config.model_format
        self.custom_preprocessing = detector_config.custom_preprocessing or {}
        self.custom_postprocessing = detector_config.custom_postprocessing or {}
        
        # Initialize interpreters for each model
        self.interpreters: Dict[str, Dict] = {}
        self._initialize_interpreters()
    
    def _initialize_interpreters(self) -> None:
        """Initialize interpreters for each model based on the model format."""
        for model_config in self.detector_config.models:
            if not model_config.path:
                logger.warning(f"No model path specified for model with purpose '{model_config.purpose}'")
                continue
            
            try:
                # Check if model file exists
                if not os.path.exists(model_config.path):
                    logger.error(f"Model file not found: {model_config.path}")
                    continue
                
                # Initialize interpreter based on model format
                if self.model_format.lower() == "tflite":
                    self._initialize_tflite_interpreter(model_config)
                elif self.model_format.lower() == "onnx":
                    self._initialize_onnx_interpreter(model_config)
                elif self.model_format.lower() == "pytorch":
                    self._initialize_pytorch_interpreter(model_config)
                else:
                    logger.error(f"Unsupported model format: {self.model_format}")
                    continue
                
                logger.info(f"Initialized interpreter for model with purpose '{model_config.purpose}'")
            except Exception as e:
                logger.error(f"Failed to initialize interpreter for model with purpose '{model_config.purpose}': {str(e)}")
    
    def _initialize_tflite_interpreter(self, model_config: ModelConfig) -> None:
        """Initialize TensorFlow Lite interpreter for the model."""
        try:
            from tflite_runtime.interpreter import Interpreter
        except ModuleNotFoundError:
            from tensorflow.lite.python.interpreter import Interpreter
        
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
            "type": "tflite",
        }
    
    def _initialize_onnx_interpreter(self, model_config: ModelConfig) -> None:
        """Initialize ONNX Runtime interpreter for the model."""
        try:
            import onnxruntime as ort
            
            # Create ONNX Runtime session
            session_options = ort.SessionOptions()
            session_options.intra_op_num_threads = self.num_threads
            session = ort.InferenceSession(
                model_config.path,
                sess_options=session_options,
                providers=["CPUExecutionProvider"],
            )
            
            # Get input and output details
            input_details = session.get_inputs()
            output_details = session.get_outputs()
            
            # Store session and details
            self.interpreters[model_config.purpose] = {
                "interpreter": session,
                "input_details": input_details,
                "output_details": output_details,
                "model_config": model_config,
                "type": "onnx",
            }
        except ImportError:
            logger.error("ONNX Runtime not installed. Please install onnxruntime package.")
        except Exception as e:
            logger.error(f"Failed to initialize ONNX interpreter: {str(e)}")
    
    def _initialize_pytorch_interpreter(self, model_config: ModelConfig) -> None:
        """Initialize PyTorch interpreter for the model."""
        try:
            import torch
            
            # Load PyTorch model
            model = torch.load(model_config.path, map_location=torch.device('cpu'))
            model.eval()
            
            # Store model and details
            self.interpreters[model_config.purpose] = {
                "interpreter": model,
                "model_config": model_config,
                "type": "pytorch",
            }
        except ImportError:
            logger.error("PyTorch not installed. Please install torch package.")
        except Exception as e:
            logger.error(f"Failed to initialize PyTorch interpreter: {str(e)}")
    
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
        
        # Detect based on interpreter type
        interpreter_type = interpreter_data.get("type", "tflite")
        
        if interpreter_type == "tflite":
            return self._detect_tflite(tensor_input, interpreter_data)
        elif interpreter_type == "onnx":
            return self._detect_onnx(tensor_input, interpreter_data)
        elif interpreter_type == "pytorch":
            return self._detect_pytorch(tensor_input, interpreter_data)
        else:
            logger.error(f"Unsupported interpreter type: {interpreter_type}")
            return np.zeros((20, 6), np.float32)
    
    def _detect_tflite(self, tensor_input: np.ndarray, interpreter_data: Dict) -> np.ndarray:
        """Perform detection using TensorFlow Lite interpreter."""
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
    
    def _detect_onnx(self, tensor_input: np.ndarray, interpreter_data: Dict) -> np.ndarray:
        """Perform detection using ONNX Runtime interpreter."""
        # Get interpreter and details
        session = interpreter_data["interpreter"]
        input_details = interpreter_data["input_details"]
        
        # Prepare input
        input_name = input_details[0].name
        input_shape = input_details[0].shape
        
        # Reshape input if needed
        if len(input_shape) == 4 and input_shape[0] == 1:
            # Batch size of 1
            if tensor_input.shape[0] != 1:
                tensor_input = np.expand_dims(tensor_input, axis=0)
        
        # Run inference
        outputs = session.run(None, {input_name: tensor_input})
        
        # Process outputs based on model type
        model_config = interpreter_data["model_config"]
        model_type = model_config.model_type
        
        # Create detections array
        detections = np.zeros((20, 6), np.float32)
        
        # Process outputs based on model type
        if model_type == ModelTypeEnum.ssd:
            # SSD format: [batch, num_detections, 7]
            # Each detection: [image_id, label, score, xmin, ymin, xmax, ymax]
            raw_detections = outputs[0]
            
            for i, detection in enumerate(raw_detections[0]):
                if i == 20:
                    break
                
                class_id = int(detection[1])
                score = float(detection[2])
                
                if score < 0.4:
                    break
                
                detections[i] = [
                    class_id,
                    score,
                    detection[3],  # xmin
                    detection[4],  # ymin
                    detection[5],  # xmax
                    detection[6],  # ymax
                ]
        elif model_type in [ModelTypeEnum.yolox, ModelTypeEnum.yolonas, ModelTypeEnum.yologeneric]:
            # YOLO format: [batch, num_detections, 5 + num_classes]
            # Each detection: [x, y, w, h, obj_conf, class_1_conf, class_2_conf, ...]
            raw_detections = outputs[0]
            
            for i, detection in enumerate(raw_detections[0]):
                if i == 20:
                    break
                
                # Get class ID and confidence
                class_scores = detection[5:]
                class_id = np.argmax(class_scores)
                class_conf = class_scores[class_id]
                obj_conf = detection[4]
                score = float(obj_conf * class_conf)
                
                if score < 0.4:
                    break
                
                # Convert from [x, y, w, h] to [x1, y1, x2, y2]
                x, y, w, h = detection[0:4]
                x1 = x - w / 2
                y1 = y - h / 2
                x2 = x + w / 2
                y2 = y + h / 2
                
                detections[i] = [
                    class_id,
                    score,
                    x1,
                    y1,
                    x2,
                    y2,
                ]
        else:
            logger.warning(f"Unsupported model type for ONNX: {model_type}")
        
        return detections
    
    def _detect_pytorch(self, tensor_input: np.ndarray, interpreter_data: Dict) -> np.ndarray:
        """Perform detection using PyTorch interpreter."""
        try:
            import torch
            
            # Get interpreter and model config
            model = interpreter_data["interpreter"]
            model_config = interpreter_data["model_config"]
            
            # Convert numpy array to torch tensor
            if tensor_input.shape[0] == 1:
                # Already has batch dimension
                input_tensor = torch.from_numpy(tensor_input).float()
            else:
                # Add batch dimension
                input_tensor = torch.from_numpy(np.expand_dims(tensor_input, axis=0)).float()
            
            # Run inference
            with torch.no_grad():
                outputs = model(input_tensor)
            
            # Create detections array
            detections = np.zeros((20, 6), np.float32)
            
            # Process outputs based on model type
            if hasattr(outputs, "xyxy"):
                # YOLOv5 format
                pred = outputs.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, cls]
                
                for i, detection in enumerate(pred):
                    if i == 20:
                        break
                    
                    if detection[4] < 0.4:
                        break
                    
                    detections[i] = [
                        detection[5],  # class_id
                        detection[4],  # confidence
                        detection[0],  # x1
                        detection[1],  # y1
                        detection[2],  # x2
                        detection[3],  # y2
                    ]
            else:
                # Generic format - assume outputs is a list of tensors
                # Try to extract boxes, scores, and class_ids
                boxes = None
                scores = None
                class_ids = None
                
                if isinstance(outputs, dict):
                    # Handle dictionary output format
                    if "boxes" in outputs:
                        boxes = outputs["boxes"].cpu().numpy()
                    if "scores" in outputs:
                        scores = outputs["scores"].cpu().numpy()
                    if "labels" in outputs:
                        class_ids = outputs["labels"].cpu().numpy()
                elif isinstance(outputs, (list, tuple)) and len(outputs) >= 3:
                    # Handle list/tuple output format
                    boxes = outputs[0].cpu().numpy()
                    scores = outputs[1].cpu().numpy()
                    class_ids = outputs[2].cpu().numpy()
                
                if boxes is not None and scores is not None and class_ids is not None:
                    for i, (box, score, class_id) in enumerate(zip(boxes, scores, class_ids)):
                        if i == 20:
                            break
                        
                        if score < 0.4:
                            break
                        
                        detections[i] = [
                            class_id,
                            score,
                            box[0],  # x1
                            box[1],  # y1
                            box[2],  # x2
                            box[3],  # y2
                        ]
                else:
                    logger.warning("Could not extract boxes, scores, and class_ids from PyTorch model output")
            
            return detections
        except Exception as e:
            logger.error(f"Error during PyTorch detection: {str(e)}")
            return np.zeros((20, 6), np.float32)
    
    def preprocess_input(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """
        Preprocess the input tensor for the detector.
        
        Args:
            tensor_input: Raw input tensor
            model_config: Configuration for the model
            
        Returns:
            Preprocessed tensor ready for the detector
        """
        # Apply custom preprocessing if configured
        if self.custom_preprocessing:
            tensor_input = self._apply_custom_preprocessing(tensor_input, model_config)
        
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
        
        # Handle different input tensor formats
        if model_config.input_tensor == "nchw" and tensor_input.shape[3] == 3:
            # Convert from NHWC to NCHW
            tensor_input = np.transpose(tensor_input, (0, 3, 1, 2))
        
        # Handle different pixel formats
        if model_config.input_pixel_format == "bgr" and tensor_input.shape[3] == 3:
            # Convert from RGB to BGR
            tensor_input = tensor_input[..., ::-1]
        
        # Handle different data types
        if model_config.input_dtype == "float":
            # Normalize to [0, 1]
            tensor_input = tensor_input.astype(np.float32) / 255.0
        elif model_config.input_dtype == "float_denorm":
            # Convert to float without normalization
            tensor_input = tensor_input.astype(np.float32)
        
        return tensor_input
    
    def _apply_custom_preprocessing(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """Apply custom preprocessing steps to the input tensor."""
        try:
            # Get preprocessing configuration
            preprocessing_config = self.custom_preprocessing
            
            # Apply mean subtraction if configured
            if "mean" in preprocessing_config:
                mean = np.array(preprocessing_config["mean"], dtype=np.float32)
                tensor_input = tensor_input.astype(np.float32) - mean
            
            # Apply standard deviation division if configured
            if "std" in preprocessing_config:
                std = np.array(preprocessing_config["std"], dtype=np.float32)
                tensor_input = tensor_input.astype(np.float32) / std
            
            # Apply custom normalization if configured
            if "scale" in preprocessing_config:
                scale = preprocessing_config["scale"]
                tensor_input = tensor_input.astype(np.float32) * scale
            
            # Apply custom transformations if configured
            if "transforms" in preprocessing_config:
                transforms = preprocessing_config["transforms"]
                
                for transform in transforms:
                    if transform == "rgb_to_bgr":
                        tensor_input = tensor_input[..., ::-1]
                    elif transform == "hwc_to_chw":
                        tensor_input = np.transpose(tensor_input, (0, 3, 1, 2))
            
            return tensor_input
        except Exception as e:
            logger.error(f"Error during custom preprocessing: {str(e)}")
            return tensor_input
    
    def cleanup(self) -> None:
        """Clean up resources used by the detector."""
        # Clear interpreters
        self.interpreters.clear()
        
        logger.info("Cleaned up Custom Model detector")
