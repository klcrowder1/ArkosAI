# Camera Configuration in Arkos AI

Arkos AI provides comprehensive and flexible camera configuration options, allowing you to customize every aspect of your camera setup to meet your specific needs.

## Overview

The camera configuration system in Arkos AI is designed to be:

- **Modular**: Each aspect of camera functionality is configured separately
- **Hierarchical**: Global settings can be overridden at the camera level
- **Extensible**: New configuration options can be added easily
- **Validated**: Configuration values are validated to ensure correctness

## Basic Camera Configuration

Here's a basic example of a camera configuration:

```yaml
cameras:
  front_door:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://username:password@camera-ip:554/stream
          roles:
            - detect
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
      fps: 5
```

## Camera Types

Arkos AI supports different camera types, each optimized for specific use cases:

- **default**: Standard camera configuration
- **lpr**: Optimized for license plate recognition
- **face**: Optimized for face detection and recognition
- **specialized**: Custom configuration for specialized use cases
- **ptz**: Pan-Tilt-Zoom cameras with movement capabilities
- **thermal**: Thermal imaging cameras for temperature detection
- **fisheye**: Fisheye cameras with dewarping capabilities
- **multi_sensor**: Multi-sensor cameras with multiple image sensors
- **doorbell**: Doorbell cameras with button detection and two-way audio

Example:

```yaml
cameras:
  front_gate:
    type: lpr
    # LPR-specific configuration
```

### PTZ Camera Configuration

PTZ (Pan-Tilt-Zoom) cameras provide movement capabilities for dynamic monitoring:

```yaml
cameras:
  ptz_camera:
    type: ptz
    ptz:
      enabled: true
      protocol: onvif
      default_speed: 0.5
      presets:
        home:
          name: Home
          position:
            pan: 0.0
            tilt: 0.0
            zoom: 1.0
          home: true
        entrance:
          name: Entrance
          position:
            pan: 45.0
            tilt: -10.0
            zoom: 2.0
      patrols:
        perimeter:
          name: Perimeter Patrol
          presets:
            - home
            - entrance
            - back
            - side
          dwell_time: 10
          speed: 0.8
      autotracking:
        enabled: true
        tracking_objects:
          - person
        tracking_timeout: 30
```

### Thermal Camera Configuration

Thermal cameras detect heat signatures and can measure temperatures:

```yaml
cameras:
  thermal_camera:
    type: thermal
    thermal:
      enabled: true
      unit: celsius
      min_temp: 0.0
      max_temp: 100.0
      palette: iron
      show_temp: true
      show_hotspot: true
      alarms:
        high_temp:
          enabled: true
          threshold_high: 38.0
          duration: 5
          zones:
            - entrance
```

### Fisheye Camera Configuration

Fisheye cameras provide wide-angle views that can be dewarped:

```yaml
cameras:
  fisheye_camera:
    type: fisheye
    fisheye:
      enabled: true
      dewarper:
        enabled: true
        method: opencv
        center: [0.5, 0.5]
        radius: 1.0
        fov: 180.0
      panorama: true
      panorama_width: 1920
      panorama_height: 480
      views:
        north:
          name: North View
          pan: 0.0
          tilt: 0.0
          zoom: 1.0
        east:
          name: East View
          pan: 90.0
          tilt: 0.0
          zoom: 1.0
```

### Multi-Sensor Camera Configuration

Multi-sensor cameras have multiple image sensors in a single housing:

```yaml
cameras:
  multi_sensor_camera:
    type: multi_sensor
    multi_sensor:
      enabled: true
      sensors:
        front:
          name: Front Sensor
          stream_url: rtsp://username:password@camera-ip:554/stream1
          position: front
        left:
          name: Left Sensor
          stream_url: rtsp://username:password@camera-ip:554/stream2
          position: left
        right:
          name: Right Sensor
          stream_url: rtsp://username:password@camera-ip:554/stream3
          position: right
      groups:
        perimeter:
          name: Perimeter Group
          sensors:
            - front
            - left
            - right
          stitching: true
          stitching_width: 2560
          stitching_height: 720
```

### Doorbell Camera Configuration

