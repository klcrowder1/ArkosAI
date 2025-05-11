# Event Notifications

Arkos AI includes a comprehensive event notification system that allows you to receive alerts when events are detected by your cameras. This document explains how to configure and use the notification system.

## Overview

The notification system in Arkos AI is designed to be:

- **Flexible**: Support for multiple notification providers (MQTT, webhooks, etc.)
- **Configurable**: Fine-grained control over what events trigger notifications
- **Efficient**: Cooldown periods to prevent notification floods
- **Informative**: Rich notifications with images and video clips

When an event is detected (such as a person, vehicle, or audio event), the notification system can send alerts through various channels based on your configuration.

## Notification Providers

Arkos AI supports the following notification providers:

### Console

The console provider outputs notifications to the Arkos AI log. This is primarily useful for debugging and testing your notification configuration.

### MQTT

The MQTT provider sends notifications to an MQTT broker, which can be used to integrate with home automation systems like Home Assistant, Node-RED, or any other system that supports MQTT.

### Webhook

The webhook provider sends HTTP requests to specified URLs when events occur. This can be used to integrate with custom systems, third-party services, or trigger automation workflows.

## Configuration

Notification settings can be configured at both the global and camera-specific levels in your `config.yml` file.

### Global Configuration

Global notification settings apply to all cameras unless overridden at the camera level.

```yaml
# Global notification configuration
notifications:
  # Console notifications (for debugging)
  console:
    enabled: true
    pretty_print: true
    include_data: false
    log_level: INFO
  
  # MQTT notifications
  mqtt:
    enabled: true
    host: mqtt
    port: 1883
    username: user
    password: pass
    topic_prefix: arkos/notifications
  
  # Webhook notifications
  webhook:
    enabled: true
    urls:
      - http://example.com/webhook
    method: POST
    timeout: 10
    headers:
      Content-Type: application/json
    include_snapshot: true
    include_clip: false
    verify_ssl: true
    base_url: http://example.com/media
```

### Camera-Specific Configuration

Each camera can have its own notification settings that override the global configuration.

```yaml
cameras:
  front_door:
    # ... other camera settings ...
    
    # Notification configuration for this camera
    notifications:
      enabled: true
      # Notification triggers (tracked_object, audio, api)
      triggers:
        - tracked_object
        - audio
      # Object filters
      required_objects:
        - person
        - car
      filtered_objects:
        - dog
        - cat
      # Zone filters
      required_zones:
        - driveway
        - entrance
      filtered_zones:
        - ignore_zone
      # Cooldown period in seconds
      cooldown: 60
      # Notification content
      include_snapshot: true
      include_preview: false
      include_clip: false
      # Notification services to use (if empty, all enabled services will be used)
      services:
        - mqtt
        - webhook
```

## Configuration Options

### Global Notification Options

| Option | Description | Default |
|--------|-------------|---------|
| `console.enabled` | Enable console notifications | `true` |
| `console.pretty_print` | Format JSON data with indentation | `true` |
| `console.include_data` | Include full notification data in log | `false` |
| `console.log_level` | Log level for notifications | `INFO` |
| `mqtt.enabled` | Enable MQTT notifications | `false` |
| `mqtt.host` | MQTT broker hostname | `localhost` |
| `mqtt.port` | MQTT broker port | `1883` |
| `mqtt.username` | MQTT username | `null` |
| `mqtt.password` | MQTT password | `null` |
| `mqtt.topic_prefix` | Prefix for MQTT topics | `arkos/notifications` |
| `webhook.enabled` | Enable webhook notifications | `false` |
| `webhook.urls` | List of webhook URLs | `[]` |
| `webhook.method` | HTTP method (GET, POST, PUT) | `POST` |
| `webhook.timeout` | Request timeout in seconds | `10` |
| `webhook.headers` | HTTP headers | `{}` |
| `webhook.include_snapshot` | Include snapshot URL in payload | `true` |
| `webhook.include_clip` | Include clip URL in payload | `false` |
| `webhook.verify_ssl` | Verify SSL certificates | `true` |
| `webhook.base_url` | Base URL for media files | `null` |

