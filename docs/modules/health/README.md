# Health Module

The Health module provides comprehensive camera health monitoring capabilities for Arkos AI, ensuring that cameras are functioning properly and providing high-quality video feeds.

## Overview

The Health module is responsible for:

- Connectivity monitoring for cameras
- Bandwidth and latency tracking
- Dirty lens detection
- Scene change detection
- Health status reporting and alerting

## Architecture

The Health module is structured as follows:

```
health/
├── connectivity/        # Connectivity monitoring components
├── quality/             # Video quality monitoring components
│   ├── dirty_lens/      # Dirty lens detection
│   └── scene_change/    # Scene change detection
├── metrics/             # Health metrics collection and analysis
├── alerts/              # Alert generation and management
├── api/                 # API endpoints
└── service/             # Core service functionality
```

### Key Components

1. **Connectivity Monitor**: Monitors camera connectivity, bandwidth, and latency
2. **Quality Monitor**: Analyzes video quality for issues like dirty lenses
3. **Scene Change Detector**: Detects changes in the camera's field of view
4. **Metrics Collector**: Collects and analyzes health metrics
5. **Alert Manager**: Generates and manages alerts for health issues

## Configuration

The Health module is configured through the main configuration file. Here's an example configuration:

```yaml
health:
  # Global health monitoring configuration
  enabled: true
  check_interval: 60  # seconds
  
  # Connectivity monitoring configuration
  connectivity:
    enabled: true
    timeout: 5  # seconds
    retry_count: 3
    bandwidth_check:
      enabled: true
      interval: 300  # seconds
    latency_check:
      enabled: true
      interval: 60  # seconds
  
  # Quality monitoring configuration
  quality:
    enabled: true
    
    # Dirty lens detection configuration
    dirty_lens:
      enabled: true
      check_interval: 3600  # seconds
      sensitivity: "medium"  # low, medium, high
      threshold: 0.7
      reference_update_interval: 86400  # seconds (24 hours)
    
    # Scene change detection configuration
    scene_change:
      enabled: true
      check_interval: 300  # seconds
      sensitivity: "medium"  # low, medium, high
      threshold: 0.6
      reference_update_mode: "manual"  # auto, scheduled, manual
  
  # Alerts configuration
  alerts:
    enabled: true
    channels:
      - type: "mqtt"
        topic: "arkos/alerts/health"
      - type: "webhook"
        url: "http://example.com/webhook"
      - type: "email"
        recipients: ["admin@example.com"]
    
    # Alert types
    types:
      connectivity:
        enabled: true
        severity: "critical"
        throttle_interval: 300  # seconds
      
      dirty_lens:
        enabled: true
        severity: "warning"
        throttle_interval: 3600  # seconds
      
      scene_change:
        enabled: true
        severity: "warning"
        throttle_interval: 300  # seconds
```

## Camera-Specific Configuration

Health monitoring can be configured for specific cameras:

```yaml
camera_health:
  - camera: "front_door"
    connectivity:
      enabled: true
      check_interval: 30  # seconds
    
    dirty_lens:
      enabled: true
      sensitivity: "high"
    
    scene_change:
      enabled: true
      sensitivity: "low"
      reference_zones:
        - name: "door_area"
          coordinates: [100, 100, 300, 400]
          sensitivity: "high"
```

## API

The Health module provides the following API endpoints:

### Health Status API

- `GET /api/health/status`: Get overall health status
- `GET /api/health/status/{camera_id}`: Get health status for a specific camera

### Connectivity API

- `GET /api/health/connectivity`: Get connectivity status for all cameras
- `GET /api/health/connectivity/{camera_id}`: Get connectivity status for a specific camera
- `POST /api/health/connectivity/{camera_id}/test`: Test connectivity for a specific camera

### Quality API

- `GET /api/health/quality`: Get quality status for all cameras
- `GET /api/health/quality/{camera_id}`: Get quality status for a specific camera
- `GET /api/health/quality/{camera_id}/dirty_lens`: Get dirty lens status for a specific camera
- `POST /api/health/quality/{camera_id}/dirty_lens/reset`: Reset dirty lens reference for a specific camera
- `GET /api/health/quality/{camera_id}/scene_change`: Get scene change status for a specific camera
- `POST /api/health/quality/{camera_id}/scene_change/reset`: Reset scene change reference for a specific camera

### Alerts API

- `GET /api/health/alerts`: Get all health alerts
- `GET /api/health/alerts/{alert_id}`: Get a specific health alert
- `PUT /api/health/alerts/{alert_id}/acknowledge`: Acknowledge a health alert
- `DELETE /api/health/alerts/{alert_id}`: Delete a health alert

## Integration with Other Modules

The Health module integrates with other Arkos AI modules through the following interfaces:

### Core Module

- Receives camera information from the Core module
- Sends health status updates to the Core module
- Affects recording quality assessment

### Analytics Module

- Provides quality metrics for analytics accuracy assessment
- Receives analytics performance metrics

### UI Module

- Provides health status information for the dashboard
- Provides alerts for the user interface

### Notify Module

- Sends health alerts to the notification system

## Dependencies

The Health module depends on:

- OpenCV for image processing and analysis
- Network tools for connectivity monitoring
- MQTT for alert publishing
- Database for storing health metrics and alerts

## Examples

### Monitoring Camera Health

```python
from arkos.health import health_manager

# Get health status for all cameras
status = health_manager.get_status()

for camera_id, camera_status in status.items():
    print(f"Camera: {camera_id}")
    print(f"  Connectivity: {camera_status.connectivity.status}")
    print(f"  Bandwidth: {camera_status.connectivity.bandwidth} Mbps")
    print(f"  Latency: {camera_status.connectivity.latency} ms")
    print(f"  Dirty Lens: {camera_status.quality.dirty_lens.status}")
    print(f"  Scene Change: {camera_status.quality.scene_change.status}")
```

### Handling Health Alerts

```python
from arkos.health.alerts import alert_manager

# Get active alerts
alerts = alert_manager.get_active_alerts()

for alert in alerts:
    print(f"Alert: {alert.id}")
    print(f"  Type: {alert.type}")
    print(f"  Camera: {alert.camera_id}")
    print(f"  Severity: {alert.severity}")
    print(f"  Timestamp: {alert.timestamp}")
    print(f"  Message: {alert.message}")
    
    # Acknowledge the alert
    alert_manager.acknowledge_alert(alert.id)
```

### Managing Dirty Lens Detection

```python
from arkos.health.quality.dirty_lens import dirty_lens_detector

# Check for dirty lens
camera_id = "front_door"
result = dirty_lens_detector.check(camera_id)

if result.is_dirty:
    print(f"Camera {camera_id} has a dirty lens")
    print(f"  Confidence: {result.confidence}")
    print(f"  Affected areas: {result.affected_areas}")
    
    # Reset the reference image
    dirty_lens_detector.reset_reference(camera_id)
```

### Managing Scene Change Detection

```python
from arkos.health.quality.scene_change import scene_change_detector

# Check for scene changes
camera_id = "front_door"
result = scene_change_detector.check(camera_id)

if result.has_changed:
    print(f"Camera {camera_id} scene has changed")
    print(f"  Confidence: {result.confidence}")
    print(f"  Changed areas: {result.changed_areas}")
    
    # Update the reference image
    scene_change_detector.update_reference(camera_id)
