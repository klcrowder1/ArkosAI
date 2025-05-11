# Event Correlation

Arkos AI provides a powerful event correlation system that allows you to identify relationships between different events and enhance the overall understanding of what's happening in your monitored areas. This feature helps reduce false positives, improve event categorization, and provide more meaningful notifications.

## Overview

Event correlation analyzes events from different sources (object detection, audio detection, API triggers) and identifies relationships between them based on temporal, spatial, and semantic factors. When events are correlated, they are linked together and can be viewed as a group, providing a more comprehensive understanding of the situation.

For example, a person detection event might be correlated with a speech audio event if they occur at the same time and in the same location, indicating that someone is talking. Similarly, a car detection event might be correlated with an engine sound event, providing stronger evidence that a vehicle is present.

## Configuration

Event correlation can be configured at both the global level and the camera-specific level. The global configuration applies to all cameras, while camera-specific configurations override or extend the global settings.

### Global Configuration

To configure event correlation at the global level, add a `correlation` section to the `events` section of your configuration file:

```yaml
events:
  correlation:
    enabled: true
    window: 30
    spatial_threshold: 0.1
    severity_upgrade: true
    cross_camera: false
    rules:
      audio_object:
        speech_person: true
        bark_dog: true
        meow_cat: true
        engine_vehicle: true
```

### Camera-Specific Configuration

To configure event correlation for a specific camera, add a `correlation` section to the camera's `events` configuration:

```yaml
cameras:
  front_door:
    # ... other camera configuration ...
    events:
      # ... other event configuration ...
      correlation:
        enabled: true
        window: 15
        spatial_threshold: 0.2
        severity_upgrade: true
        cross_camera: false
        rules:
          audio_object:
            speech_person: true
            doorbell_person: true
```

## Configuration Options

The following options are available for event correlation:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable event correlation |
| `window` | integer | `30` | Time window in seconds for correlation |
| `spatial_threshold` | float | `0.1` | Spatial correlation threshold (IoU) |
| `severity_upgrade` | boolean | `true` | Upgrade severity of correlated events |
| `cross_camera` | boolean | `false` | Enable cross-camera correlation |
| `rules` | object | `{}` | Custom correlation rules |

### Correlation Rules

Correlation rules allow you to define specific relationships between different types of events. The following rule types are available:

#### Audio-Object Correlation

Audio-object correlation rules define relationships between audio events and tracked object events. The following predefined correlations are available:

- `speech_person`: Correlate speech audio events with person detection events
- `bark_dog`: Correlate bark audio events with dog detection events
- `meow_cat`: Correlate meow audio events with cat detection events
- `engine_vehicle`: Correlate engine audio events with vehicle detection events (car, truck, motorcycle)

You can enable or disable these predefined correlations, or add your own custom correlations:

```yaml
correlation:
  rules:
    audio_object:
      speech_person: true
      bark_dog: true
      meow_cat: true
      engine_vehicle: true
      custom:
        doorbell_person: true
        glass_break_window: true
```

## How Correlation Works

Event correlation is applied at the event processing stage, after events are filtered but before they are stored in the database. When an event is received, the following steps are performed:

1. The event is processed and filtered as usual.
2. If event correlation is enabled, the event is added to the correlation engine.
3. The correlation engine checks for temporal, spatial, and semantic correlations with other recent events.
4. If correlations are found, the events are linked together and their metadata is updated.
5. If severity upgrade is enabled, the severity of correlated events may be increased based on the correlation.
6. The events are stored in the database with their updated metadata.

### Temporal Correlation

Temporal correlation is based on the time overlap between events. Two events are considered temporally correlated if they overlap in time, or if they occur within the configured correlation window of each other.

### Spatial Correlation

Spatial correlation is based on the spatial overlap between tracked object events. Two tracked object events are considered spatially correlated if they share any zones, or if their bounding boxes overlap with an Intersection over Union (IoU) value above the configured spatial threshold.

### Semantic Correlation

Semantic correlation is based on the semantic relationship between events of different types. For example, a speech audio event and a person detection event have a semantic relationship because speech is typically produced by people.

## Viewing Correlated Events

Correlated events are linked together in the database and can be viewed as a group in the Arkos AI web interface. When viewing an event, any correlated events will be displayed in the "Related Events" section.

## Examples

### Basic Correlation

To enable basic event correlation with default settings:

```yaml
events:
  correlation:
    enabled: true
```

### Custom Correlation Window

To set a custom correlation window:

```yaml
events:
  correlation:
    enabled: true
    window: 15  # 15 seconds
```

### Disable Severity Upgrade

To disable automatic severity upgrade for correlated events:

```yaml
events:
  correlation:
    enabled: true
    severity_upgrade: false
```

### Custom Correlation Rules

To define custom correlation rules:

```yaml
events:
  correlation:
    enabled: true
    rules:
      audio_object:
        speech_person: true
        doorbell_person: true
        glass_break_window: true
```

## Best Practices

- Start with the default correlation settings and adjust as needed.
- Use a shorter correlation window for high-traffic areas to reduce false correlations.
- Use a longer correlation window for low-traffic areas to increase the chance of finding correlations.
- Enable severity upgrade to automatically increase the severity of correlated events.
- Define custom correlation rules for your specific use case.
- Monitor the correlation results and adjust the settings as needed.
