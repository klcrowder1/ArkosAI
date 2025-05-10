import datetime
import multiprocessing as mp
import os
import time

import cv2
import numpy as np

from frigate.config.camera.motion import MotionConfig
from frigate.motion.improved_motion import ImprovedMotionDetector
from frigate.motion.optimized_motion import OptimizedMotionDetector
from frigate.util.image import create_mask

# Create debug directory if it doesn't exist
os.makedirs("debug/frames", exist_ok=True)

# get info on the video
cap = cv2.VideoCapture("debug/motion_test_clips/test_motion.mp4")
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_shape = (height, width, 3)
# Nick back:
# "1280,0,1280,316,1170,216,1146,126,1016,127,979,82,839,0",
# "310,350,300,402,224,405,241,354",
# "378,0,375,26,0,23,0,0",
# Front door:
# "1080,0,1080,339,1010,280,1020,169,777,163,452,170,318,299,191,365,186,417,139,470,108,516,40,530,0,514,0,0",
# "336,833,438,1024,346,1093,103,1052,24,814",
# Back
# "1855,0,1851,100,1289,96,1105,161,1045,119,890,121,890,0",
# "505,95,506,138,388,153,384,114",
# "689,72,689,122,549,134,547,89",
# "261,134,264,176,169,195,167,158",
# "145,159,146,202,70,220,65,183",

# Create a simple mask for the test video (mask out the top and bottom 10% of the frame)
mask = np.ones((height, width), np.uint8) * 255
mask[0:int(height*0.1), :] = 0  # Mask top 10%
mask[int(height*0.9):height, :] = 0  # Mask bottom 10%

# create the motion configs
motion_config_1 = MotionConfig()
motion_config_1.mask = np.zeros((height, width), np.uint8)
motion_config_1.mask[:] = mask
motion_config_1.frame_height = 150

motion_config_2 = MotionConfig()
motion_config_2.mask = np.zeros((height, width), np.uint8)
motion_config_2.mask[:] = mask
motion_config_2.frame_height = 150
motion_config_2.threshold = 20

motion_config_3 = MotionConfig()
motion_config_3.mask = np.zeros((height, width), np.uint8)
motion_config_3.mask[:] = mask
motion_config_3.frame_height = 150

save_images = True

# Create motion detectors
improved_motion_detector_1 = ImprovedMotionDetector(
    frame_shape=frame_shape,
    config=motion_config_1,
    fps=fps,
    name="improved1",
)
improved_motion_detector_1.save_images = save_images

improved_motion_detector_2 = ImprovedMotionDetector(
    frame_shape=frame_shape,
    config=motion_config_2,
    fps=fps,
    name="improved2",
)
improved_motion_detector_2.save_images = save_images

optimized_motion_detector = OptimizedMotionDetector(
    frame_shape=frame_shape,
    config=motion_config_3,
    fps=fps,
    name="optimized",
)
optimized_motion_detector.save_images = save_images

# Performance tracking
performance_metrics = {
    "improved1": {"times": [], "motion_boxes": []},
    "improved2": {"times": [], "motion_boxes": []},
    "optimized": {"times": [], "motion_boxes": []},
}

print(f"Starting benchmark with video: {width}x{height} @ {fps}fps")
print("Processing frames...")

# read and process frames
ret, frame = cap.read()
frame_counter = 1
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

while ret:
    yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)

    # Test improved motion detector 1
    start_time = time.time()
    boxes1 = improved_motion_detector_1.detect(yuv_frame)
    elapsed1 = time.time() - start_time
    performance_metrics["improved1"]["times"].append(elapsed1)
    performance_metrics["improved1"]["motion_boxes"].append(len(boxes1))

    # Test improved motion detector 2
    start_time = time.time()
    boxes2 = improved_motion_detector_2.detect(yuv_frame)
    elapsed2 = time.time() - start_time
    performance_metrics["improved2"]["times"].append(elapsed2)
    performance_metrics["improved2"]["motion_boxes"].append(len(boxes2))

    # Test optimized motion detector
    start_time = time.time()
    boxes3 = optimized_motion_detector.detect(yuv_frame)
    elapsed3 = time.time() - start_time
    performance_metrics["optimized"]["times"].append(elapsed3)
    performance_metrics["optimized"]["motion_boxes"].append(len(boxes3))

    # Combine debug images if they exist
    improved1_frame = f"debug/frames/improved1-{frame_counter}.jpg"
    improved2_frame = f"debug/frames/improved2-{frame_counter}.jpg"
    optimized_frame = f"debug/frames/optimized-{frame_counter}.jpg"
    
    if os.path.exists(improved1_frame) and os.path.exists(improved2_frame) and os.path.exists(optimized_frame):
        images = [
            cv2.imread(improved1_frame),
            cv2.imread(improved2_frame),
            cv2.imread(optimized_frame),
        ]

        cv2.imwrite(
            f"debug/frames/comparison-{frame_counter}.jpg",
            cv2.vconcat(images)
            if frame_shape[0] > frame_shape[1]
            else cv2.hconcat(images),
        )
        
        # Clean up individual frames to save space
        os.unlink(improved1_frame)
        os.unlink(improved2_frame)
        os.unlink(optimized_frame)
    
    # Print progress
    if frame_counter % 10 == 0:
        progress = (frame_counter / total_frames) * 100
        print(f"Progress: {progress:.1f}% ({frame_counter}/{total_frames})")
    
    frame_counter += 1
    ret, frame = cap.read()

# Calculate and print performance metrics
print("\nPerformance Results:")
print("-" * 80)
print(f"{'Detector':<15} {'Avg Time (ms)':<15} {'Max Time (ms)':<15} {'Motion Detected %':<20}")
print("-" * 80)

for detector, metrics in performance_metrics.items():
    avg_time = np.mean(metrics["times"]) * 1000  # Convert to ms
    max_time = np.max(metrics["times"]) * 1000   # Convert to ms
    motion_percent = (np.sum(np.array(metrics["motion_boxes"]) > 0) / len(metrics["motion_boxes"])) * 100
    
    print(f"{detector:<15} {avg_time:<15.2f} {max_time:<15.2f} {motion_percent:<20.2f}")

print("-" * 80)
print(f"Total frames processed: {frame_counter-1}")

cap.release()
