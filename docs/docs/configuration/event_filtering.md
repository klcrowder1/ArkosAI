# Event Filtering

Event filtering allows you to control which events are processed and stored based on various criteria. This feature helps reduce noise, focus on important events, and optimize storage usage.

## Configuration

Event filtering can be configured at both the global level and the camera-specific level. The global configuration applies to all cameras, while camera-specific configurations override or extend the global settings.

### Global Configuration

To configure event filtering at the global level, add an `events` section to your configuration file:

```yaml
events:
  enabled: true
  # Global filter that applies to all event types
  global_filter:
    min_score: 0.6
    min_duration: 2.0
    severities:
      - alert
      - detection
  # Event type-specific filters
  filters:
    tracked_object:
      min_score: 0.7
      labels:
        - person
        - car
        - truck
      exclude_labels:
        - dog
        - cat
    audio:
      min_score: 0.8
      min_duration: 3.0
    api:
      min_duration: 5.0
```

### Camera-Specific Configuration

To configure event filtering for a specific camera, add an `events` section to the camera configuration:

```yaml
cameras:
  front_door:
    # ... other camera configuration ...
    events:
      enabled: true
      # Global filter that applies to all event types for this camera
      global_filter:
        min_score: 0.65
        min_duration: 1.5
        zones:
          - entrance
          - driveway
        categories:
          - security
          - monitoring
      # Event type-specific filters
      filters:
        tracked_object:
          min_score: 0.75
          labels:
            - person
            - car
          exclude_zones:
            - ignore_zone
          confidence_levels:
            - high
            - medium
        audio:
          min_score: 0.85
          sources:
            - microphone
        api:
          custom_filters:
            trigger_type: manual
```

## Filter Options

The following filter options are available for event filtering:

### Common Filter Options

These options apply to all event types:

| Option | Type | Description |
|--------|------|-------------|
| `min_score` | float | Minimum confidence score for events (0.0-1.0) |
| `max_score` | float | Maximum confidence score for events (0.0-1.0) |
| `min_duration` | float | Minimum duration for events in seconds |
| `max_duration` | float | Maximum duration for events in seconds |
| `labels` | list | Labels to include in filtering |
| `exclude_labels` | list | Labels to exclude from filtering |
| `zones` | list | Zones to include in filtering |
| `exclude_zones` | list | Zones to exclude from filtering |
| `categories` | list | Categories to include in filtering (security, monitoring, analytics, system, custom) |
| `exclude_categories` | list | Categories to exclude from filtering |
| `severities` | list | Severities to include in filtering (alert, detection, info) |
| `exclude_severities` | list | Severities to exclude from filtering |
| `confidence_levels` | list | Confidence levels to include in filtering (high, medium, low) |
| `exclude_confidence_levels` | list | Confidence levels to exclude from filtering |
| `tags` | list | Tags to include in filtering |
| `exclude_tags` | list | Tags to exclude from filtering |
| `sources` | list | Sources to include in filtering |
| `exclude_sources` | list | Sources to exclude from filtering |
| `custom_filters` | object | Custom filters for events |

### Event Type-Specific Filters

#### Tracked Object Events

Tracked object events are generated when objects are detected and tracked in the camera feed. In addition to the common filter options, tracked object events support the following specific filters:

- `min_area`: Minimum area for object detection
- `max_area`: Maximum area for object detection
- `min_ratio`: Minimum aspect ratio for object detection
- `max_ratio`: Maximum aspect ratio for object detection

#### Audio Events

Audio events are generated when audio is detected in the camera feed. Audio events use the common filter options.

#### API Events

API events are generated when external systems trigger events through the API. API events use the common filter options.

## Examples

### Filter Out Low-Confidence Events

To filter out events with low confidence scores:

```yaml
events:
  enabled: true
  global_filter:
    min_score: 0.7
```

### Filter Events by Label

To only include events with specific labels:

```yaml
events:
  enabled: true
  filters:
    tracked_object:
      labels:
        - person
        - car
```

### Filter Events by Zone

To only include events in specific zones:

```yaml
events:
  enabled: true
  global_filter:
    zones:
      - entrance
      - driveway
```

### Filter Events by Duration

To filter out short events:

```yaml
events:
  enabled: true
  global_filter:
    min_duration: 5.0
```

### Combine Multiple Filters

You can combine multiple filters to create complex filtering rules:

```yaml
events:
  enabled: true
  global_filter:
    min_score: 0.7
    min_duration: 3.0
    zones:
      - entrance
      - driveway
    categories:
      - security
    severities:
      - alert
```

## Best Practices

- Start with conservative filter settings and adjust as needed.
- Use the global filter for common filtering rules that apply to all event types.
- Use event type-specific filters for more granular control.
- Consider using different filter settings for different cameras based on their location and purpose.
- Regularly review your filter settings to ensure they are still appropriate for your needs.

For more detailed information about event filtering, see the [Event Filtering](../../features/event-filtering.md) feature documentation.
