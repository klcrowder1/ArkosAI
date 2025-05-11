"""
Detection Pipeline for Arkos AI object detection.

This module provides the orchestration layer for the object detection process,
handling preprocessing, detection, and postprocessing with support for multiple models.
"""

import datetime
import logging
import multiprocessing as mp
import os
import queue
import signal
import threading
import time
from multiprocessing import Queue, Value
from multiprocessing.synchronize import Event as MpEvent
from typing import Dict, List, Optional, Tuple, Union, Set

import numpy as np
from setproctitle import setproctitle

from arkos.detectors.detector_config import BaseDetectorConfig, ModelConfig
from arkos.detectors.detection_api import DetectionApi
from arkos.object_detection.detector_registry import DetectorRegistry
from arkos.util import Process
from arkos.util.builtin import EventsPerSecond
from arkos.util.image import SharedMemoryFrameManager, UntrackedSharedMemory

logger = logging.getLogger(__name__)


class DetectionPipeline:
    """
    Orchestrates the object detection process with support for multiple models.
    
    This class manages the lifecycle of detectors, handles preprocessing and
    postprocessing, and coordinates the detection process across multiple models.
    """
    
    def __init__(
        self,
        detector_config: BaseDetectorConfig,
        labels_path: str = None,
        custom_labels: Dict[int, str] = None,
    ):
        """
        Initialize the detection pipeline.
        
        Args:
            detector_config: Configuration for the detector
            labels_path: Path to the labels file
            custom_labels: Custom label mapping to override defaults
        """
        self.detector_config = detector_config
        self.labels_path = labels_path
        self.custom_labels = custom_labels
        self.detector = None
        self.fps = EventsPerSecond()
        
        # Initialize the detector
        self._initialize_detector()
    
    def _initialize_detector(self) -> None:
        """Initialize the detector based on configuration."""
        try:
            # Create detector using the registry
            self.detector = DetectorRegistry.create_detector(
                detector_config=self.detector_config,
                labels_path=self.labels_path,
                custom_labels=self.custom_labels,
            )
            logger.info(f"Initialized detector of type: {self.detector_config.type}")
            
            # Log information about the models
            model_info = self.detector.get_model_info()
            for purpose, models in model_info.items():
                for i, model in enumerate(models):
                    logger.info(f"Model {i+1} for purpose '{purpose}': {model['path']} ({model['width']}x{model['height']})")
        except Exception as e:
            logger.error(f"Failed to initialize detector: {str(e)}")
            raise
    
    def detect(
        self, 
        tensor_input: np.ndarray, 
        purpose: str = "general",
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection on the input tensor using a model with the specified purpose.
        
        This method handles preprocessing, detection, and postprocessing.
        
        Args:
            tensor_input: Input tensor
            purpose: Purpose of the model to use
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        if self.detector is None:
            logger.error("Detector not initialized")
            return []
        
        try:
            # Perform detection using the model with the specified purpose
            detections = self.detector.detect_with_purpose(tensor_input, purpose, threshold)
            
            # Update FPS counter
            self.fps.update()
            
            return detections
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return []
    
    def detect_with_all_models(
        self, 
        tensor_input: np.ndarray, 
        threshold: float = 0.4
    ) -> Dict[str, List[Tuple[str, float, Tuple[float, float, float, float]]]]:
        """
        Perform detection on the input tensor using all available models.
        
        This method runs detection using all models and returns the results
        organized by model purpose.
        
        Args:
            tensor_input: Input tensor
            threshold: Confidence threshold for filtering detections
            
        Returns:
            Dictionary mapping purpose to list of detections
        """
        if self.detector is None:
            logger.error("Detector not initialized")
            return {}
        
        try:
            # Perform detection using all models
            results = self.detector.detect_with_all_models(tensor_input, threshold)
            
            # Update FPS counter
            self.fps.update()
            
            return results
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return {}
    
    def merge_detections(
        self, 
        detections_by_purpose: Dict[str, List[Tuple[str, float, Tuple[float, float, float, float]]]],
        merge_strategy: str = "highest_confidence"
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Merge detections from multiple models.
        
        This method combines detections from multiple models into a single list
        using the specified merge strategy.
        
        Args:
            detections_by_purpose: Dictionary mapping purpose to list of detections
            merge_strategy: Strategy for merging detections
                - "highest_confidence": Keep the detection with the highest confidence
                - "specialized_first": Prefer detections from specialized models over general ones
                - "all": Keep all detections
            
        Returns:
            List of merged detections
        """
        if not detections_by_purpose:
            return []
        
        # Flatten all detections
        all_detections = []
        for purpose, detections in detections_by_purpose.items():
            for detection in detections:
                all_detections.append((purpose, detection))
        
        if merge_strategy == "all":
            # Return all detections
            return [detection for _, detection in all_detections]
        
        # Group detections by label and bounding box overlap
        grouped_detections = {}
        for purpose, detection in all_detections:
            label, confidence, bbox = detection
            
            # Check if this detection overlaps with any existing group
            found_group = False
            for group_key, group in grouped_detections.items():
                group_label, _, group_bbox = group[0][1]
                
                # If labels match and bounding boxes overlap significantly
                if label == group_label and self._calculate_iou(bbox, group_bbox) > 0.5:
                    group.append((purpose, detection))
                    found_group = True
                    break
            
            # If no matching group found, create a new one
            if not found_group:
                grouped_detections[len(grouped_detections)] = [(purpose, detection)]
        
        # Apply merge strategy to each group
        merged_detections = []
        for group in grouped_detections.values():
            if merge_strategy == "highest_confidence":
                # Keep the detection with the highest confidence
                best_detection = max(group, key=lambda x: x[1][1])
                merged_detections.append(best_detection[1])
            elif merge_strategy == "specialized_first":
                # Prefer detections from specialized models over general ones
                specialized = [d for d in group if d[0] != "general"]
                if specialized:
                    # If there are specialized detections, use the one with highest confidence
                    best_detection = max(specialized, key=lambda x: x[1][1])
                    merged_detections.append(best_detection[1])
                else:
                    # Otherwise use the general detection with highest confidence
                    best_detection = max(group, key=lambda x: x[1][1])
                    merged_detections.append(best_detection[1])
        
        return merged_detections
    
    def _calculate_iou(self, bbox1: Tuple[float, float, float, float], bbox2: Tuple[float, float, float, float]) -> float:
        """
        Calculate the Intersection over Union (IoU) of two bounding boxes.
        
        Args:
            bbox1: First bounding box (x1, y1, x2, y2)
            bbox2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            IoU value
        """
        # Calculate intersection area
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        if x2 < x1 or y2 < y1:
            return 0.0
        
        intersection_area = (x2 - x1) * (y2 - y1)
        
        # Calculate union area
        bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union_area = bbox1_area + bbox2_area - intersection_area
        
        # Calculate IoU
        iou = intersection_area / union_area if union_area > 0 else 0.0
        
        return iou
    
    def cleanup(self) -> None:
        """Clean up resources used by the pipeline."""
        if self.detector is not None:
            self.detector.cleanup()
            self.detector = None
    
    def get_info(self) -> Dict[str, any]:
        """
        Get information about the detection pipeline.
        
        Returns:
            Dictionary containing pipeline information
        """
        info = {
            "fps": self.fps.value(),
            "detector_type": self.detector_config.type,
        }
        
        if self.detector is not None:
            info["models"] = self.detector.get_model_info()
        
        return info
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.cleanup()


class DetectionProcess:
    """
    Manages a detection process for running detections in a separate process.
    
    This class handles the creation and management of a separate process for
    running object detection, communication with the process, and cleanup.
    """
    
    def __init__(
        self,
        name: str,
        detection_queue: Queue,
        out_events: Dict[str, MpEvent],
        detector_config: BaseDetectorConfig,
        labels_path: str = None,
    ):
        """
        Initialize the detection process.
        
        Args:
            name: Name of the detection process
            detection_queue: Queue for receiving detection requests
            out_events: Events for signaling detection completion
            detector_config: Configuration for the detector
            labels_path: Path to the labels file
        """
        self.name = name
        self.detection_queue = detection_queue
        self.out_events = out_events
        self.detector_config = detector_config
        self.labels_path = labels_path
        
        # Performance metrics
        self.avg_inference_speed = Value("d", 0.01)
        self.detection_start = Value("d", 0.0)
        
        # Process management
        self.detect_process: Optional[Process] = None
        
        # Start the detection process
        self.start_or_restart()
    
    def start_or_restart(self) -> None:
        """Start or restart the detection process."""
        self.detection_start.value = 0.0
        
        if (self.detect_process is not None) and self.detect_process.is_alive():
            self.stop()
        
        self.detect_process = Process(
            target=run_detector_process,
            name=f"detector:{self.name}",
            args=(
                self.name,
                self.detection_queue,
                self.out_events,
                self.avg_inference_speed,
                self.detection_start,
                self.detector_config,
                self.labels_path,
            ),
        )
        self.detect_process.daemon = True
        self.detect_process.start()
        logger.info(f"Started detection process: {self.name} (PID: {self.detect_process.pid})")
    
    def stop(self) -> None:
        """Stop the detection process."""
        # If the process has already exited, just return
        if self.detect_process and self.detect_process.exitcode is not None:
            return
        
        # Terminate the process
        self.detect_process.terminate()
        logger.info(f"Waiting for detection process {self.name} to exit gracefully...")
        
        # Wait for the process to exit
        self.detect_process.join(timeout=30)
        
        # If the process didn't exit, force kill it
        if self.detect_process.exitcode is None:
            logger.info(f"Detection process {self.name} didn't exit. Force killing...")
            self.detect_process.kill()
            self.detect_process.join()
        
        logger.info(f"Detection process {self.name} has exited...")
    
    def is_alive(self) -> bool:
        """Check if the detection process is alive."""
        return self.detect_process is not None and self.detect_process.is_alive()
    
    def get_info(self) -> Dict[str, any]:
        """
        Get information about the detection process.
        
        Returns:
            Dictionary containing process information
        """
        return {
            "name": self.name,
            "alive": self.is_alive(),
            "avg_inference_speed": self.avg_inference_speed.value,
            "detector_type": self.detector_config.type,
        }


def run_detector_process(
    name: str,
    detection_queue: Queue,
    out_events: Dict[str, MpEvent],
    avg_speed: Value,
    start: Value,
    detector_config: BaseDetectorConfig,
    labels_path: str = None,
) -> None:
    """
    Run the detector in a separate process.
    
    Args:
        name: Name of the detection process
        detection_queue: Queue for receiving detection requests
        out_events: Events for signaling detection completion
        avg_speed: Shared value for tracking average inference speed
        start: Shared value for tracking detection start time
        detector_config: Configuration for the detector
        labels_path: Path to the labels file
    """
    # Set up process
    threading.current_thread().name = f"detector:{name}"
    logger = logging.getLogger(f"detector.{name}")
    logger.info(f"Starting detection process: {os.getpid()}")
    setproctitle(f"arkos.detector.{name}")
    
    # Set up signal handling
    stop_event = mp.Event()
    
    def receive_signal(signal_number, frame):
        logger.info(f"Received signal {signal_number}, shutting down...")
        stop_event.set()
    
    signal.signal(signal.SIGTERM, receive_signal)
    signal.signal(signal.SIGINT, receive_signal)
    
    # Initialize resources
    frame_manager = SharedMemoryFrameManager()
    
    try:
        # Create detection pipeline
        pipeline = DetectionPipeline(
            detector_config=detector_config,
            labels_path=labels_path,
        )
        
        # Set up output shared memory
        outputs = {}
        for connection_id in out_events.keys():
            out_shm = UntrackedSharedMemory(name=f"out-{connection_id}", create=False)
            out_np = np.ndarray((20, 6), dtype=np.float32, buffer=out_shm.buf)
            outputs[connection_id] = {"shm": out_shm, "np": out_np}
        
        # Main detection loop
        while not stop_event.is_set():
            try:
                # Get detection request from queue
                request = detection_queue.get(timeout=1)
                
                # Parse request
                if isinstance(request, tuple) and len(request) >= 2:
                    connection_id, purpose = request[0], request[1]
                else:
                    connection_id, purpose = request, "general"
            except queue.Empty:
                continue
            
            # Get model config for the purpose
            model_config = None
            for model in detector_config.models:
                if model.purpose == purpose:
                    model_config = model
                    break
            
            # If no model found for the purpose, use the first model
            if model_config is None and detector_config.models:
                model_config = detector_config.models[0]
                logger.warning(f"No model found for purpose '{purpose}', using default model")
            
            # If no model config, skip
            if model_config is None:
                logger.error(f"No model config found for detector")
                continue
            
            # Get frame from shared memory
            input_frame = frame_manager.get(
                connection_id,
                (1, model_config.height, model_config.width, 3),
            )
            
            if input_frame is None:
                logger.warning(f"Failed to get frame {connection_id} from shared memory")
                continue
            
            # Perform detection
            start.value = datetime.datetime.now().timestamp()
            
            try:
                # Get raw detections
                raw_detections = pipeline.detector.detect_raw(input_frame, model_config)
                
                # Copy results to output shared memory
                outputs[connection_id]["np"][:] = raw_detections[:]
                
                # Calculate duration
                duration = datetime.datetime.now().timestamp() - start.value
                
                # Update average speed
                avg_speed.value = (avg_speed.value * 9 + duration) / 10
                
                # Signal completion
                out_events[connection_id].set()
            except Exception as e:
                logger.error(f"Error during detection: {str(e)}")
            finally:
                # Clean up
                frame_manager.close(connection_id)
                start.value = 0.0
        
        # Clean up pipeline
        pipeline.cleanup()
        
    except Exception as e:
        logger.error(f"Error in detection process: {str(e)}")
    
    logger.info("Exited detection process...")


class RemoteDetectionClient:
    """
    Client for interacting with a remote detection process.
    
    This class provides a client interface for sending detection requests to
    a remote detection process and receiving results.
    """
    
    def __init__(
        self,
        name: str,
        labels: Dict[int, str],
        detection_queue: Queue,
        event: MpEvent,
        model_config: ModelConfig,
        stop_event: MpEvent,
    ):
        """
        Initialize the remote detection client.
        
        Args:
            name: Name of the client
            labels: Label mapping
            detection_queue: Queue for sending detection requests
            event: Event for waiting for detection completion
            model_config: Model configuration
            stop_event: Event for signaling stop
        """
        self.name = name
        self.labels = labels
        self.detection_queue = detection_queue
        self.event = event
        self.model_config = model_config
        self.stop_event = stop_event
        self.fps = EventsPerSecond()
        
        # Set up shared memory
        self.shm = UntrackedSharedMemory(name=self.name, create=False)
        self.np_shm = np.ndarray(
            (1, model_config.height, model_config.width, 3),
            dtype=np.uint8,
            buffer=self.shm.buf,
        )
        
        self.out_shm = UntrackedSharedMemory(name=f"out-{self.name}", create=False)
        self.out_np_shm = np.ndarray((20, 6), dtype=np.float32, buffer=self.out_shm.buf)
    
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
        detections = []
        
        # Check if stopped
        if self.stop_event.is_set():
            return detections
        
        try:
            # Copy input to shared memory
            self.np_shm[:] = tensor_input[:]
            
            # Clear event and send request
            self.event.clear()
            self.detection_queue.put((self.name, purpose))
            
            # Wait for result
            result = self.event.wait(timeout=5.0)
            
            # If timed out
            if result is None:
                logger.warning(f"Detection request timed out for {self.name}")
                return detections
            
            # Process results
            for d in self.out_np_shm:
                if d[1] < threshold:
                    break
                
                detections.append(
                    (self.labels[int(d[0])], float(d[1]), (d[2], d[3], d[4], d[5]))
                )
            
            # Update FPS counter
            self.fps.update()
            
        except Exception as e:
            logger.error(f"Error during remote detection: {str(e)}")
        
        return detections
    
    def cleanup(self) -> None:
        """Clean up resources used by the client."""
        try:
            self.shm.unlink()
            self.out_shm.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up remote detection client: {str(e)}")