### Camera-Specific Notification Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Enable notifications for this camera | `true` |
| `triggers` | Event types that trigger notifications | `[]` (all) |
| `required_objects` | Objects that should trigger notifications | `[]` (all) |
| `filtered_objects` | Objects that should not trigger notifications | `[]` |
| `required_zones` | Zones that should trigger notifications | `[]` (all) |
| `filtered_zones` | Zones that should not trigger notifications | `[]` |
| `cooldown` | Minimum time between notifications in seconds | `60` |
| `include_snapshot` | Include snapshot image in notification | `true` |
| `include_preview` | Include preview image in notification | `false` |
| `include_clip` | Include video clip in notification | `false` |
| `services` | Notification services to use | `[]` (all) |

## Notification Triggers

Notifications can be triggered by the following event types:

- `tracked_object`: Object detection events (person, car, etc.)
- `audio`: Audio detection events
- `api`: Events triggered via the API

## Notification Filtering

You can filter notifications based on various criteria:

### Object Filtering

- `required_objects`: Only send notifications for these object types
- `filtered_objects`: Do not send notifications for these object types

### Zone Filtering

- `required_zones`: Only send notifications for events in these zones
- `filtered_zones`: Do not send notifications for events in these zones

## Notification Cooldown

To prevent notification floods, you can set a cooldown period for each camera. The cooldown period is the minimum time between notifications for the same object type.

For example, if you set a cooldown of 60 seconds for a camera, and a person is detected, you will not receive another notification for a person on that camera for at least 60 seconds.

## Notification Content

Notifications can include the following content:

- `include_snapshot`: Include a snapshot image of the event
- `include_preview`: Include a preview image of the event
- `include_clip`: Include a video clip of the event

## MQTT Integration

MQTT notifications are sent to the following topics:

- `{topic_prefix}/{notification_type}/{camera}`: For camera-specific events
- `{topic_prefix}/{notification_type}`: For system-wide events

The payload is a JSON object containing the notification data.

## Webhook Integration

Webhook notifications are sent as HTTP requests to the configured URLs. The request body is a JSON object containing the notification data.

If `include_snapshot` or `include_clip` is enabled, the notification will include URLs to the media files. If `base_url` is configured, the URLs will be absolute; otherwise, they will be relative.

## Example Notification Payload

Here's an example of a notification payload for a person detection event:

```json
{
  "id": "event_1234567890_1620000000",
  "title": "Person detected",
  "message": "Person detected on front_door",
  "timestamp": 1620000000,
  "notification_type": "event",
  "priority": "medium",
  "source": "arkos",
  "camera": "front_door",
  "event_id": "1234567890",
  "snapshot_path": "/clips/front_door/1234567890/snapshot.jpg",
  "clip_path": "/clips/front_door/1234567890/clip.mp4",
  "preview_path": null,
  "event_type": "tracked_object",
  "label": "person",
  "score": 0.95,
  "zones": ["driveway"],
  "data": {
    "event_type": "tracked_object",
    "label": "person",
    "score": 0.95,
    "zones": ["driveway"],
    "detection_time": "2021-05-03T12:00:00.000Z",
    "created_at": "2021-05-03T12:00:00.000Z"
  }
}
```

## Troubleshooting

If you're not receiving notifications, check the following:

1. Ensure the notification provider is enabled in your configuration.
2. Check the Arkos AI logs for any errors related to notifications.
3. Verify that your notification filters are not too restrictive.
4. Check that the cooldown period has elapsed since the last notification.
5. For MQTT, verify that your broker is running and accessible.
6. For webhooks, verify that your server is running and accessible.

## Advanced Usage

### Custom Notification Templates

You can customize the notification title and message by modifying the event handler code. This requires modifying the source code and is not recommended for most users.

### Integration with Home Automation Systems

The notification system can be integrated with home automation systems like Home Assistant, Node-RED, or any other system that supports MQTT or webhooks.

#### Home Assistant Example

```yaml
mqtt:
  sensor:
    - name: "Arkos Notifications"
      state_topic: "arkos/notifications/event/#"
      value_template: "{{ value_json.message }}"
      json_attributes_topic: "arkos/notifications/event/#"
      json_attributes_template: "{{ value_json | tojson }}"
```

#### Node-RED Example

Create a flow that subscribes to the MQTT topic `arkos/notifications/#` and processes the notifications as needed.

## Conclusion

The notification system in Arkos AI provides a flexible and powerful way to receive alerts when events are detected. By configuring the notification providers and filters, you can ensure that you only receive the notifications that are important to you.
