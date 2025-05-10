#!/usr/bin/env python3
"""
Test script for the Arkos AI object detection framework.

This script demonstrates how to use the object detection framework to
perform object detection on a sample image.
"""

import argparse
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from frigate.detectors.detector_config import BaseDetectorConfig, ModelConfig
from frigate.object_detection import (
    DetectionPipeline,
    DetectorRegistry,
    create_detector,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_detector")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test object detection framework")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to the model file",
    )
    parser.add_argument(
        "--labels",
        type=str,
        default="/labelmap.txt",
        help="Path to the labels file",
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the input image",
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="cpu",
        help="Detector type (e.g., cpu, edgetpu, openvino)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=320,
        help="Model input width",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=320,
        help="Model input height",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.4,
        help="Detection threshold",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.jpg",
        help="Path to the output image",
    )
    return parser.parse_args()


def create_detector_config(args) -> BaseDetectorConfig:
    """Create detector configuration from command line arguments."""
    # Create model configuration
    model_config = ModelConfig(
        path=args.model,
        labelmap_path=args.labels,
        width=args.width,
        height=args.height,
    )
    
    # Create detector configuration
    detector_config = BaseDetectorConfig(
        type=args.detector,
        model=model_config,
    )
    
    return detector_config


def load_image(image_path: str, width: int, height: int) -> np.ndarray:
    """Load and preprocess an image for object detection."""
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize image to model input size
    resized = cv2.resize(image, (width, height))
    
    # Add batch dimension
    tensor = np.expand_dims(resized, axis=0)
    
    return tensor


def draw_detections(
    image: np.ndarray,
    detections: List[Tuple[str, float, Tuple[float, float, float, float]]],
    threshold: float = 0.4,
) -> np.ndarray:
    """Draw detection results on the image."""
    # Make a copy of the image
    output = image.copy()
    
    # Get image dimensions
    height, width = output.shape[:2]
    
    # Draw each detection
    for label, score, bbox in detections:
        if score < threshold:
            continue
        
        # Convert normalized coordinates to pixel coordinates
        y1, x1, y2, x2 = bbox
        x1 = int(x1 * width)
        y1 = int(y1 * height)
        x2 = int(x2 * width)
        y2 = int(y2 * height)
        
        # Draw bounding box
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label and score
        text = f"{label}: {score:.2f}"
        cv2.putText(
            output,
            text,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    
    return output


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Check if files exist
    if not os.path.isfile(args.model):
        logger.error(f"Model file not found: {args.model}")
        return 1
    
    if not os.path.isfile(args.image):
        logger.error(f"Image file not found: {args.image}")
        return 1
    
    try:
        # Create detector configuration
        detector_config = create_detector_config(args)
        
        # Log available detectors
        available_detectors = DetectorRegistry.get_available_detectors()
        logger.info(f"Available detectors: {', '.join(available_detectors)}")
        
        # Check if requested detector is available
        if args.detector not in available_detectors:
            logger.error(f"Detector not available: {args.detector}")
            return 1
        
        # Create detection pipeline
        logger.info(f"Creating detection pipeline with {args.detector} detector")
        pipeline = DetectionPipeline(
            detector_config=detector_config,
            labels_path=args.labels,
        )
        
        # Load image
        logger.info(f"Loading image: {args.image}")
        image = cv2.imread(args.image)
        if image is None:
            logger.error(f"Failed to load image: {args.image}")
            return 1
        
        # Prepare input tensor
        tensor = load_image(args.image, args.width, args.height)
        
        # Perform detection
        logger.info("Performing detection")
        start_time = time.time()
        detections = pipeline.detect(tensor, threshold=args.threshold)
        end_time = time.time()
        
        # Log detection results
        logger.info(f"Detection took {end_time - start_time:.4f} seconds")
        logger.info(f"Found {len(detections)} objects")
        for label, score, bbox in detections:
            logger.info(f"  {label}: {score:.4f} at {bbox}")
        
        # Draw detections on image
        output = draw_detections(image, detections, threshold=args.threshold)
        
        # Save output image
        logger.info(f"Saving output image: {args.output}")
        cv2.imwrite(args.output, output)
        
        # Clean up
        pipeline.cleanup()
        
        logger.info("Done")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
