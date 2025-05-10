"""
Detection Pipeline for Arkos AI object detection.

This module provides the orchestration layer for the object detection process,
handling preprocessing, detection, and postprocessing.
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
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from setproctitle import setproctitle

from frigate.detectors.detector_config import BaseDetectorConfig
from frigate.object_detection.detector_interface import DetectorInterface
from frigate.object_detection.detector_registry import DetectorRegistry
from frigate.util import Process
from frigate.util.builtin import EventsPerSecond
from frigate.util.image import SharedMemoryFrameManager, UntrackedSharedMemory
from frigate.util.services import listen

logger = logging.getLogger(__name__)


class DetectionPipeline:
    """
    Orchestrates the object detection process.
    
    This class manages the lifecycle of detectors, handles preprocessing and
    postprocessing, and coordinates the detection process.
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
        except Exception as e:
            logger.error(f"Failed to initialize detector: {str(e)}")
            raise
    
    def detect(
        self, 
        tensor_input: np.ndarray, 
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection on the input tensor.
        
        This method handles preprocessing, detection, and postprocessing.
        
        Args:
            tensor_input: Input tensor
            threshold: Confidence threshold for filtering detections
            
        Returns:
            List of tuples (label, confidence, (x1, y1, x2, y2))
        """
        if self.detector is None:
            logger.error("Detector not initialized")
            return []
        
        try:
            # Preprocess input
            processed_input = self._preprocess_input(tensor_input)
            
            # Perform detection
            detections = self.detector.detect(processed_input, threshold)
            
            # Postprocess results
            processed_detections = self._postprocess_detections(detections)
            
            # Update FPS counter
            self.fps.update()
            
            return processed_detections
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return []
    
    def _preprocess_input(self, tensor_input: np.ndarray) -> np.ndarray:
        """
        Preprocess the input tensor.
        
        Args:
            tensor_input: Raw input tensor
            
        Returns:
            Preprocessed tensor
        """
        # Apply detector-specific preprocessing
        return self.detector.preprocess_input(tensor_input)
    
    def _postprocess_detections(
        self, 
        detections: List[Tuple[str, float, Tuple[float, float, float, float]]]
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Postprocess detection results.
        
        Args:
            detections: Raw detection results
            
        Returns:
            Processed detection results
        """
        # Default implementation just returns the detections
        # Subclasses can override to add additional processing
        return detections
    
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
            info["detector"] = self.detector.get_model_info()
        
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
    listen()
    
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
                connection_id = detection_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            # Get frame from shared memory
            input_frame = frame_manager.get(
                connection_id,
                (1, detector_config.model.height, detector_config.model.width, 3),
            )
            
            if input_frame is None:
                logger.warning(f"Failed to get frame {connection_id} from shared memory")
                continue
            
            # Perform detection
            start.value = datetime.datetime.now().timestamp()
            
            try:
                # Get raw detections
                raw_detections = pipeline.detector.detect_raw(input_frame)
                
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
        model_config,
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
        threshold: float = 0.4
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        """
        Perform detection on the input tensor.
        
        Args:
            tensor_input: Input tensor
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
            self.detection_queue.put(self.name)
            
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
