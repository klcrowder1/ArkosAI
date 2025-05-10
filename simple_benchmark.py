import cv2
import numpy as np
import os
import time
from typing import List, Tuple, Optional

# Create debug directory if it doesn't exist
os.makedirs("debug/frames", exist_ok=True)

# Simple motion detector base class
class SimpleMotionDetector:
    def __init__(self, frame_shape, name="base"):
        self.frame_shape = frame_shape
        self.name = name
        self.save_images = False
        
    def detect(self, frame):
        # Base implementation does nothing
        return []
        
    def stop(self):
        pass

# Original motion detector implementation
class OriginalMotionDetector(SimpleMotionDetector):
    def __init__(self, frame_shape, name="original"):
        super().__init__(frame_shape, name)
        self.height, self.width = frame_shape[0], frame_shape[1]
        self.resize_factor = 1.0
        self.motion_frame_size = (
            int(self.height / 3),
            int(self.width / 3),
        )
        self.avg_frame = np.zeros(self.motion_frame_size, np.float32)
        self.frame_counter = 0
        
    def detect(self, frame):
        motion_boxes = []
        
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
            
        # Resize frame
        resized_frame = cv2.resize(
            gray,
            dsize=(self.motion_frame_size[1], self.motion_frame_size[0]),
            interpolation=cv2.INTER_LINEAR,
        )
        
        # Save original for debugging
        if self.save_images:
            resized_saved = resized_frame.copy()
        
        # It takes ~30 frames to establish a baseline
        if self.frame_counter < 30:
            self.frame_counter += 1
            # Update average frame
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.1)
            return motion_boxes
            
        # Compare to average
        frame_delta = cv2.absdiff(resized_frame, cv2.convertScaleAbs(self.avg_frame))
        
        # Threshold
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate
        thresh_dilated = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Process contours
        for c in contours:
            # If the contour is big enough, count it as motion
            if cv2.contourArea(c) > 50:
                x, y, w, h = cv2.boundingRect(c)
                motion_boxes.append(
                    (
                        int(x * self.resize_factor),
                        int(y * self.resize_factor),
                        int((x + w) * self.resize_factor),
                        int((y + h) * self.resize_factor),
                    )
                )
        
        # Save debug images
        if self.save_images:
            debug_image = cv2.cvtColor(thresh_dilated, cv2.COLOR_GRAY2BGR)
            for box in motion_boxes:
                cv2.rectangle(
                    debug_image,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    (0, 0, 255),
                    2,
                )
            cv2.imwrite(f"debug/frames/{self.name}-{self.frame_counter}.jpg", debug_image)
            self.frame_counter += 1
        
        # Update average frame
        if len(motion_boxes) > 0:
            # When motion detected, update average frame more slowly
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.01)
        else:
            # When no motion, update average frame more quickly
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.1)
        
        return motion_boxes

