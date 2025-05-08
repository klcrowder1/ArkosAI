# Analytics Module

The Analytics module provides enhanced video and audio analytics capabilities for Arkos AI, extending the basic object detection provided by the Core module with advanced features like custom model integration, activity recognition, and audio analytics.

## Overview

The Analytics module is responsible for:

- Advanced object detection with custom models
- Activity recognition and behavioral analysis
- Audio event detection and analysis
- Multi-modal integration for improved accuracy

## Architecture

The Analytics module is structured as follows:

```
analytics/
├── video/               # Video analytics components
│   ├── detection/       # Enhanced object detection
│   ├── activity/        # Activity recognition
│   ├── behavior/        # Behavioral analysis
│   └── models/          # Custom model management
├── audio/               # Audio analytics components
│   ├── detection/       # Audio event detection
│   ├── speech/          # Speech and voice analytics
│   └── models/          # Audio model management
├── multimodal/          # Multi-modal integration
├── api/                 # API endpoints
└── service/             # Core service functionality
```

### Key Components

1. **Video Analytics Engine**: Processes video frames for enhanced object detection and activity recognition
2. **Custom Model Manager**: Manages custom YOLO and other ML models
3. **Activity Recognition Engine**: Analyzes object movements and interactions
4. **Behavioral Analysis Engine**: Identifies patterns and anomalies in behavior
5. **Audio Analytics Engine**: Processes audio for event detection and analysis
6. **Multi-modal Integration Engine**: Combines video and audio analytics for improved accuracy

## Configuration

The Analytics module is configured through the main configuration file. Here's an example configuration:

```yaml
analytics:
  # Video analytics configuration
  video:
    enabled: true
    
    # Custom model configuration
    models:
      - name: "Package Detection"
        type: "YOLOv8"
        path: "/models/custom/package_detection.pt"
        confidence_threshold: 0.65
        classes:
          - id: 0
            name: "small_package"
          - id: 1
            name: "medium_package"
          - id: 2
            name: "large_package"
      
      - name: "Vehicle Classification"
        type: "YOLOv8"
        path: "/models/custom/vehicle_classification.pt"
        confidence_threshold: 0.7
        classes:
          - id: 0
            name: "car"
          - id: 1
            name: "truck"
          - id: 2
            name: "motorcycle"
          - id: 3
            name: "bicycle"
    
    # Activity recognition configuration
    activity:
      enabled: true
      types:
        - name: "walking"
          confidence_threshold: 0.6
        - name: "running"
          confidence_threshold: 0.7
        - name: "standing"
          confidence_threshold: 0.6
        - name: "sitting"
          confidence_threshold: 0.6
    
    # Behavioral analysis configuration
    behavior:
      enabled: true
      types:
        - name: "loitering"
          duration_threshold: 60  # seconds
        - name: "pacing"
          repetition_threshold: 3
        - name: "approach_door"
          distance_threshold: 2.0  # meters
  
  # Audio analytics configuration
  audio:
    enabled: true
    
    # Audio event detection configuration
    detectors:
      - name: "Glass Break Detector"
        type: "frequency_pattern"
        frequency_range: [4000, 10000]  # Hz
        pattern: "sudden_peak"
        threshold: 75  # dB
        min_duration: 0.2  # seconds
        
      - name: "Alarm Sound Detector"
        type: "frequency_pattern"
        frequency_range: [2500, 4000]  # Hz
        pattern: "oscillating"
        threshold: 70  # dB
        min_duration: 1.0  # seconds
    
    # Speech analytics configuration
    speech:
      enabled: true
      language: "en-US"
      keywords:
        - "help"
        - "emergency"
        - "fire"
      aggression_detection:
        enabled: true
        threshold: 0.7
  
  # Multi-modal integration configuration
  multimodal:
    enabled: true
    integration_methods:
      - name: "temporal_correlation"
        time_window: 2.0  # seconds
      - name: "spatial_correlation"
        distance_threshold: 3.0  # meters
    confidence_boost: 0.2  # Confidence boost for correlated detections
```

## Camera-Specific Model Assignment

Models can be assigned to specific cameras:

```yaml
camera_models:
  - camera: "front_door"
    models:
      - name: "Package Detection"
        enabled: true
        zones: ["porch", "driveway"]
        schedule: "always"
      - name: "Person Detection"  # Core Frigate model
        enabled: true
        zones: ["all"]
        schedule: "always"
```

## API

The Analytics module provides the following API endpoints:

### Video Analytics API

- `GET /api/analytics/video/models`: List all video analytics models
- `GET /api/analytics/video/models/{model_id}`: Get model details
- `POST /api/analytics/video/models`: Upload a new model
- `DELETE /api/analytics/video/models/{model_id}`: Delete a model
- `GET /api/analytics/video/activities`: List detected activities
- `GET /api/analytics/video/behaviors`: List detected behaviors

### Audio Analytics API

- `GET /api/analytics/audio/detectors`: List all audio detectors
- `GET /api/analytics/audio/events`: List detected audio events
- `GET /api/analytics/audio/speech`: List detected speech events

### Multi-modal API

- `GET /api/analytics/multimodal/events`: List multi-modal events

## Integration with Other Modules

The Analytics module integrates with other Arkos AI modules through the following interfaces:

### Core Module

- Receives video frames from the Core module
- Sends detection results to the Core module
- Enhances events with additional analytics data

### Audio Module

- Receives audio streams from the Audio module
- Sends audio analytics results to the Audio module

### Health Module

- Provides analytics performance metrics
- Contributes to camera health assessment

### Timeline Module

- Provides enhanced event data for timeline generation
- Contributes activity and behavior data for day-in-the-life analytics

## Dependencies

The Analytics module depends on:

- TensorFlow or PyTorch for machine learning models
- OpenCV for image processing
- Librosa for audio processing
- ONNX Runtime for model inference optimization

## Examples

### Using Custom Models

```python
from arkos.analytics.video.models import model_manager

# Load a custom model
model = model_manager.load_model("Package Detection")

# Process a frame with the model
results = model.detect(frame)

# Process results
for detection in results:
    print(f"Detected {detection.class_name} with confidence {detection.confidence}")
    print(f"Bounding box: {detection.bbox}")
```

### Activity Recognition

```python
from arkos.analytics.video.activity import activity_recognizer

# Process a sequence of frames for activity recognition
activity = activity_recognizer.recognize(frames)

print(f"Detected activity: {activity.name} with confidence {activity.confidence}")
print(f"Duration: {activity.duration} seconds")
```

### Audio Event Detection

```python
from arkos.analytics.audio.detection import audio_detector

# Process audio data for event detection
events = audio_detector.detect(audio_data)

for event in events:
    print(f"Detected audio event: {event.name} at {event.timestamp}")
    print(f"Confidence: {event.confidence}, Duration: {event.duration} seconds")
```

### Multi-modal Integration

```python
from arkos.analytics.multimodal import multimodal_integrator

# Integrate video and audio events
integrated_events = multimodal_integrator.integrate(video_events, audio_events)

for event in integrated_events:
    print(f"Integrated event: {event.name} at {event.timestamp}")
    print(f"Video confidence: {event.video_confidence}, Audio confidence: {event.audio_confidence}")
    print(f"Combined confidence: {event.combined_confidence}")
