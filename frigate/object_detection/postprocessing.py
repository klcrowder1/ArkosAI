"""
Postprocessing utilities for Arkos AI object detection.

This module provides utilities for postprocessing detection results.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class PostprocessingUtils:
    """
    Utilities for postprocessing detection results.
    
    This class provides methods for common postprocessing tasks such as
    non-maximum suppression, bounding box conversion, and filtering.
    """
    
    @staticmethod
    def non_maximum_suppression(
        boxes: np.ndarray,
        scores: np.ndarray,
        classes: np.ndarray,
        iou_threshold: float = 0.5,
        score_threshold: float = 0.4,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Apply non-maximum suppression to detection results.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            scores: Confidence scores
            classes: Class IDs
            iou_threshold: IoU threshold for NMS
            score_threshold: Score threshold for filtering
            
        Returns:
            Tuple of (filtered_boxes, filtered_scores, filtered_classes)
        """
        # Filter by score threshold
        mask = scores >= score_threshold
        boxes = boxes[mask]
        scores = scores[mask]
        classes = classes[mask]
        
        # If no boxes remain after filtering, return empty arrays
        if len(boxes) == 0:
            return np.array([]), np.array([]), np.array([])
        
        # Initialize list of picked indices
        picked_indices = []
        
        # Process each class separately
        unique_classes = np.unique(classes)
        for cls in unique_classes:
            # Get indices of boxes with this class
            cls_mask = classes == cls
            cls_boxes = boxes[cls_mask]
            cls_scores = scores[cls_mask]
            cls_indices = np.where(cls_mask)[0]
            
            # Sort by score
            order = np.argsort(-cls_scores)
            
            # Process boxes in order of decreasing score
            while order.size > 0:
                # Pick the box with the highest score
                i = order[0]
                picked_indices.append(cls_indices[i])
                
                # If only one box remains, we're done with this class
                if order.size == 1:
                    break
                
                # Get the coordinates of the picked box
                x1 = cls_boxes[i, 0]
                y1 = cls_boxes[i, 1]
                x2 = cls_boxes[i, 2]
                y2 = cls_boxes[i, 3]
                
                # Compute IoU of the picked box with the rest
                xx1 = np.maximum(x1, cls_boxes[order[1:], 0])
                yy1 = np.maximum(y1, cls_boxes[order[1:], 1])
                xx2 = np.minimum(x2, cls_boxes[order[1:], 2])
                yy2 = np.minimum(y2, cls_boxes[order[1:], 3])
                
                w = np.maximum(0.0, xx2 - xx1 + 1)
                h = np.maximum(0.0, yy2 - yy1 + 1)
                
                intersection = w * h
                area1 = (x2 - x1 + 1) * (y2 - y1 + 1)
                area2 = (cls_boxes[order[1:], 2] - cls_boxes[order[1:], 0] + 1) * (
                    cls_boxes[order[1:], 3] - cls_boxes[order[1:], 1] + 1
                )
                iou = intersection / (area1 + area2 - intersection)
                
                # Keep boxes with IoU less than threshold
                inds = np.where(iou <= iou_threshold)[0]
                order = order[inds + 1]
        
        # Return filtered results
        return boxes[picked_indices], scores[picked_indices], classes[picked_indices]
    
    @staticmethod
    def convert_to_corners(boxes: np.ndarray) -> np.ndarray:
        """
        Convert boxes from [x, y, width, height] to [x1, y1, x2, y2] format.
        
        Args:
            boxes: Bounding boxes in format [x, y, width, height]
            
        Returns:
            Bounding boxes in format [x1, y1, x2, y2]
        """
        return np.concatenate(
            [
                boxes[:, 0:2],  # x1, y1
                boxes[:, 0:2] + boxes[:, 2:4],  # x2, y2
            ],
            axis=1,
        )
    
    @staticmethod
    def convert_to_xywh(boxes: np.ndarray) -> np.ndarray:
        """
        Convert boxes from [x1, y1, x2, y2] to [x, y, width, height] format.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            
        Returns:
            Bounding boxes in format [x, y, width, height]
        """
        return np.concatenate(
            [
                boxes[:, 0:2],  # x, y
                boxes[:, 2:4] - boxes[:, 0:2],  # width, height
            ],
            axis=1,
        )
    
    @staticmethod
    def scale_boxes(
        boxes: np.ndarray,
        original_size: Tuple[int, int],
        target_size: Tuple[int, int],
    ) -> np.ndarray:
        """
        Scale boxes from original image size to target image size.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            original_size: Original image size (height, width)
            target_size: Target image size (height, width)
            
        Returns:
            Scaled bounding boxes
        """
        # Calculate scale factors
        y_scale = target_size[0] / original_size[0]
        x_scale = target_size[1] / original_size[1]
        
        # Scale boxes
        scaled_boxes = boxes.copy()
        scaled_boxes[:, 0] *= x_scale  # x1
        scaled_boxes[:, 1] *= y_scale  # y1
        scaled_boxes[:, 2] *= x_scale  # x2
        scaled_boxes[:, 3] *= y_scale  # y2
        
        return scaled_boxes
    
    @staticmethod
    def clip_boxes(boxes: np.ndarray, image_size: Tuple[int, int]) -> np.ndarray:
        """
        Clip boxes to image boundaries.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            image_size: Image size (height, width)
            
        Returns:
            Clipped bounding boxes
        """
        height, width = image_size
        
        # Clip coordinates to image boundaries
        clipped_boxes = boxes.copy()
        clipped_boxes[:, 0] = np.clip(clipped_boxes[:, 0], 0, width - 1)  # x1
        clipped_boxes[:, 1] = np.clip(clipped_boxes[:, 1], 0, height - 1)  # y1
        clipped_boxes[:, 2] = np.clip(clipped_boxes[:, 2], 0, width - 1)  # x2
        clipped_boxes[:, 3] = np.clip(clipped_boxes[:, 3], 0, height - 1)  # y2
        
        return clipped_boxes
    
    @staticmethod
    def filter_detections(
        detections: List[Tuple[str, float, Tuple[float, float, float, float]]],
        min_score: float = 0.4,
        allowed_labels: Optional[List[str]] = None,
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Filter detections based on score and labels.
        
        Args:
            detections: List of detections (label, score, (x1, y1, x2, y2))
            min_score: Minimum score threshold
            allowed_labels: List of allowed labels (if None, all labels are allowed)
            
        Returns:
            Filtered detections
        """
        filtered = []
        
        for detection in detections:
            label, score, bbox = detection
            
            # Filter by score
            if score < min_score:
                continue
            
            # Filter by label
            if allowed_labels is not None and label not in allowed_labels:
                continue
            
            filtered.append(detection)
        
        return filtered
    
    @staticmethod
    def format_detections(
        boxes: np.ndarray,
        scores: np.ndarray,
        classes: np.ndarray,
        labels_map: Dict[int, str],
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Format detection results into a standardized format.
        
        Args:
            boxes: Bounding boxes in format [x1, y1, x2, y2]
            scores: Confidence scores
            classes: Class IDs
            labels_map: Mapping from class IDs to labels
            
        Returns:
            List of detections (label, score, (x1, y1, x2, y2))
        """
        detections = []
        
        for i in range(len(boxes)):
            class_id = int(classes[i])
            
            # Skip if class ID is not in labels map
            if class_id not in labels_map:
                logger.warning(f"Class ID {class_id} not found in labels map")
                continue
            
            label = labels_map[class_id]
            score = float(scores[i])
            bbox = tuple(float(x) for x in boxes[i])
            
            detections.append((label, score, bbox))
        
        return detections
    
    @staticmethod
    def merge_detections(
        detections1: List[Tuple[str, float, Tuple[float, float, float, float]]],
        detections2: List[Tuple[str, float, Tuple[float, float, float, float]]],
        iou_threshold: float = 0.5,
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Merge two sets of detections, removing duplicates.
        
        Args:
            detections1: First set of detections
            detections2: Second set of detections
            iou_threshold: IoU threshold for considering detections as duplicates
            
        Returns:
            Merged detections
        """
        # Combine detections
        all_detections = detections1 + detections2
        
        # Extract components
        labels = [d[0] for d in all_detections]
        scores = np.array([d[1] for d in all_detections])
        boxes = np.array([d[2] for d in all_detections])
        
        # Create class IDs (using label strings as keys)
        unique_labels = list(set(labels))
        label_to_id = {label: i for i, label in enumerate(unique_labels)}
        classes = np.array([label_to_id[label] for label in labels])
        
        # Apply NMS
        filtered_boxes, filtered_scores, filtered_classes = PostprocessingUtils.non_maximum_suppression(
            boxes, scores, classes, iou_threshold
        )
        
        # Convert back to original format
        merged_detections = []
        for i in range(len(filtered_boxes)):
            label = unique_labels[int(filtered_classes[i])]
            score = float(filtered_scores[i])
            bbox = tuple(float(x) for x in filtered_boxes[i])
            merged_detections.append((label, score, bbox))
        
        return merged_detections