# Optimized motion detector implementation
class OptimizedMotionDetector(SimpleMotionDetector):
    def __init__(self, frame_shape, name="optimized"):
        super().__init__(frame_shape, name)
        self.height, self.width = frame_shape[0], frame_shape[1]
        self.resize_factor = 1.0
        self.motion_frame_size = (
            int(self.height / 3),
            int(self.width / 3),
        )
        self.avg_frame = np.zeros(self.motion_frame_size, np.float32)
        self.frame_counter = 0
        self.last_motion_detected_time = 0
        
        # Adaptive parameters
        self.dynamic_threshold = 25
        self.min_threshold = 15
        self.max_threshold = 40
        self.threshold_adjustment_rate = 0.5
        
        # Noise estimation
        self.noise_level = 0
        self.noise_samples = []
        self.max_noise_samples = 30
        
        # Performance metrics
        self.processing_times = []
        self.max_processing_times = 100
        
    def _update_noise_level(self, frame):
        """Update the estimated noise level in the frame."""
        if len(self.noise_samples) >= self.max_noise_samples:
            self.noise_samples.pop(0)
            
        # Calculate noise using the difference between adjacent pixels
        noise = np.mean(np.abs(frame[1:, :] - frame[:-1, :]))
        self.noise_samples.append(noise)
        self.noise_level = np.mean(self.noise_samples)
    
    def _enhance_contrast(self, frame):
        """Enhance the contrast of the frame using adaptive parameters."""
        # Calculate percentiles more efficiently
        flat_frame = frame.flatten()
        samples = flat_frame[np.random.choice(flat_frame.size, min(1000, flat_frame.size), replace=False)]
        samples.sort()
        
        min_value = samples[int(len(samples) * 0.04)]
        max_value = samples[int(len(samples) * 0.96)]
        
        # Skip contrast enhancement if the image has very little contrast
        if max_value - min_value < 10:
            return frame
            
        # Apply contrast enhancement
        enhanced = np.clip(frame, min_value, max_value)
        enhanced = (((enhanced - min_value) / (max_value - min_value)) * 255).astype(np.uint8)
        
        return enhanced
    
    def _apply_dynamic_threshold(self, frame_delta):
        """Apply dynamic thresholding based on noise level."""
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
    
    def _update_dynamic_threshold(self, motion_detected, contour_count):
        """Update the dynamic threshold based on detection results."""
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
    
    def detect(self, frame):
        start_time = time.time()
        motion_boxes = []
        
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
            
        # Resize frame
        resized_frame = cv2.resize(
            gray,
            dsize=(self.motion_frame_size[1], self.motion_frame_size[0]),
            interpolation=cv2.INTER_AREA,  # Better quality downsampling
        )
        
        # Save original for debugging
        if self.save_images:
            resized_saved = resized_frame.copy()
        
        # Enhance contrast
        resized_frame = self._enhance_contrast(resized_frame)
        
        # Save contrasted for debugging
        if self.save_images:
            contrasted_saved = resized_frame.copy()
        
        # Update noise level estimate
        self._update_noise_level(resized_frame)
        
        # Apply Gaussian blur only if noise level is high
        if self.noise_level > 1.5:
            resized_frame = cv2.GaussianBlur(resized_frame, (3, 3), 0)
        
        # Save blurred for debugging
        if self.save_images:
            blurred_saved = resized_frame.copy()
        
        # It takes ~30 frames to establish a baseline
        if self.frame_counter < 30:
            self.frame_counter += 1
            # Update average frame
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.1)
            return motion_boxes
            
        # Compare to average
        frame_delta = cv2.absdiff(resized_frame, cv2.convertScaleAbs(self.avg_frame))
        
        # Apply dynamic thresholding
        thresh = self._apply_dynamic_threshold(frame_delta)
        
        # Dilate
        kernel = np.ones((3, 3), np.uint8)
        thresh_dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Process contours
        for c in contours:
            # If the contour is big enough, count it as motion
            contour_area = cv2.contourArea(c)
            if contour_area > 50:
                x, y, w, h = cv2.boundingRect(c)
                motion_boxes.append(
                    (
                        int(x * self.resize_factor),
                        int(y * self.resize_factor),
                        int((x + w) * self.resize_factor),
                        int((y + h) * self.resize_factor),
                    )
                )
        
        # Save debug images
        if self.save_images:
            # Create debug image with all processing steps
            thresh_dilated_color = cv2.cvtColor(thresh_dilated, cv2.COLOR_GRAY2BGR)
            for box in motion_boxes:
                cv2.rectangle(
                    thresh_dilated_color,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    (0, 0, 255),
                    2,
                )
            
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
            combined = cv2.hconcat(frames) if self.motion_frame_size[0] > self.motion_frame_size[1] else cv2.vconcat(frames)
            cv2.imwrite(f"debug/frames/{self.name}-{self.frame_counter}.jpg", combined)
            self.frame_counter += 1
        
        # Update motion detection time
        if len(motion_boxes) > 0:
            self.last_motion_detected_time = time.time()
        
        # Update dynamic threshold
        self._update_dynamic_threshold(len(motion_boxes) > 0, len(contours))
        
        # Update average frame
        if len(motion_boxes) > 0:
            # When motion detected, update average frame more slowly
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.01)
        else:
            # When no motion, update average frame more quickly
            cv2.accumulateWeighted(resized_frame, self.avg_frame, 0.1)
        
        # Update performance metrics
        processing_time = time.time() - start_time
        if len(self.processing_times) >= self.max_processing_times:
            self.processing_times.pop(0)
        self.processing_times.append(processing_time)
        
        return motion_boxes

