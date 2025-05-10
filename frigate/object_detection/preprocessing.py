"""
Preprocessing utilities for Arkos AI object detection.

This module provides utilities for preprocessing input tensors for object detection.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from frigate.detectors.detector_config import InputDTypeEnum, InputTensorEnum, PixelFormatEnum

logger = logging.getLogger(__name__)


class PreprocessingUtils:
    """
    Utilities for preprocessing input tensors for object detection.
    
    This class provides methods for common preprocessing tasks such as
    normalization, channel ordering, and data type conversion.
    """
    
    @staticmethod
    def normalize(tensor: np.ndarray, dtype: InputDTypeEnum = InputDTypeEnum.float) -> np.ndarray:
        """
        Normalize the input tensor.
        
        Args:
            tensor: Input tensor
            dtype: Target data type
            
        Returns:
            Normalized tensor
        """
        if dtype == InputDTypeEnum.float:
            # Normalize to [0, 1]
            return tensor.astype(np.float32) / 255.0
        elif dtype == InputDTypeEnum.float_denorm:
            # Convert to float without normalization
            return tensor.astype(np.float32)
        else:
            # Keep as integer
            return tensor
    
    @staticmethod
    def transpose(tensor: np.ndarray, input_format: InputTensorEnum) -> np.ndarray:
        """
        Transpose the input tensor to the desired format.
        
        Args:
            tensor: Input tensor
            input_format: Target tensor format
            
        Returns:
            Transposed tensor
        """
        if input_format == InputTensorEnum.nchw:
            # NHWC -> NCHW
            return np.transpose(tensor, (0, 3, 1, 2))
        elif input_format == InputTensorEnum.nhwc:
            # Already in NHWC format
            return tensor
        elif input_format == InputTensorEnum.hwnc:
            # NHWC -> HWNC
            return np.transpose(tensor, (1, 2, 0, 3))
        elif input_format == InputTensorEnum.hwcn:
            # NHWC -> HWCN
            return np.transpose(tensor, (1, 2, 3, 0))
        else:
            logger.warning(f"Unknown input format: {input_format}, returning original tensor")
            return tensor
    
    @staticmethod
    def convert_color_format(tensor: np.ndarray, target_format: PixelFormatEnum) -> np.ndarray:
        """
        Convert the color format of the input tensor.
        
        Args:
            tensor: Input tensor
            target_format: Target color format
            
        Returns:
            Tensor with converted color format
        """
        # Assume input is RGB
        if target_format == PixelFormatEnum.rgb:
            # Already in RGB format
            return tensor
        elif target_format == PixelFormatEnum.bgr:
            # RGB -> BGR
            return tensor[..., ::-1]
        elif target_format == PixelFormatEnum.yuv:
            # RGB -> YUV
            # This is a simplified conversion, might need to be improved
            r, g, b = tensor[..., 0], tensor[..., 1], tensor[..., 2]
            y = 0.299 * r + 0.587 * g + 0.114 * b
            u = -0.14713 * r - 0.28886 * g + 0.436 * b
            v = 0.615 * r - 0.51499 * g - 0.10001 * b
            return np.stack([y, u, v], axis=-1)
        else:
            logger.warning(f"Unknown color format: {target_format}, returning original tensor")
            return tensor
    
    @staticmethod
    def resize(tensor: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Resize the input tensor.
        
        Args:
            tensor: Input tensor
            width: Target width
            height: Target height
            
        Returns:
            Resized tensor
        """
        import cv2
        
        # Get current dimensions
        current_height, current_width = tensor.shape[1:3]
        
        # Skip if already the right size
        if current_height == height and current_width == width:
            return tensor
        
        # Resize each image in the batch
        resized = np.zeros((tensor.shape[0], height, width, tensor.shape[3]), dtype=tensor.dtype)
        for i in range(tensor.shape[0]):
            resized[i] = cv2.resize(tensor[i], (width, height))
        
        return resized
    
    @staticmethod
    def preprocess(
        tensor: np.ndarray,
        width: int,
        height: int,
        input_format: InputTensorEnum = InputTensorEnum.nhwc,
        color_format: PixelFormatEnum = PixelFormatEnum.rgb,
        dtype: InputDTypeEnum = InputDTypeEnum.float,
    ) -> np.ndarray:
        """
        Apply all preprocessing steps to the input tensor.
        
        Args:
            tensor: Input tensor
            width: Target width
            height: Target height
            input_format: Target tensor format
            color_format: Target color format
            dtype: Target data type
            
        Returns:
            Preprocessed tensor
        """
        # Resize if needed
        if tensor.shape[1] != height or tensor.shape[2] != width:
            tensor = PreprocessingUtils.resize(tensor, width, height)
        
        # Convert color format
        tensor = PreprocessingUtils.convert_color_format(tensor, color_format)
        
        # Normalize
        tensor = PreprocessingUtils.normalize(tensor, dtype)
        
        # Transpose
        tensor = PreprocessingUtils.transpose(tensor, input_format)
        
        return tensor


def tensor_transform(input_tensor: InputTensorEnum) -> Tuple[int, ...]:
    """
    Get the transpose indices for the given input tensor format.
    
    Args:
        input_tensor: Input tensor format
        
    Returns:
        Tuple of transpose indices
    """
    if input_tensor == InputTensorEnum.nchw:
        return (0, 3, 1, 2)
    elif input_tensor == InputTensorEnum.nhwc:
        return (0, 1, 2, 3)
    elif input_tensor == InputTensorEnum.hwnc:
        return (1, 2, 0, 3)
    elif input_tensor == InputTensorEnum.hwcn:
        return (1, 2, 3, 0)
    else:
        logger.warning(f"Unknown input tensor format: {input_tensor}, using NHWC")
        return (0, 1, 2, 3)
