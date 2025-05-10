# Getting Started with Arkos AI

Arkos AI is an advanced, customizable Network Video Recorder (NVR) system designed to provide comprehensive security, monitoring, and analytics capabilities. This guide will help you get started with Arkos AI.

## Prerequisites

Before installing Arkos AI, ensure you have the following:

- A compatible hardware platform (recommended: LattePanda Sigma)
- Docker and Docker Compose installed
- At least one IP camera with RTSP stream capability
- Storage space for recordings

## Installation

### Using Docker Compose

The easiest way to get started with Arkos AI is to use Docker Compose:

```yaml
version: '3'
services:
  arkos:
    container_name: arkos
    image: ghcr.io/arkosai/arkos:latest
    restart: unless-stopped
    privileged: true
    volumes:
      - /dev/bus/usb:/dev/bus/usb
      - /dev/dri:/dev/dri
      - /path/to/config:/config
      - /path/to/storage:/media/arkos
    ports:
      - "5000:5000"
      - "1935:1935"
      - "8554:8554"
```

Replace `/path/to/config` and `/path/to/storage` with your desired paths for configuration and storage.

### Configuration

After starting Arkos AI for the first time, a default configuration file will be created at `/path/to/config/config.yml`. You'll need to edit this file to add your cameras and customize settings.

Here's a basic configuration example:

```yaml
mqtt:
  enabled: False

cameras:
  front_door:
    enabled: True
    ffmpeg:
      inputs:
        - path: rtsp://username:password@camera-ip:554/stream
          roles:
            - detect
            - record
    detect:
      enabled: True
      width: 1280
      height: 720
```

## Accessing the Web Interface

Once Arkos AI is running, you can access the web interface by navigating to `http://your-server-ip:5000` in your web browser.

## Next Steps

- [Configure Object Detection](features/object-detection.md)
- [Set Up Recording](features/recording.md)
- [Configure Notifications](features/notifications.md)
- [Explore Hardware Acceleration](advanced/hardware-acceleration.md)
