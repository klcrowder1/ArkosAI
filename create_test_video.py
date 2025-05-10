import cv2
import numpy as np
import os

# Create directory if it doesn't exist
os.makedirs("debug/motion_test_clips", exist_ok=True)

# Video parameters
width, height = 640, 480
fps = 30
duration = 5  # seconds
output_path = "debug/motion_test_clips/test_motion.mp4"

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Generate frames
total_frames = fps * duration
for i in range(total_frames):
    # Create a black frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add a moving object (white rectangle)
    x_pos = int((i / total_frames) * (width - 100))
    cv2.rectangle(frame, (x_pos, 200), (x_pos + 100, 300), (255, 255, 255), -1)
    
    # Add some noise
    noise = np.random.randint(0, 10, (height, width, 3), dtype=np.uint8)
    frame = cv2.add(frame, noise)
    
    # Write the frame
    out.write(frame)
    
    # Print progress
    if i % 30 == 0:
        print(f"Generated {i}/{total_frames} frames")

# Release the VideoWriter
out.release()

print(f"Test video created at {output_path}")
