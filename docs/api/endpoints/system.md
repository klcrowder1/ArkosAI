# System API Endpoints

This document describes the API endpoints for managing the Arkos AI system.

## Overview

The System API provides endpoints for managing the system, including getting system information, statistics, configuration, logs, and performing system operations.

## Base URL

All system endpoints are available under the base URL:

```
/api/v1/system
```

## Authentication

All system endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### Get System Information

```http
GET /api/v1/system/info
```

Returns information about the system.

#### Response

```json
{
  "version": "1.0.0",
  "hostname": "arkos-server",
  "platform": "Linux",
  "architecture": "x86_64",
  "cpu_count": 8,
  "memory_total": 16000000000,
  "gpu_info": {
    "name": "NVIDIA GeForce RTX 3080",
    "memory": 10000000000,
    "driver_version": "460.91.03"
  },
  "uptime": 3600.0,
  "python_version": "3.9.5",
  "ffmpeg_version": "4.4",
  "opencv_version": "4.5.2",
  "timezone": "UTC"
}
```

### Get System Statistics

```http
GET /api/v1/system/stats
```

Returns current system statistics.

#### Response

```json
{
  "cpu_usage": 10.0,
  "memory_usage": 20.0,
  "disk_usage": 30.0,
  "gpu_usage": 5.0,
  "network_rx": 1000000.0,
  "network_tx": 500000.0,
  "temperature": 40.0,
  "process_count": 100,
  "load_average": [0.5, 0.7, 0.9]
}
```

### Get System Configuration

```http
GET /api/v1/system/config
```

Returns the current system configuration.

#### Response

```json
{
  "config_path": "/config/config.yml",
  "config_version": "1.0.0",
  "last_modified": 1620000000.0,
  "cameras": ["front_door", "back_door"],
  "detectors": ["cpu", "gpu"],
  "storage_paths": ["/recordings", "/cache"],
  "auth_enabled": true,
  "mqtt_enabled": true,
  "webhook_enabled": true,
  "debug_mode": false
}
```

### Update System Configuration

```http
PUT /api/v1/system/config
```

Updates the system configuration.

#### Request Body

```json
{
  "config": {
    "cameras": {
      "front_door": {
        "enabled": true,
        "url": "rtsp://example.com/front_door"
      }
    },
    "detectors": {
      "cpu": {
        "enabled": true,
        "model_path": "/models/cpu_model.tflite"
      }
    }
  },
  "restart": true
}
```

#### Response

```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

### Restart System

```http
POST /api/v1/system/restart
```

Restarts the Arkos AI system.

#### Response

```json
{
  "success": true,
  "message": "System restart initiated"
}
```

### Get System Logs

```http
GET /api/v1/system/logs
```

Returns system logs.

#### Query Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `level` | string | null | Filter by log level |
| `source` | string | null | Filter by log source |
| `after` | number | null | Filter by timestamp after |
| `before` | number | null | Filter by timestamp before |
| `search` | string | null | Search term |
| `limit` | integer | 100 | Maximum number of log entries to return |
| `offset` | integer | 0 | Number of log entries to skip |

#### Response

```json
[
  {
    "timestamp": 1620000000.0,
    "level": "INFO",
    "source": "system",
    "message": "System started",
    "details": null
  },
  {
    "timestamp": 1620000001.0,
    "level": "INFO",
    "source": "camera",
    "message": "Camera connected",
    "details": {
      "camera": "camera1"
    }
  },
  {
    "timestamp": 1620000002.0,
    "level": "WARNING",
    "source": "detector",
    "message": "Detector performance degraded",
    "details": {
      "detector": "cpu",
      "fps": 5.0
    }
  }
]
```

### Get Version

```http
GET /api/v1/system/version
```

Returns the Arkos AI version.

#### Response

```json
{
  "version": "1.0.0"
}
```

## Log Levels

The system logs use the following log levels:

- `DEBUG`: Detailed information, typically of interest only when diagnosing problems
- `INFO`: Confirmation that things are working as expected
- `WARNING`: An indication that something unexpected happened, or may happen in the near future
- `ERROR`: Due to a more serious problem, the software has not been able to perform some function
- `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/system/info` | `read` |
| `GET /api/v1/system/stats` | `read` |
| `GET /api/v1/system/config` | `read` |
| `PUT /api/v1/system/config` | `admin` |
| `POST /api/v1/system/restart` | `admin` |
| `GET /api/v1/system/logs` | `read` |
| `GET /api/v1/system/version` | None |

See the [Authentication](../authentication.md) documentation for details on permissions.