Doorbell cameras include button detection and two-way audio:

```yaml
cameras:
  doorbell_camera:
    type: doorbell
    doorbell:
      enabled: true
      button_enabled: true
      button_detection_method: api
      audio_enabled: true
      two_way_audio: true
      events:
        button_press:
          name: Button Press
          trigger_type: button
          notify: true
          notification_title: Doorbell
          notification_message: Someone is at the door
        person_detected:
          name: Person Detected
          trigger_type: object
          trigger_objects:
            - person
          notify: true
      responses:
        welcome:
          name: Welcome Message
          trigger_events:
            - button_press
          audio_text: Hello, I'll be right there
```

## FFmpeg Configuration

The FFmpeg configuration controls how video streams are processed:

```yaml
ffmpeg:
  inputs:
    - path: rtsp://username:password@camera-ip:554/stream
      roles:
        - detect
        - record
      input_args: -rtsp_transport tcp
  output_args:
    record: -f segment -segment_time 10 -segment_format mp4 -reset_timestamps 1 -strftime 1 -c copy
  hwaccel_args: -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi
```

### Input Roles

Each input can have one or more roles:

- **detect**: Used for object detection
- **record**: Used for recording
- **rtmp**: Used for RTMP streaming
- **audio**: Used for audio processing
- **snapshots**: Used for snapshots

## Detection Configuration

The detection configuration controls object detection parameters:

```yaml
detect:
  enabled: true
  width: 1280
  height: 720
  fps: 5
  model_purposes:
    - general
    - person
  model_merge_strategy: highest_confidence
```

### Advanced Detection Options

```yaml
detect:
  # Object tracking parameters
  max_disappeared: 25
  min_initialized: 3
  stationary:
    threshold: 50
    interval: 50
  
  # Region of interest
  roi_strategy: motion
  crop_regions:
    - x: 0
      y: 0
      width: 640
      height: 360
  
  # Hardware acceleration
  acceleration:
    device: gpu
    precision: fp16
```

## Motion Detection Configuration

The motion detection configuration controls how motion is detected:

```yaml
motion:
  enabled: true
  threshold: 25
  contour_area: 30
  delta_alpha: 0.2
  frame_alpha: 0.2
  mask: "0,0,320,0,320,240,0,240"
  improve_contrast: true
```

### Advanced Motion Detection Options

```yaml
motion:
  # Adaptive motion detection
  adaptive: true
  adaptive_steps: 3
  adaptive_learning_rate: 0.01
  
  # Filtering
  temporal_filter: true
  temporal_filter_size: 3
  spatial_filter: true
  spatial_filter_size: 3
```

## Object Configuration

The object configuration controls which objects are tracked and how they are filtered:

```yaml
objects:
  track:
    - person
    - car
    - dog
  filters:
    person:
      min_area: 5000
      max_area: 100000
      min_score: 0.5
    car:
      min_score: 0.6
      min_ratio: 0.5
      max_ratio: 2.0
```

### Advanced Object Configuration

```yaml
objects:
  # Object tracking options
  tracking_mode: norfair
  tracking_config:
    distance_threshold: 30
    hit_counter_max: 15
    initialization_delay: 3
  
  # Classification
  classification:
    enabled: true
    model: resnet50
    threshold: 0.7
```

## Recording Configuration

The recording configuration controls how video is recorded:

```yaml
record:
  enabled: true
  retain:
    days: 7
    mode: motion
  segments:
    time: 10
    format: mp4
  events:
    pre_capture: 5
    post_capture: 5
    objects:
      - person
      - car
```

### Advanced Recording Configuration

```yaml
record:
  # Tiered storage
  tiered_storage:
    enabled: true
    hot_storage:
      path: /media/ssd
      max_days: 3
    cold_storage:
      path: /media/hdd
      max_days: 30
  
  # Compression
  compression:
    enabled: true
    codec: h265
    crf: 23
```

## Snapshots Configuration

The snapshots configuration controls how snapshots are captured and stored:

```yaml
snapshots:
  enabled: true
  clean_copy: true
  timestamp: true
  bounding_box: true
  quality: 80
  format: jpg
```

