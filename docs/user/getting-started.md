# Getting Started with Arkos AI

This guide provides instructions for installing, configuring, and using Arkos AI on the LattePanda Sigma hardware platform.

## Overview

Arkos AI is an advanced Network Video Recorder (NVR) system with AI-powered analytics capabilities. It is designed to run on the LattePanda Sigma hardware platform and provides comprehensive security, monitoring, and analytics features.

## Hardware Requirements

### Recommended Hardware

- **LattePanda Sigma**:
  - Intel Core i5/i7 processor
  - 16GB RAM
  - 256GB or larger M.2 SSD
  - Intel Iris Xe Graphics

### Storage Requirements

- **Primary Storage**: M.2 SSD for operating system and application
- **Secondary Storage**: External USB drive or NAS for video recordings
  - Recommended: 1TB or larger, depending on retention requirements
  - USB 3.0 or faster connection for external drives
  - Gigabit Ethernet or faster for NAS

### Camera Requirements

- **Supported Camera Types**:
  - IP cameras with RTSP, ONVIF, or HTTP streams
  - USB cameras (limited functionality)
  
- **Recommended Camera Specifications**:
  - Resolution: 1080p or higher
  - Frame Rate: 15 FPS or higher
  - Codec: H.264 or H.265
  - Audio: Optional, supported if available

### Network Requirements

- **Wired Network**: Gigabit Ethernet recommended
- **Wireless Network**: Wi-Fi 6 recommended for wireless cameras
- **Bandwidth**: 5-10 Mbps per 1080p camera (varies based on configuration)

## Installation

### Operating System Installation

