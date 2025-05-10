# Object Detection Pipeline Refactoring Implementation

This document describes the implementation of the refactored object detection pipeline for Arkos AI. It provides an overview of the new architecture, key components, and usage examples.

## Overview

The refactored object detection pipeline provides a modular, extensible framework for object detection in Arkos AI. It addresses the issues identified in the [Object Detection Pipeline Refactoring Plan](./object-detection-refactoring-plan.md) by:

1. Improving modularity through clear separation of concerns
2. Enhancing extensibility with a plugin-based architecture
3. Standardizing patterns across detector implementations
4. Simplifying configuration with a streamlined structure
5. Reducing duplication by centralizing common functionality

## Architecture

The refactored architecture consists of the following key components:

### Core Components

#### `DetectorInterface` (Abstract Class)

The `DetectorInterface` defines the contract for all detector implementations. It provides:

- Common functionality through default implementations
- Abstract methods that must be implemented by subclasses
- Standardized error handling and logging
- Support for the context manager protocol

```python
from frigate.object_detection import DetectorInterface

class MyDetector(DetectorInterface):
    def detect_raw(self, tensor_input):
        # Implementation goes here
        pass
```

#### `DetectorRegistry` (Singleton)

The `DetectorRegistry` manages the registration and creation of detector implementations. It provides:

- Registration of detector implementations
- Factory methods for creating detector instances
- Dynamic discovery of detector implementations
- Support for third-party detector plugins

```python
from frigate.object_detection import DetectorRegistry, register_detector

# Register a detector
@register_detector("my_detector")
class MyDetector(DetectorInterface):
    # Implementation goes here
    pass

# Create a detector
detector = DetectorRegistry.create_detector(detector_config)
```

#### `DetectionPipeline` (Orchestrator)

The `DetectionPipeline` orchestrates the detection process. It handles:

- Preprocessing of input tensors
- Detection using the appropriate detector
- Postprocessing of detection results
- Management of detector lifecycle

```python
from frigate.object_detection import DetectionPipeline

# Create a pipeline
pipeline = DetectionPipeline(detector_config)

# Perform detection
detections = pipeline.detect(tensor_input)
```

### Utilities

#### `PreprocessingUtils` (Static Methods)

The `PreprocessingUtils` class provides utilities for preprocessing input tensors. It includes methods for:

- Normalization
- Channel ordering
- Data type conversion
- Resizing
- Color format conversion

```python
from frigate.object_detection import PreprocessingUtils

# Preprocess input tensor
processed_tensor = PreprocessingUtils.preprocess(
    tensor,
    width=320,
    height=320,
    input_format="nhwc",
    color_format="rgb",
    dtype="float",
)
```

#### `PostprocessingUtils` (Static Methods)

The `PostprocessingUtils` class provides utilities for postprocessing detection results. It includes methods for:

- Non-maximum suppression
- Bounding box conversion
- Filtering
- Scaling
- Clipping
- Merging

```python
from frigate.object_detection import PostprocessingUtils

# Apply non-maximum suppression
filtered_boxes, filtered_scores, filtered_classes = PostprocessingUtils.non_maximum_suppression(
    boxes, scores, classes, iou_threshold=0.5
)
```

### Detector Implementations

The refactored architecture includes implementations of the `DetectorInterface` for various detector types:

- `CpuTflDetector`: CPU-based TensorFlow Lite detector
- Additional detector implementations can be added as needed

## Usage Examples

### Basic Usage

```python
from frigate.detectors.detector_config import BaseDetectorConfig, ModelConfig
from frigate.object_detection import DetectionPipeline

# Create model configuration
model_config = ModelConfig(
    path="/path/to/model.tflite",
    labelmap_path="/path/to/labelmap.txt",
    width=320,
    height=320,
)

# Create detector configuration
detector_config = BaseDetectorConfig(
    type="cpu",
    model=model_config,
)

# Create detection pipeline
pipeline = DetectionPipeline(detector_config)

# Perform detection
detections = pipeline.detect(tensor_input)

# Process detection results
for label, score, bbox in detections:
    print(f"Detected {label} with confidence {score} at {bbox}")

# Clean up
pipeline.cleanup()
```

### Using the Detection Process

```python
from frigate.detectors.detector_config import BaseDetectorConfig, ModelConfig
from frigate.object_detection import DetectionProcess

# Create detector configuration
detector_config = BaseDetectorConfig(
    type="cpu",
    model=ModelConfig(
        path="/path/to/model.tflite",
        width=320,
        height=320,
    ),
)

# Create detection process
detection_process = DetectionProcess(
    name="my_detector",
    detection_queue=queue,
    out_events=events,
    detector_config=detector_config,
)

# Start the detection process
detection_process.start_or_restart()

# Stop the detection process
detection_process.stop()
```

### Creating a Custom Detector

```python
from frigate.object_detection import DetectorInterface, register_detector

@register_detector("my_custom_detector")
class MyCustomDetector(DetectorInterface):
    def _initialize_detector(self):
        # Initialize detector-specific resources
        pass
    
    def detect_raw(self, tensor_input):
        # Perform detection
        pass
    
    def cleanup(self):
        # Clean up resources
        pass
```

## Integration with Existing Code

The refactored object detection pipeline is designed to be compatible with the existing codebase. It provides:

1. A drop-in replacement for the existing object detection functionality
2. Backward compatibility with existing configurations
3. The same detection results with improved architecture
4. Comparable performance characteristics

## Performance Considerations

The refactored architecture is designed to minimize overhead and maintain performance:

1. Minimal abstraction layers to reduce overhead
2. Optimized critical paths in the detection process
3. Efficient memory management with shared memory
4. Comparable performance to the original implementation

## Future Enhancements

The refactored architecture provides a foundation for future enhancements:

1. Support for additional detector types
2. Integration with hardware acceleration
3. Enhanced preprocessing and postprocessing capabilities
4. Improved error handling and recovery
5. Better integration with the event system

## Conclusion

The refactored object detection pipeline provides a more modular, extensible, and maintainable architecture for object detection in Arkos AI. It addresses the issues identified in the refactoring plan while maintaining compatibility with the existing codebase and performance characteristics.
