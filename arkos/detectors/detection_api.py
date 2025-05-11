import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import numpy as np

from arkos.detectors.detector_config import BaseDetectorConfig, ModelConfig, ModelTypeEnum

logger = logging.getLogger(__name__)


class DetectionApi(ABC):
    """
    Abstract base class for all detector implementations in Arkos AI.
    
    This class defines the contract that all detector implementations must follow.
    It provides common functionality through default implementations and requires
    specific methods to be implemented by subclasses.
    """
    
    type_key: str
    supported_models: List[ModelTypeEnum] = []

    @abstractmethod
    def __init__(self, detector_config: BaseDetectorConfig):
        """
        Initialize the detector with configuration.
        
        Args:
            detector_config: Configuration for the detector
        """
        self.detector_config = detector_config
        self.thresh = 0.4
        
        # Store models by purpose for quick lookup
        self.models_by_purpose: Dict[str, List[ModelConfig]] = {}
        
        # Initialize models
        for model_config in detector_config.models:
            if model_config.purpose not in self.models_by_purpose:
                self.models_by_purpose[model_config.purpose] = []
            self.models_by_purpose[model_config.purpose].append(model_config)
            
        # Sort models by priority within each purpose
        for purpose, models in self.models_by_purpose.items():
            self.models_by_purpose[purpose] = sorted(models, key=lambda m: m.priority)

    @abstractmethod
    def detect_raw(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """
        Perform raw detection on the input tensor using the specified model.
        
        This is the core detection method that must be implemented by all detectors.
        It should return the raw detection results in a standardized format.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            model_config: Configuration for the model to use
            
        Returns:
            numpy array of shape (N, 6) where each row contains:
            [class_id, confidence, x1, y1, x2, y2]
        """
        pass
    
    def detect(
        self, 
        tensor_input: np.ndarray, 
        model_config: ModelConfig,
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection and return processed results.
        
        This method calls detect_raw and processes the results into a standardized format.
        It filters results based on the confidence threshold and converts class IDs to labels.
        
        Args:
            tensor_input: Input tensor with shape matching the model's expected input
            model_config: Configuration for the model to use
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        detections = []
        
        try:
            # Get raw detections
            raw_detections = self.detect_raw(tensor_input, model_config)
            
            # Process raw detections
            for d in raw_detections:
                # Skip invalid class IDs
                if int(d[0]) < 0 or int(d[0]) not in model_config.merged_labelmap:
                    logger.warning(f"Raw detection returned invalid label ID: {d[0]}")
                    continue
                
                # Skip detections below threshold
                if d[1] < threshold:
                    continue
                
                # Add to processed detections
                detections.append(
                    (model_config.merged_labelmap[int(d[0])], float(d[1]), (d[2], d[3], d[4], d[5]))
                )
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
        
        return detections
    
    def detect_with_purpose(
        self, 
        tensor_input: np.ndarray, 
        purpose: str = "general",
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection using a model with the specified purpose.
        
        This method selects the highest priority model for the given purpose
        and performs detection using that model.
        
        Args:
            tensor_input: Input tensor
            purpose: Purpose of the model to use
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        # If no models for the specified purpose, fall back to general
        if purpose not in self.models_by_purpose:
            if purpose != "general" and "general" in self.models_by_purpose:
                logger.warning(f"No models found for purpose '{purpose}', falling back to general")
                purpose = "general"
            else:
                logger.error(f"No models found for purpose '{purpose}'")
                return []
        
        # Get the highest priority model for the purpose
        model_config = self.models_by_purpose[purpose][0]
        
        # Preprocess input for the model
        processed_input = self.preprocess_input(tensor_input, model_config)
        
        # Perform detection
        return self.detect(processed_input, model_config, threshold)
    
    def detect_with_all_models(
        self, 
        tensor_input: np.ndarray, 
        threshold: float = 0.4
    ) -> Dict[str, List[Tuple[str, float, Tuple[float, float, float, float]]]]:
        """
        Perform detection using all available models.
        
        This method runs detection using all models and returns the results
        organized by model purpose.
        
        Args:
            tensor_input: Input tensor
            threshold: Confidence threshold for filtering detections
            
        Returns:
            Dictionary mapping purpose to list of detections
        """
        results = {}
        
        for purpose, models in self.models_by_purpose.items():
            # Use the highest priority model for each purpose
            model_config = models[0]
            
            # Preprocess input for the model
            processed_input = self.preprocess_input(tensor_input, model_config)
            
            # Perform detection
            detections = self.detect(processed_input, model_config, threshold)
            
            results[purpose] = detections
        
        return results
    
    def preprocess_input(self, tensor_input: np.ndarray, model_config: ModelConfig) -> np.ndarray:
        """
        Preprocess the input tensor for the detector.
        
        This method handles common preprocessing steps like normalization,
        channel ordering, and data type conversion.
        
        Args:
            tensor_input: Raw input tensor
            model_config: Configuration for the model
            
        Returns:
            Preprocessed tensor ready for the detector
        """
        # Default implementation does nothing
        return tensor_input
    
    def calculate_grids_strides(self, model_config: ModelConfig, expanded=True) -> None:
        """
        Calculate grids and strides for YOLO-style models.
        
        Args:
            model_config: Configuration for the model
            expanded: Whether to use expanded format
        """
        grids = []
        expanded_strides = []

        # decode and orient predictions
        strides = [8, 16, 32]
        hsizes = [model_config.height // stride for stride in strides]
        wsizes = [model_config.width // stride for stride in strides]

        for hsize, wsize, stride in zip(hsizes, wsizes, strides):
            xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))

            if expanded:
                grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
                grids.append(grid)
                shape = grid.shape[:2]
                expanded_strides.append(np.full((*shape, 1), stride))
            else:
                xv = xv.reshape(1, 1, hsize, wsize)
                yv = yv.reshape(1, 1, hsize, wsize)
                grids.extend(np.concatenate((xv, yv), axis=1).tolist())
                expanded_strides.extend(
                    np.array([stride, stride]).reshape(1, 2, 1, 1).tolist()
                )

        if expanded:
            self.grids = np.concatenate(grids, 1)
            self.expanded_strides = np.concatenate(expanded_strides, 1)
        else:
            self.grids = grids
            self.expanded_strides = expanded_strides
    
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
        models_info = {}
        
        for purpose, models in self.models_by_purpose.items():
            models_info[purpose] = []
            for model_config in models:
                models_info[purpose].append({
                    "width": model_config.width,
                    "height": model_config.height,
                    "type": model_config.model_type,
                    "path": model_config.path,
                    "priority": model_config.priority
                })
        
        return models_info
