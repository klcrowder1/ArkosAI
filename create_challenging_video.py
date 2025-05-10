import cv2
import numpy as np
import os

# Create directory if it doesn't exist
os.makedirs("debug/motion_test_clips", exist_ok=True)

# Video parameters
width, height = 640, 480
fps = 30
duration = 10  # seconds
output_path = "debug/motion_test_clips/challenging_motion.mp4"

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Generate frames
total_frames = fps * duration
for i in range(total_frames):
    # Create a dark frame with low contrast
    frame = np.ones((height, width, 3), dtype=np.uint8) * 30  # Dark background
    
    # Add a moving object (slightly brighter rectangle)
    x_pos = int((i / total_frames) * (width - 100))
    
    # Make the object move in a sine wave pattern
    y_pos = int(height/2 + np.sin(i/20) * height/4)
    
    # Object brightness varies
    brightness = 50 + int(20 * np.sin(i/10))
    
    # Draw the object
    cv2.rectangle(frame, (x_pos, y_pos), (x_pos + 100, y_pos + 80), (brightness, brightness, brightness), -1)
    
    # Add significant noise (varies over time to simulate changing conditions)
    noise_level = 15 + 10 * np.sin(i/50)
    noise = np.random.randint(0, int(noise_level), (height, width, 3), dtype=np.uint8)
    frame = cv2.add(frame, noise)
    
    # Add some random bright spots (like reflections or light sources)
    if i % 10 == 0:
        spot_x = np.random.randint(0, width)
        spot_y = np.random.randint(0, height)
        cv2.circle(frame, (spot_x, spot_y), 20, (200, 200, 200), -1)
    
    # Simulate lighting changes
    if i > total_frames * 0.6 and i < total_frames * 0.7:
        # Sudden brightness increase (like turning on a light)
        frame = cv2.add(frame, np.ones_like(frame) * 50)
    
    # Simulate camera shake
    if i > total_frames * 0.3 and i < total_frames * 0.4:
        # Apply a small random translation
        M = np.float32([[1, 0, np.random.randint(-5, 5)], [0, 1, np.random.randint(-5, 5)]])
        frame = cv2.warpAffine(frame, M, (width, height))
    
    # Write the frame
    out.write(frame)
    
    # Print progress
    if i % 30 == 0:
        print(f"Generated {i}/{total_frames} frames")

# Release the VideoWriter
out.release()

print(f"Challenging test video created at {output_path}")
