import logging
import time
from typing import List, Tuple, Optional

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

from frigate.camera import PTZMetrics
from frigate.comms.config_updater import ConfigSubscriber
from frigate.config.camera.motion import MotionConfig
from frigate.motion import MotionDetector
from frigate.util.image import grab_cv2_contours

logger = logging.getLogger(__name__)


class OptimizedMotionDetector(MotionDetector):
    """
    An optimized motion detector that improves upon the ImprovedMotionDetector.
    
    Optimizations include:
    - More efficient frame processing
    - Adaptive thresholding
    - Improved contrast enhancement
    - Better handling of lighting changes
    - Reduced false positives
    - Optimized calibration
    """

    def __init__(
        self,
        frame_shape: Tuple[int, int, int],
        config: MotionConfig,
        fps: int,
        ptz_metrics: Optional[PTZMetrics] = None,
        name: str = "optimized",
        blur_radius: int = 1,
        interpolation: int = cv2.INTER_AREA,
        contrast_frame_history: int = 50,
    ):
        """
        Initialize the optimized motion detector.
        
        Args:
            frame_shape: The shape of the input frame (height, width, channels)
            config: The motion configuration
            fps: Frames per second of the video stream
            ptz_metrics: PTZ camera metrics (optional)
            name: Name of the detector
            blur_radius: Radius for Gaussian blur
            interpolation: Interpolation method for resizing
            contrast_frame_history: Number of frames to keep for contrast history
        """
        self.name = name
        self.config = config
        self.frame_shape = frame_shape
        self.resize_factor = frame_shape[0] / config.frame_height
        self.motion_frame_size = (
            config.frame_height,
            config.frame_height * frame_shape[1] // frame_shape[0],
        )
        
        # Initialize frame buffers
        self.avg_frame = np.zeros(self.motion_frame_size, np.float32)
        self.prev_frame = None
        self.motion_frame_count = 0
        self.frame_counter = 0
        self.last_motion_detected_time = 0
        
        # Prepare mask
        resized_mask = cv2.resize(
            config.mask,
            dsize=(self.motion_frame_size[1], self.motion_frame_size[0]),
            interpolation=cv2.INTER_AREA,
        )
        self.mask = np.where(resized_mask == [0])
        
        # Configuration
        self.save_images = False
        self.calibrating = True
        self.blur_radius = blur_radius
        self.interpolation = interpolation
        
        # Contrast enhancement
        self.contrast_values = np.zeros((contrast_frame_history, 2), np.uint8)
        self.contrast_values[:, 1:2] = 255
        self.contrast_values_index = 0
        
        # Dynamic thresholding
        self.dynamic_threshold = config.threshold
        self.min_threshold = max(config.threshold - 10, 10)
        self.max_threshold = min(config.threshold + 10, 50)
        self.threshold_adjustment_rate = 0.1
        
        # Noise reduction
        self.noise_level = 0
        self.noise_samples = []
        self.max_noise_samples = 30
        
        # PTZ handling
        self.config_subscriber = ConfigSubscriber(f"config/motion/{name}", True)
        self.ptz_metrics = ptz_metrics
        self.last_stop_time = None
        
        # Performance metrics
        self.processing_times = []
        self.max_processing_times = 100
        self.last_fps_check = time.time()
        self.processed_frames = 0
        self.effective_fps = 0

    def is_calibrating(self) -> bool:
        """
        Check if the detector is still calibrating.
        
        Returns:
            True if calibrating, False otherwise
        """
        return self.calibrating

    def _update_noise_level(self, frame: np.ndarray) -> None:
        """
        Update the estimated noise level in the frame.
        
        Args:
            frame: The current frame
        """
        if len(self.noise_samples) >= self.max_noise_samples:
            self.noise_samples.pop(0)
            
        # Calculate noise using the difference between adjacent pixels
        noise = np.mean(np.abs(frame[1:, :] - frame[:-1, :]))
        self.noise_samples.append(noise)
        self.noise_level = np.mean(self.noise_samples)

    def _enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance the contrast of the frame using adaptive parameters.
        
        Args:
            frame: The input frame
            
        Returns:
            The contrast-enhanced frame
        """
        if not self.config.improve_contrast:
            return frame
            
        # Calculate percentiles more efficiently
        flat_frame = frame.flatten()
        samples = flat_frame[np.random.choice(flat_frame.size, min(1000, flat_frame.size), replace=False)]
        samples.sort()
        
        min_value = samples[int(len(samples) * 0.04)]
        max_value = samples[int(len(samples) * 0.96)]
        
        # Skip contrast enhancement if the image has very little contrast
        if max_value - min_value < 10:
            return frame
            
        # Update contrast history
        self.contrast_values[self.contrast_values_index] = [min_value, max_value]
        self.contrast_values_index = (self.contrast_values_index + 1) % len(self.contrast_values)
        
        # Use a weighted average that gives more weight to recent values
        weights = np.linspace(0.5, 1.0, len(self.contrast_values))
        weights = weights / np.sum(weights)
        
        avg_min = np.sum(self.contrast_values[:, 0] * weights).astype(np.uint8)
        avg_max = np.sum(self.contrast_values[:, 1] * weights).astype(np.uint8)
        
        # Apply contrast enhancement
        enhanced = np.clip(frame, avg_min, avg_max)
        enhanced = (((enhanced - avg_min) / (avg_max - avg_min)) * 255).astype(np.uint8)
        
        return enhanced

    def _apply_dynamic_threshold(self, frame_delta: np.ndarray) -> np.ndarray:
        """
        Apply dynamic thresholding based on noise level and recent motion.
        
        Args:
            frame_delta: The frame delta
            
        Returns:
            The thresholded image
        """
        # Adjust threshold based on noise level
        if self.noise_level > 0:
            noise_adjustment = min(max(self.noise_level - 2, 0), 10)
            adjusted_threshold = self.dynamic_threshold + noise_adjustment
        else:
            adjusted_threshold = self.dynamic_threshold
            
        # Apply threshold
        thresh = cv2.threshold(
            frame_delta, adjusted_threshold, 255, cv2.THRESH_BINARY
        )[1]
        
        return thresh

    def _update_dynamic_threshold(self, motion_detected: bool, contour_count: int) -> None:
        """
        Update the dynamic threshold based on detection results.
        
        Args:
            motion_detected: Whether motion was detected
            contour_count: Number of motion contours detected
        """
        # If too many contours, increase threshold to reduce sensitivity
        if motion_detected and contour_count > 10:
            self.dynamic_threshold = min(
                self.dynamic_threshold + self.threshold_adjustment_rate, 
                self.max_threshold
            )
        # If no motion for a while, gradually decrease threshold to increase sensitivity
        elif not motion_detected and time.time() - self.last_motion_detected_time > 10:
            self.dynamic_threshold = max(
                self.dynamic_threshold - self.threshold_adjustment_rate * 0.1,
                self.min_threshold
            )

    def _handle_ptz_movement(self, frame: np.ndarray) -> bool:
        """
        Handle PTZ camera movement.
        
        Args:
            frame: The current frame
            
        Returns:
            True if PTZ movement was handled, False otherwise
        """
        if not self.ptz_metrics or not self.ptz_metrics.autotracker_enabled.value:
            return False
            
        # If motor is moving, return a large motion box
        if not self.ptz_metrics.motor_stopped.is_set():
            return True
            
        # Check if the motor has just stopped
        if (self.last_stop_time is None or 
            self.ptz_metrics.stop_time.value != self.last_stop_time) and \
            self.ptz_metrics.stop_time.value != 0:
            
            self.last_stop_time = self.ptz_metrics.stop_time.value
            self.avg_frame = frame.astype(np.float32)
            self.calibrating = True
            return True
            
        return False

    def _update_average_frame(self, frame: np.ndarray, motion_detected: bool) -> None:
        """
        Update the average frame based on motion detection.
        
        Args:
            frame: The current frame
            motion_detected: Whether motion was detected
        """
        if motion_detected:
            self.motion_frame_count += 1
            if self.motion_frame_count >= 10:
                # Only average in the current frame if the difference persists for a bit
                cv2.accumulateWeighted(
                    frame,
                    self.avg_frame,
                    0.2 if self.calibrating else self.config.frame_alpha,
                )
        else:
            # When no motion, just keep averaging the frames together
            cv2.accumulateWeighted(
                frame,
                self.avg_frame,
                0.2 if self.calibrating else self.config.frame_alpha,
            )
            self.motion_frame_count = 0

    def _update_calibration_status(self, pct_motion: float, motion_box_count: int) -> None:
        """
        Update the calibration status based on motion detection.
        
        Args:
            pct_motion: Percentage of the frame with motion
            motion_box_count: Number of motion boxes detected
        """
        # Once the motion is less than 5% and the number of contours is < 4, assume it's calibrated
        if pct_motion < 0.05 and motion_box_count <= 4:
            self.calibrating = False

        # If calibrating or the motion contours are > threshold of the image area (lightning, IR, PTZ) recalibrate
        if self.calibrating or pct_motion > self.config.lightning_threshold:
            self.calibrating = True

    def _update_performance_metrics(self, start_time: float) -> None:
        """
        Update performance metrics.
        
        Args:
            start_time: Start time of frame processing
        """
        processing_time = time.time() - start_time
        
        if len(self.processing_times) >= self.max_processing_times:
            self.processing_times.pop(0)
        self.processing_times.append(processing_time)
        
        self.processed_frames += 1
        current_time = time.time()
        
        # Update FPS calculation every second
        if current_time - self.last_fps_check >= 1.0:
            self.effective_fps = self.processed_frames / (current_time - self.last_fps_check)
            self.processed_frames = 0
            self.last_fps_check = current_time
            
            # Log performance metrics occasionally
            if self.frame_counter % 100 == 0:
                avg_processing_time = np.mean(self.processing_times) * 1000
                logger.debug(
                    f"Motion detection performance: {avg_processing_time:.2f}ms per frame, "
                    f"effective FPS: {self.effective_fps:.2f}, "
                    f"dynamic threshold: {self.dynamic_threshold:.2f}"
                )

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect motion in the frame.
        
        Args:
            frame: The input frame
            
        Returns:
            List of motion boxes (x1, y1, x2, y2)
        """
        start_time = time.time()
        motion_boxes = []

        # Check for updated motion config
        _, updated_motion_config = self.config_subscriber.check_for_update()
        if updated_motion_config:
            self.config = updated_motion_config

        if not self.config.enabled:
            return motion_boxes

        # Handle PTZ camera movement
        if self._handle_ptz_movement(frame):
            return [
                (
                    int(self.frame_shape[1] * 0.1),
                    int(self.frame_shape[0] * 0.1),
                    int(self.frame_shape[1] * 0.9),
                    int(self.frame_shape[0] * 0.9),
                )
            ]

        # Extract grayscale frame
        gray = frame[0 : self.frame_shape[0], 0 : self.frame_shape[1]]

        # Resize frame more efficiently using INTER_AREA for downsampling
        resized_frame = cv2.resize(
            gray,
            dsize=(self.motion_frame_size[1], self.motion_frame_size[0]),
            interpolation=self.interpolation,
        )

        # Save original for debugging if needed
        if self.save_images:
            resized_saved = resized_frame.copy()

        # Enhance contrast
        resized_frame = self._enhance_contrast(resized_frame)

        # Save contrasted for debugging if needed
        if self.save_images:
            contrasted_saved = resized_frame.copy()

        # Apply mask - setting masked pixels to zero to match the average frame at startup
        resized_frame[self.mask] = [0]

        # Update noise level estimate
        self._update_noise_level(resized_frame)

        # Apply Gaussian blur - using smaller kernel for better performance
        # Only apply blur if noise level is above a threshold
        if self.noise_level > 1.5:
            resized_frame = gaussian_filter(
                resized_frame, 
                sigma=1, 
                radius=self.blur_radius
            )
        
        # Save blurred for debugging if needed
        if self.save_images:
            blurred_saved = resized_frame.copy()

        # Increment frame counter for debugging and calibration
        if self.save_images or self.calibrating:
            self.frame_counter += 1

        # Compare to average frame
        frame_delta = cv2.absdiff(resized_frame, cv2.convertScaleAbs(self.avg_frame))

        # Apply dynamic thresholding
        thresh = self._apply_dynamic_threshold(frame_delta)

        # Dilate the thresholded image to fill in holes
        # Use a more efficient kernel for dilation
        kernel = np.ones((3, 3), np.uint8)
        thresh_dilated = cv2.dilate(thresh, kernel, iterations=1)

        # Find contours more efficiently
        contours = cv2.findContours(
            thresh_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = grab_cv2_contours(contours)

        # Process contours
        total_contour_area = 0
        for c in contours:
            # Calculate contour area
            contour_area = cv2.contourArea(c)
            total_contour_area += contour_area
            
            # If the contour is big enough, count it as motion
            if contour_area > self.config.contour_area:
                x, y, w, h = cv2.boundingRect(c)
                motion_boxes.append(
                    (
                        int(x * self.resize_factor),
                        int(y * self.resize_factor),
                        int((x + w) * self.resize_factor),
                        int((y + h) * self.resize_factor),
                    )
                )

        # Calculate percentage of frame with motion
        pct_motion = total_contour_area / (
            self.motion_frame_size[0] * self.motion_frame_size[1]
        )

        # Update calibration status
        self._update_calibration_status(pct_motion, len(motion_boxes))

        # Save debug images if enabled
        if self.save_images:
            thresh_dilated_color = cv2.cvtColor(thresh_dilated, cv2.COLOR_GRAY2BGR)
            for b in motion_boxes:
                cv2.rectangle(
                    thresh_dilated_color,
                    (int(b[0] / self.resize_factor), int(b[1] / self.resize_factor)),
                    (int(b[2] / self.resize_factor), int(b[3] / self.resize_factor)),
                    (0, 0, 255),
                    2,
                )
            
            # Create debug image with all processing steps
            frames = [
                cv2.cvtColor(resized_saved, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(contrasted_saved, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(blurred_saved, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
                thresh_dilated_color,
            ]
            
            # Add text with metrics
            for i, frame_name in enumerate(["Original", "Contrast", "Blur", "Delta", "Threshold", "Dilated"]):
                cv2.putText(
                    frames[i],
                    frame_name,
                    (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
            
            # Add threshold value to threshold frame
            cv2.putText(
                frames[4],
                f"T: {self.dynamic_threshold:.1f}",
                (5, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )
            
            # Save combined debug image
            cv2.imwrite(
                f"debug/frames/{self.name}-{self.frame_counter}.jpg",
                (
                    cv2.hconcat(frames)
                    if self.frame_shape[0] > self.frame_shape[1]
                    else cv2.vconcat(frames)
                ),
            )

        # Update motion detection time
        if len(motion_boxes) > 0:
            self.last_motion_detected_time = time.time()

        # Update dynamic threshold
        self._update_dynamic_threshold(len(motion_boxes) > 0, len(contours))

        # Update average frame
        self._update_average_frame(resized_frame, len(motion_boxes) > 0)

        # Update performance metrics
        self._update_performance_metrics(start_time)

        return motion_boxes

    def stop(self) -> None:
        """Stop the motion detector."""
        self.config_subscriber.stop()