# Main benchmark function
def run_benchmark():
    # Load test video
    cap = cv2.VideoCapture("debug/motion_test_clips/challenging_motion.mp4")
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Get video info
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_shape = (height, width)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
    
    # Create motion detectors
    original_detector = OriginalMotionDetector(frame_shape, "original")
    optimized_detector = OptimizedMotionDetector(frame_shape, "optimized")
    
    # Enable debug images
    original_detector.save_images = True
    optimized_detector.save_images = True
    
    # Performance tracking
    performance_metrics = {
        "original": {"times": [], "motion_boxes": []},
        "optimized": {"times": [], "motion_boxes": []},
    }
    
    # Process frames
    frame_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Test original detector
        start_time = time.time()
        boxes1 = original_detector.detect(frame)
        elapsed1 = time.time() - start_time
        performance_metrics["original"]["times"].append(elapsed1)
        performance_metrics["original"]["motion_boxes"].append(len(boxes1))
        
        # Test optimized detector
        start_time = time.time()
        boxes2 = optimized_detector.detect(frame)
        elapsed2 = time.time() - start_time
        performance_metrics["optimized"]["times"].append(elapsed2)
        performance_metrics["optimized"]["motion_boxes"].append(len(boxes2))
        
        # Print progress
        frame_counter += 1
        if frame_counter % 10 == 0:
            progress = (frame_counter / total_frames) * 100
            print(f"Progress: {progress:.1f}% ({frame_counter}/{total_frames})")
    
    # Calculate additional metrics
    for detector, metrics in performance_metrics.items():
        # Calculate motion consistency (how stable the detection is)
        motion_boxes = np.array(metrics["motion_boxes"])
        changes = np.sum(np.abs(np.diff(motion_boxes > 0)))
        consistency = 100 - (changes / len(motion_boxes) * 100)
        metrics["consistency"] = consistency
        
        # Calculate average number of motion boxes when motion is detected
        motion_frames = motion_boxes > 0
        if np.sum(motion_frames) > 0:
            avg_boxes = np.mean(motion_boxes[motion_frames])
        else:
            avg_boxes = 0
        metrics["avg_boxes"] = avg_boxes
    
    # Print results
    print("\nPerformance Results:")
    print("-" * 100)
    print(f"{'Detector':<15} {'Avg Time (ms)':<15} {'Max Time (ms)':<15} {'Motion Detected %':<20} {'Consistency %':<15} {'Avg Boxes':<10}")
    print("-" * 100)
    
    for detector, metrics in performance_metrics.items():
        avg_time = np.mean(metrics["times"]) * 1000  # Convert to ms
        max_time = np.max(metrics["times"]) * 1000   # Convert to ms
        motion_percent = (np.sum(np.array(metrics["motion_boxes"]) > 0) / len(metrics["motion_boxes"])) * 100
        
        print(f"{detector:<15} {avg_time:<15.2f} {max_time:<15.2f} {motion_percent:<20.2f} {metrics['consistency']:<15.2f} {metrics['avg_boxes']:<10.2f}")
    
    print("-" * 80)
    print(f"Total frames processed: {frame_counter}")
    
    # Release resources
    cap.release()

if __name__ == "__main__":
    run_benchmark()
