# Arkos AI Testing Framework

This directory contains the testing framework for Arkos AI, a custom NVR system built on a Frigate fork.

## Overview

The Arkos AI testing framework is designed to validate all aspects of the system, including:

- Camera connectivity and RTSP streaming
- Object detection and tracking
- Audio analytics
- Enhancement features (zoom overlay, detail enhancement)
- MQTT messaging
- Event and alarm generation
- Timeline creation
- Monitoring center integration

## Test Structure

The tests are organized into the following directories:

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for component interactions
- `rtsp/`: Tests for RTSP stream connectivity and processing
- `performance/`: Performance and benchmark tests
- `e2e/`: End-to-end tests for complete workflows
- `fixtures/`: Test fixtures and sample data
- `docker/`: Docker configurations for test environments

## Running Tests

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- FFmpeg
- GStreamer (for RTSP streaming)

### Installation

Install the test dependencies:

```bash
pip install -r requirements-test.txt
```

### Running Tests Locally

Use the provided script to run tests:

```bash
# Run all tests
./scripts/run-tests.sh

# Run specific test types
./scripts/run-tests.sh --test-type=unit
./scripts/run-tests.sh --test-type=integration
./scripts/run-tests.sh --test-type=rtsp
./scripts/run-tests.sh --test-type=performance
./scripts/run-tests.sh --test-type=e2e

# Additional options
./scripts/run-tests.sh --verbose
./scripts/run-tests.sh --no-coverage
./scripts/run-tests.sh --skip-rtsp
./scripts/run-tests.sh --skip-media-gen
./scripts/run-tests.sh --skip-lint
```

### Running Tests in CI/CD

The tests are configured to run in GitHub Actions. See the workflow configuration in `.github/workflows/arkos-ai-tests.yml`.

## Test Components

### RTSP Simulator

The RTSP simulator provides test video streams for testing camera connectivity and video processing. It includes:

- Standard camera stream
- PTZ camera stream
- Audio-enabled camera stream
- Multi-object camera stream
- License plate camera stream

To start the RTSP simulator:

```bash
docker-compose -f tests/docker/rtsp-streams.yml up -d
```

### Test Fixtures

The test fixtures include:

- Sample videos for RTSP streaming
- Sample audio for audio analytics testing
- Test data for database operations
- Mock objects for unit testing

### Configuration

The test configuration is defined in `conftest.py`, which provides pytest fixtures for:

- Test paths and directories
- Default configuration
- Docker client
- RTSP simulator
- Mock objects
- Sample data
- Utility functions

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual components in isolation. Use mock objects to simulate dependencies.

Example:

```python
def test_video_analytics(mock_detector, mock_tracker, sample_frame):
    # Create video analytics with mock detector and tracker
    analytics = VideoAnalytics(
        camera_name="test_camera",
        config={"detect": {"enabled": True}},
        detector=mock_detector,
        tracker=mock_tracker,
    )
    
    # Process a frame
    result = analytics.process_frame(sample_frame, time.time())
    
    # Assert the result
    assert len(result) == 1
    assert result[0]["label"] == "person"
```

### Integration Tests

Integration tests should focus on testing the interaction between components.

Example:

```python
def test_event_generation(event_processor, sample_frame, sample_detection):
    # Process a detection
    event = event_processor.process(sample_detection, sample_frame)
    
    # Assert the event
    assert event is not None
    assert event["label"] == sample_detection["label"]
    assert event["has_snapshot"] is True
```

### RTSP Tests

RTSP tests should focus on testing camera connectivity and stream processing.

Example:

```python
def test_rtsp_connection(rtsp_simulator):
    # Create RTSP stream
    stream = RTSPStream(
        camera_name="test_camera",
        rtsp_url=rtsp_simulator["standard_url"],
        config={"detect": {"enabled": True}},
    )
    
    # Start the stream
    stream.start()
    
    # Assert the stream is connected
    assert stream.is_connected() is True
    
    # Get a frame
    frame = stream.get_frame()
    
    # Assert the frame is not None
    assert frame is not None
    
    # Stop the stream
    stream.stop()
```

### Performance Tests

Performance tests should focus on measuring the performance of the system.

Example:

```python
def test_frame_processing_speed(benchmark, video_analytics, sample_frame):
    # Benchmark frame processing
    result = benchmark(video_analytics.process_frame, sample_frame, time.time())
    
    # Assert the result
    assert result is not None
```

### End-to-End Tests

End-to-end tests should focus on testing complete workflows.

Example:

```python
def test_detection_to_notification(camera, video_analytics, event_processor, notification_manager):
    # Start the camera
    camera.start()
    
    # Get a frame
    frame = camera.get_frame()
    
    # Process the frame
    detections = video_analytics.process_frame(frame, time.time())
    
    # Process the detections
    events = []
    for detection in detections:
        event = event_processor.process(detection, frame)
        if event:
            events.append(event)
    
    # Send notifications
    for event in events:
        notification_manager.send_notification(event)
    
    # Assert notifications were sent
    assert notification_manager.get_notification_count() == len(events)
    
    # Stop the camera
    camera.stop()
```

## Code Coverage

The tests are configured to generate code coverage reports. The coverage reports are uploaded to Codecov in the CI/CD pipeline.

To generate a coverage report locally:

```bash
pytest --cov=arkos --cov-report=html
```

The coverage report will be available in the `htmlcov` directory.

## Continuous Integration

The tests are configured to run in GitHub Actions on every push and pull request. The workflow is defined in `.github/workflows/arkos-ai-tests.yml`.

The CI pipeline includes:

- Linting and code quality checks
- Unit tests
- Integration tests
- RTSP tests
- Performance tests
- End-to-end tests
- Code coverage reporting

## License

This testing framework is part of Arkos AI and is licensed under the same license as the main project.