1. **Download Ubuntu Server**:
   - Download Ubuntu Server 22.04 LTS from [ubuntu.com](https://ubuntu.com/download/server)
   - Create a bootable USB drive using [Rufus](https://rufus.ie/) (Windows) or [Etcher](https://www.balena.io/etcher/) (macOS/Linux)

2. **Install Ubuntu Server**:
   - Connect the LattePanda Sigma to a monitor, keyboard, and mouse
   - Insert the bootable USB drive
   - Power on the LattePanda and boot from the USB drive
   - Follow the Ubuntu Server installation instructions
   - Select the M.2 SSD as the installation target
   - Install the OpenSSH server when prompted
   - Complete the installation and reboot

3. **Initial System Configuration**:
   - Log in with the credentials created during installation
   - Update the system:
     ```bash
     sudo apt update
     sudo apt upgrade -y
     ```
   - Install required packages:
     ```bash
     sudo apt install -y curl git docker.io docker-compose
     ```
   - Add your user to the docker group:
     ```bash
     sudo usermod -aG docker $USER
     ```
   - Log out and log back in for the group change to take effect

### Arkos AI Installation

1. **Download Arkos AI**:
   ```bash
   git clone https://github.com/your-organization/arkos-ai.git
   cd arkos-ai
   ```

2. **Configure Installation**:
   ```bash
   cp config/config.yml.example config/config.yml
   nano config/config.yml
   ```
   
   Edit the configuration file to match your environment (see Configuration section below).

3. **Start Arkos AI**:
   ```bash
   docker-compose up -d
   ```

4. **Verify Installation**:
   - Open a web browser and navigate to `http://<lattepanda-ip>:5000`
   - Log in with the default credentials:
     - Username: `admin`
     - Password: `admin`
   - Change the default password immediately

## Configuration

### Basic Configuration

The main configuration file is located at `config/config.yml`. Here's a basic configuration example:

```yaml
# Global configuration
mqtt:
  host: localhost
  port: 1883

# Camera configuration
cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.1.100:554/stream
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
    record:
      enabled: true
      retain:
        days: 7
        mode: motion
    objects:
      track:
        - person
        - car
        - package

# Storage configuration
storage:
  path: /media/recordings
  max_usage_percent: 90
```

### Camera Configuration

To add a camera:

1. Determine the camera's RTSP URL:
   - Consult your camera's documentation
   - Common formats:
     - Hikvision: `rtsp://username:password@camera-ip:554/Streaming/Channels/101`
     - Dahua: `rtsp://username:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0`
     - Generic ONVIF: `rtsp://username:password@camera-ip:554/onvif1`

2. Add the camera to the configuration file:
   ```yaml
   cameras:
     camera_name:
       ffmpeg:
         inputs:
           - path: rtsp://username:password@camera-ip:554/stream
             roles:
               - detect
               - record
       detect:
         width: 1280
         height: 720
         fps: 5
       record:
         enabled: true
         retain:
           days: 7
           mode: motion
       objects:
         track:
           - person
           - car
           - package
   ```

3. Restart Arkos AI:
   ```bash
   docker-compose restart
   ```

### Storage Configuration

To configure storage:

1. Connect an external drive or configure NAS access:
   ```bash
   # For external USB drive
   sudo mkdir -p /media/recordings
   sudo mount /dev/sdX1 /media/recordings
   sudo chown -R $USER:$USER /media/recordings
   
   # For NAS (example for NFS)
   sudo apt install -y nfs-common
   sudo mkdir -p /media/recordings
   sudo mount -t nfs nas-server:/share /media/recordings
   sudo chown -R $USER:$USER /media/recordings
   ```

2. Update the storage configuration:
   ```yaml
   storage:
     path: /media/recordings
     max_usage_percent: 90
   ```

3. For automatic mounting at boot:
   ```bash
   # For external USB drive (get UUID first)
   sudo blkid
   # Add to /etc/fstab
   echo "UUID=<drive-uuid> /media/recordings ext4 defaults 0 2" | sudo tee -a /etc/fstab
   
   # For NAS (NFS example)
   echo "nas-server:/share /media/recordings nfs defaults 0 0" | sudo tee -a /etc/fstab
   ```

### Object Detection Configuration

To configure object detection:

1. Configure detection objects:
   ```yaml
   objects:
     track:
       - person
       - car
       - bicycle
       - motorcycle
       - bus
       - truck
       - animal
       - package
   ```

2. Configure detection zones:
   ```yaml
   cameras:
     front_door:
       zones:
         driveway:
           coordinates: [[0, 0], [1280, 0], [1280, 720], [0, 720]]
           objects:
             - person
             - car
         porch:
           coordinates: [[500, 400], [800, 400], [800, 720], [500, 720]]
           objects:
             - person
             - package
   ```

3. Configure detection sensitivity:
   ```yaml
   cameras:
     front_door:
       detect:
         width: 1280
         height: 720
         fps: 5
         threshold: 0.7  # Confidence threshold (0.0-1.0)
   ```

### Enhanced Analytics Configuration

To configure enhanced analytics:

1. Configure activity recognition:
   ```yaml
   analytics:
     activity:
       enabled: true
       types:
         - walking
         - running
         - loitering
   ```

2. Configure audio analytics:
   ```yaml
   audio:
     enabled: true
     detectors:
       - name: "Glass Break Detector"
         type: "frequency_pattern"
         frequency_range: [4000, 10000]
         pattern: "sudden_peak"
         threshold: 75
         min_duration: 0.2
   ```

3. Configure custom detection models:
   ```yaml
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
   ```

### IO Configuration

To configure IO integration:

1. Configure GPIO:
   ```yaml
   io:
     gpio:
       enabled: true
       inputs:
         - pin: 17
           name: "motion_sensor"
           type: "digital"
           pull: "up"
           invert: true
       outputs:
         - pin: 18
           name: "alarm_siren"
           type: "digital"
           initial_state: "off"
   ```

2. Configure triggers:
   ```yaml
   triggers:
     - name: "Front Door Alert"
       event:
         type: "detection"
         source: "front_door"
         object: ["person"]
         zone: "porch"
       actions:
         - output: "alarm_siren"
           state: "on"
           duration: 60
   ```

3. Configure schedules:
   ```yaml
   schedules:
     - name: "Night Lights"
       type: "time"
       time: "19:00:00"
       days: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
       actions:
         - output: "perimeter_lights"
           state: "on"
   ```

## Basic Usage

### Accessing the Web Interface

1. Open a web browser and navigate to `http://<lattepanda-ip>:5000`
2. Log in with your credentials
3. The web interface provides access to all Arkos AI features

### Live View

1. Click on the "Live" tab in the navigation menu
2. Select cameras to view from the camera list
3. Use the controls to:
   - Take snapshots
   - Start/stop recording
   - Toggle audio
   - View in fullscreen

### Event Review

1. Click on the "Events" tab in the navigation menu
2. Use the filters to find specific events:
   - Camera
   - Object type
   - Time range
   - Zone
3. Click on an event to view details:
   - Event clip
   - Event snapshot
   - Event metadata
4. Use the controls to:
   - Export clips
   - Delete events
   - Mark as false positive

### Timeline View

1. Click on the "Timeline" tab in the navigation menu
2. Select cameras to include in the timeline
3. Use the timeline controls to:
   - Navigate through time
   - Zoom in/out
   - Play/pause
   - Jump to specific times
4. Click on timeline events to view details

### Configuration

1. Click on the "Config" tab in the navigation menu
2. Use the configuration editor to modify settings
3. Click "Save" to apply changes
4. Restart services if required

## Advanced Features

### Camera Health Monitoring

1. Click on the "Health" tab in the navigation menu
2. View camera health status:
   - Connectivity
   - Video quality
   - Dirty lens detection
   - Scene change detection
3. Configure health monitoring settings:
   - Alert thresholds
   - Notification settings
   - Automatic recovery options

### IO Control

1. Click on the "IO" tab in the navigation menu
2. View IO status:
   - Input states
   - Output states
3. Control outputs manually:
   - Turn outputs on/off
   - Set output duration
4. Configure IO settings:
   - Triggers
   - Schedules
   - MQTT integration

### Analytics Dashboard

1. Click on the "Analytics" tab in the navigation menu
2. View analytics data:
   - Object detection statistics
   - Activity recognition statistics
   - Audio event statistics
3. Use filters to analyze specific data:
   - Camera
   - Time range
   - Object type
   - Activity type
4. Export analytics data for further analysis

### Custom Detection Models

1. Click on the "Models" tab in the navigation menu
2. View available detection models
3. Upload custom models:
   - YOLO models
   - TensorFlow models
   - ONNX models
4. Configure model settings:
   - Confidence threshold
   - Class mapping
   - Camera assignment

## Troubleshooting

### Camera Connection Issues

1. **Problem**: Camera not connecting
   - **Solution**:
     - Verify camera is powered on and connected to the network
     - Check camera IP address and credentials
     - Verify RTSP URL format
     - Check network connectivity with `ping <camera-ip>`
     - Try accessing the camera directly with VLC or similar tool

2. **Problem**: Poor video quality
   - **Solution**:
     - Check camera resolution and bitrate settings
     - Verify network bandwidth is sufficient
     - Reduce camera resolution or frame rate if necessary
     - Check for network congestion

### System Performance Issues

1. **Problem**: High CPU usage
   - **Solution**:
     - Reduce number of cameras or camera resolution
     - Lower detection frame rate
     - Disable unnecessary features
     - Check for other processes consuming CPU

2. **Problem**: High memory usage
   - **Solution**:
     - Reduce number of cameras
     - Lower buffer sizes
     - Restart services to clear memory
     - Check for memory leaks with `docker stats`

3. **Problem**: Storage filling up quickly
   - **Solution**:
     - Adjust retention settings
     - Use motion-based recording instead of continuous
     - Add more storage
     - Check for large files with `du -h --max-depth=1 /media/recordings`

### Detection Issues

1. **Problem**: False positives
   - **Solution**:
     - Increase detection threshold
     - Configure detection zones
     - Adjust motion detection sensitivity
     - Use better lighting conditions

2. **Problem**: Missed detections
   - **Solution**:
     - Decrease detection threshold
     - Improve camera positioning
     - Improve lighting conditions
     - Use higher resolution for detection

### System Access Issues

1. **Problem**: Cannot access web interface
   - **Solution**:
     - Check if services are running with `docker-compose ps`
     - Verify network connectivity
     - Check firewall settings
     - Restart services with `docker-compose restart`

2. **Problem**: Authentication issues
   - **Solution**:
     - Reset password using command line
     - Check user permissions
     - Verify correct username and password
     - Check for keyboard layout issues

## Maintenance

### Regular Maintenance Tasks

1. **Backup Configuration**:
   ```bash
   cp config/config.yml config/config.yml.backup
   ```

2. **Update Arkos AI**:
   ```bash
   cd arkos-ai
   git pull
   docker-compose down
   docker-compose up -d
   ```

3. **Check System Logs**:
   ```bash
   docker-compose logs
   ```

4. **Check Storage Usage**:
   ```bash
   df -h /media/recordings
   ```

5. **Clean Docker Resources**:
   ```bash
   docker system prune -f
   ```

### Database Maintenance

1. **Backup Database**:
   ```bash
   cp data/db/arkos.db data/db/arkos.db.backup
   ```

2. **Optimize Database**:
   ```bash
   docker-compose exec arkos-db sqlite3 /data/arkos.db 'VACUUM;'
   ```

3. **Check Database Integrity**:
   ```bash
   docker-compose exec arkos-db sqlite3 /data/arkos.db 'PRAGMA integrity_check;'
   ```

### Camera Maintenance

1. **Clean Camera Lenses**:
   - Use a microfiber cloth
   - Clean gently to avoid scratches
   - Check for dirt or obstructions

2. **Check Camera Positioning**:
   - Verify cameras are properly aimed
   - Adjust for seasonal changes (e.g., vegetation growth)
   - Check for obstructions

3. **Update Camera Firmware**:
   - Check manufacturer's website for updates
   - Follow firmware update procedures
   - Document firmware versions

## Additional Resources

### Documentation

- [Arkos AI Documentation](https://docs.arkos.ai/)
- [API Documentation](https://docs.arkos.ai/api/)
- [Configuration Reference](https://docs.arkos.ai/config/)

### Community

- [Arkos AI Forum](https://forum.arkos.ai/)
- [GitHub Repository](https://github.com/your-organization/arkos-ai)
- [Discord Community](https://discord.gg/arkos-ai)

### Support

- [Support Email](mailto:support@arkos.ai)
- [Issue Tracker](https://github.com/your-organization/arkos-ai/issues)
- [FAQ](https://docs.arkos.ai/faq/)

## Conclusion

This guide provides the basics for getting started with Arkos AI. For more detailed information, refer to the full documentation and additional resources. Arkos AI is a powerful and flexible NVR system that can be customized to meet your specific needs.