### Advanced Snapshots Configuration

```yaml
snapshots:
  # Enhancement
  enhance: true
  enhance_method: clahe
  enhance_params:
    clip_limit: 2.0
    tile_grid_size: [8, 8]
  
  # Storage
  storage:
    path: /media/snapshots
    structure: "{camera}/{year}/{month}/{day}"
```

## Timestamp Configuration

The timestamp configuration controls how timestamps are displayed:

```yaml
timestamp_style:
  format: "%m/%d/%Y %H:%M:%S"
  position: tl
  font_size: 0.5
  font_thickness: 1
  color: [255, 255, 255]
  background: [0, 0, 0]
```

## Notification Configuration

The notification configuration controls how notifications are sent:

```yaml
notifications:
  enabled: true
  triggers:
    - object_detected
    - motion_detected
  required_objects:
    - person
    - car
  cooldown: 60
  include_snapshot: true
```

### Advanced Notification Configuration

```yaml
notifications:
  # Services
  services:
    telegram:
      enabled: true
      token: "your-telegram-token"
      chat_id: "your-chat-id"
    pushover:
      enabled: true
      user_key: "your-user-key"
      app_token: "your-app-token"
  
  # Scheduling
  scheduling:
    enabled: true
    schedule:
      - days: [1, 2, 3, 4, 5]
        time_ranges:
          - start: "08:00"
            end: "18:00"
```

## Review Configuration

The review configuration controls how events are reviewed:

```yaml
review:
  alerts:
    enabled: true
    required_objects:
      - person
    required_zones:
      - driveway
  detections:
    enabled: true
    min_score: 0.6
```

## Birdseye Configuration

The birdseye configuration controls the birdseye view:

```yaml
birdseye:
  enabled: true
  width: 1280
  height: 720
  quality: 70
  mode: objects
  label: true
  timestamp: true
```

## Audio Configuration

The audio configuration controls audio processing:

```yaml
audio:
  enabled: true
  sample_rate: 16000
  channels: 1
  threshold: 0.5
  min_duration: 1.0
  max_duration: 30.0
```

## Generative AI Configuration

The generative AI configuration controls AI-powered features:

```yaml
genai:
  enabled: true
  model: gpt-4
  event_description: true
  event_description_prompt: "Describe what is happening in this scene."
```

## Zones Configuration

Zones allow you to define specific areas of interest in your camera view:

```yaml
zones:
  driveway:
    coordinates: "0,0,320,0,320,240,0,240"
    objects:
      - person
      - car
    inertia: 3
  porch:
    coordinates: "320,0,640,0,640,240,320,240"
    objects:
      - person
    inertia: 5
```

## ONVIF Configuration

The ONVIF configuration controls PTZ and other ONVIF features:

```yaml
onvif:
  host: 192.168.1.100
  port: 80
  username: admin
  password: password
  autotracking:
    enabled: true
    required_zones:
      - driveway
    zoom_factor: 1.5
    track_timeout: 10
```

## Global vs. Camera-Specific Configuration

Many configuration options can be set globally and then overridden at the camera level:

```yaml
# Global configuration
detect:
  fps: 5

# Camera-specific configuration
cameras:
  front_door:
    detect:
      fps: 10  # Overrides the global setting
```

## Configuration Validation

Arkos AI validates all configuration values to ensure they are correct:

- **Type checking**: Ensures values are of the correct type
- **Range checking**: Ensures values are within valid ranges
- **Enum checking**: Ensures values are one of a set of valid options
- **Dependency checking**: Ensures dependent configuration options are set correctly

## Best Practices

- **Start simple**: Begin with a basic configuration and add more options as needed
- **Test changes**: Test configuration changes to ensure they work as expected
- **Monitor performance**: Monitor system performance after making configuration changes
- **Use comments**: Add comments to your configuration file to document your choices
- **Back up configuration**: Back up your configuration file before making changes

## Troubleshooting

If you encounter issues with your camera configuration:

1. Check the logs for error messages
2. Verify that your camera is accessible
3. Ensure that your configuration values are valid
4. Try simplifying your configuration to isolate the issue
5. Check the Arkos AI documentation for more information
