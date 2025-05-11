# Camera Connection Management in Arkos AI

Arkos AI provides robust camera connection management capabilities, allowing you to monitor and manage the connection status of your cameras.

## Overview

The camera connection management system in Arkos AI is designed to:

- **Monitor** camera connections in real-time
- **Detect** connection issues and provide detailed error information
- **Automatically reconnect** to cameras when connections are lost
- **Provide API endpoints** for monitoring and managing camera connections

## Connection Status

Each camera can have one of the following connection statuses:

- **Connected**: The camera is connected and streaming video
- **Connecting**: The system is attempting to connect to the camera
- **Disconnected**: The camera is not connected
- **Error**: There was an error connecting to the camera
- **Disabled**: The camera is disabled in the configuration

## Connection Errors

When a camera has a connection error, the system provides detailed information about the error:

- **Network**: The camera is not reachable on the network
- **Authentication**: Authentication failed (incorrect username or password)
- **Timeout**: The connection timed out
- **FFMPEG**: There was an error with the FFMPEG process
- **Unknown**: An unknown error occurred

## Automatic Reconnection

Arkos AI automatically attempts to reconnect to cameras when connections are lost. The system uses an exponential backoff strategy to avoid overwhelming the camera with connection attempts.

The reconnection behavior can be configured in the camera configuration:

```yaml
cameras:
  front_door:
    ffmpeg:
      retry_interval: 30  # Seconds between reconnection attempts
```

## API Endpoints

Arkos AI provides API endpoints for monitoring and managing camera connections:

### Get Connection Status for All Cameras

```
GET /api/cameras/connection/status
```

Response:

```json
{
  "cameras": {
    "front_door": {
      "status": "connected",
      "error": "none",
      "reconnect_count": 0,
      "uptime": 3600,
      "last_connect_attempt": 1620000000
    },
    "back_yard": {
      "status": "error",
      "error": "network",
      "reconnect_count": 5,
      "uptime": 0,
      "last_connect_attempt": 1620000300
    }
  }
}
```

### Get Connection Status for a Specific Camera

```
GET /api/cameras/connection/{camera_name}/status
```

Response:

```json
{
  "status": "connected",
  "error": "none",
  "reconnect_count": 0,
  "uptime": 3600,
  "last_connect_attempt": 1620000000
}
```

### Reset Connection for a Specific Camera

```
POST /api/cameras/connection/{camera_name}/reset
```

Response:

```json
{
  "status": "connecting",
  "error": "none",
  "reconnect_count": 1,
  "uptime": 0,
  "last_connect_attempt": 1620000600
}
```

## Web Interface

The Arkos AI web interface provides a visual representation of camera connection status:

- **Green**: Connected
- **Yellow**: Connecting
- **Red**: Error
- **Gray**: Disabled or Disconnected

The interface also provides detailed information about connection errors and allows you to reset connections with a single click.

## Camera Type-Specific Connection Management

Arkos AI provides specialized connection management for different camera types:

### PTZ Cameras

PTZ cameras have additional connection requirements:

- **ONVIF Connection**: PTZ cameras often use ONVIF for control
- **Movement Control**: Verify that movement commands are being received
- **Preset Positions**: Test preset positions to ensure they work correctly

### Thermal Cameras

Thermal cameras may have specific connection requirements:

- **Temperature Data**: Verify that temperature data is being received
- **Calibration**: Some thermal cameras require calibration after connection
- **Special Protocols**: Some thermal cameras use proprietary protocols

### Fisheye Cameras

Fisheye cameras have unique connection considerations:

- **Dewarping Parameters**: Verify that dewarping parameters are correct
- **View Configuration**: Test different views to ensure they are properly configured
- **Panorama Mode**: If using panorama mode, verify that it's working correctly

### Multi-Sensor Cameras

Multi-sensor cameras require special handling:

- **Multiple Streams**: Verify that all sensor streams are accessible
- **Synchronization**: Check that sensors are properly synchronized
- **Stitching**: If using image stitching, verify that it's working correctly

### Doorbell Cameras

Doorbell cameras have additional connection requirements:

- **Button Detection**: Verify that button presses are being detected
- **Two-Way Audio**: Test two-way audio functionality
- **Integration**: Check integration with notification systems

## Troubleshooting

If you're experiencing connection issues with your cameras:

1. **Check the camera's network connectivity**:
   - Ensure the camera is powered on and connected to the network
   - Verify that the camera's IP address is correct in the configuration
   - Check if you can ping the camera from the Arkos AI system

2. **Verify authentication credentials**:
   - Ensure the username and password are correct
   - Try accessing the camera directly using the same credentials

3. **Check RTSP/HTTP settings**:
   - Verify that the camera's RTSP or HTTP stream is properly configured
   - Try accessing the stream directly using a media player like VLC

4. **Inspect logs**:
   - Check the Arkos AI logs for detailed error messages
   - Look for FFMPEG errors that might indicate stream format issues

5. **Reset the connection**:
   - Use the API or web interface to reset the connection
   - Monitor the logs during the reconnection attempt

6. **Camera-specific troubleshooting**:
   - For PTZ cameras, check ONVIF connectivity and movement control
   - For thermal cameras, verify temperature data and calibration
   - For fisheye cameras, check dewarping parameters and view configuration
   - For multi-sensor cameras, verify all sensor streams and synchronization
   - For doorbell cameras, test button detection and two-way audio

## Best Practices

- **Use static IP addresses** for your cameras to avoid connection issues due to changing IP addresses
- **Configure appropriate retry intervals** based on your network reliability
- **Monitor connection status** regularly to identify potential issues
- **Use wired connections** when possible for more reliable connectivity
- **Ensure sufficient bandwidth** is available for all camera streams
