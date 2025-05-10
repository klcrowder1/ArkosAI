# Arkos AI Motion Detection

This module provides motion detection capabilities for the Arkos AI system. It includes multiple implementations of motion detection algorithms with different performance characteristics and features.

## Motion Detector Interface

All motion detectors implement the `MotionDetector` abstract base class, which defines the following interface:

```python
class MotionDetector(ABC):
    @abstractmethod
    def __init__(
        self,
        frame_shape: Tuple[int, int, int],
        config: MotionConfig,
        fps: int,
        **kwargs
    ):
        pass

    @abstractmethod
    def detect(self, frame):
        pass

    @abstractmethod
    def is_calibrating(self):
        pass

    @abstractmethod
    def stop(self):
        pass
```

## Available Implementations

### FrigateMotionDetector

The original motion detection implementation from Frigate NVR. It provides basic motion detection capabilities.

### ImprovedMotionDetector

An improved version of the motion detector with better handling of PTZ cameras and improved contrast enhancement.

### OptimizedMotionDetector

The latest and most optimized motion detector implementation with the following features:

- **Adaptive Thresholding**: Dynamically adjusts thresholds based on noise levels and detection history
- **Efficient Contrast Enhancement**: Uses sampling instead of full percentile calculations for better performance
- **Selective Gaussian Blur**: Only applies blur when noise levels are high
- **Improved PTZ Camera Handling**: Better detection during and after camera movements
- **Noise Estimation**: Estimates noise levels in the frame to reduce false positives
- **Performance Monitoring**: Tracks processing times and detection rates
- **Optimized Calibration**: Faster and more accurate calibration process

## Configuration

Motion detection is configured through the `MotionConfig` class, which includes the following parameters:

- `enabled`: Enable/disable motion detection
- `threshold`: Motion detection threshold (1-255)
- `lightning_threshold`: Threshold for detecting sudden lighting changes (0.3-1.0)
- `improve_contrast`: Enable/disable contrast enhancement
- `contour_area`: Minimum contour area to consider as motion
- `delta_alpha`: Weight for accumulating frame deltas
- `frame_alpha`: Weight for accumulating frames
- `frame_height`: Height to resize frames to for processing
- `mask`: Mask to apply to frames to ignore certain areas

## Benchmarking

You can benchmark the different motion detector implementations using the `benchmark_motion.py` script:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-benchmark.txt

# Create a test video
python3 create_test_video.py

# Run the benchmark
python3 benchmark_motion.py
```

The benchmark will compare the performance of the different motion detector implementations and provide metrics on processing time and detection accuracy.

## Performance Considerations

- The `OptimizedMotionDetector` is generally the most efficient and accurate implementation
- For low-power devices, consider using a higher `frame_height` value to reduce processing requirements
- Use masks to exclude areas where motion detection is not needed
- Adjust the `threshold` parameter based on the environment and camera characteristics
