# Camera API Endpoints

This document describes the API endpoints for managing cameras in Arkos AI.

## Overview

The Camera API provides endpoints for managing cameras, including listing cameras, getting camera details, creating and updating cameras, and managing camera connections.

## Base URL

All camera endpoints are available under the base URL:

```
/api/v1/cameras
```

## Authentication

All camera endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### List Cameras

```http
GET /api/v1/cameras
```

Returns a list of all cameras.

#### Query Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `limit` | integer | 100 | Maximum number of cameras to return |
| `offset` | integer | 0 | Number of cameras to skip |

#### Response

```json
{
  "items": [
    {
      "id": "front_door",
      "name": "front_door",
      "enabled": true,
      "url": "rtsp://example.com/front_door",
      "type": "rtsp",
      "width": 1280,
      "height": 720,
      "fps": 5,
      "rtsp_url": "rtsp://example.com/front_door",
      "ptz_enabled": false,
      "audio_enabled": false,
      "detect_enabled": true,
      "motion_enabled": true,
      "recording_enabled": true,
      "snapshot_enabled": true,
      "zones": {
        "yard": {
          "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
        }
      },
      "objects": ["person", "car"]
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 100,
    "offset": 0,
    "next": null
  }
}
```

### Get Camera

```http
GET /api/v1/cameras/{camera_id}
```

Returns details for a specific camera.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_id` | string | Camera ID |

#### Response

```json
{
  "id": "front_door",
  "name": "front_door",
  "enabled": true,
  "url": "rtsp://example.com/front_door",
  "type": "rtsp",
  "width": 1280,
  "height": 720,
  "fps": 5,
  "rtsp_url": "rtsp://example.com/front_door",
  "ptz_enabled": false,
  "audio_enabled": false,
  "detect_enabled": true,
  "motion_enabled": true,
  "recording_enabled": true,
  "snapshot_enabled": true,
  "zones": {
    "yard": {
      "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },
  "objects": ["person", "car"]
}
```

### Create Camera

```http
POST /api/v1/cameras
```

Creates a new camera.

#### Request Body

```json
{
  "name": "front_door",
  "url": "rtsp://example.com/front_door",
  "type": "rtsp",
  "width": 1280,
  "height": 720,
  "fps": 5,
  "rtsp_url": "rtsp://example.com/front_door",
  "ptz_enabled": false,
  "audio_enabled": false,
  "detect_enabled": true,
  "motion_enabled": true,
  "recording_enabled": true,
  "snapshot_enabled": true,
  "zones": {
    "yard": {
      "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },
  "objects": ["person", "car"]
}
```

#### Response

```json
{
  "id": "front_door",
  "name": "front_door",
  "enabled": true,
  "url": "rtsp://example.com/front_door",
  "type": "rtsp",
  "width": 1280,
  "height": 720,
  "fps": 5,
  "rtsp_url": "rtsp://example.com/front_door",
  "ptz_enabled": false,
  "audio_enabled": false,
  "detect_enabled": true,
  "motion_enabled": true,
  "recording_enabled": true,
  "snapshot_enabled": true,
  "zones": {
    "yard": {
      "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },
  "objects": ["person", "car"]
}
```

### Update Camera

```http
PUT /api/v1/cameras/{camera_id}
```

Updates an existing camera.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_id` | string | Camera ID |

#### Request Body

```json
{
  "name": "front_door",
  "url": "rtsp://example.com/front_door",
  "type": "rtsp",
  "width": 1280,
  "height": 720,
  "fps": 5,
  "rtsp_url": "rtsp://example.com/front_door",
  "ptz_enabled": false,
  "audio_enabled": false,
  "detect_enabled": true,
  "motion_enabled": true,
  "recording_enabled": true,
  "snapshot_enabled": true,
  "zones": {
    "yard": {
      "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },
  "objects": ["person", "car"]
}
```

#### Response

```json
{
  "id": "front_door",
  "name": "front_door",
  "enabled": true,
  "url": "rtsp://example.com/front_door",
  "type": "rtsp",
  "width": 1280,
  "height": 720,
  "fps": 5,
  "rtsp_url": "rtsp://example.com/front_door",
  "ptz_enabled": false,
  "audio_enabled": false,
  "detect_enabled": true,
  "motion_enabled": true,
  "recording_enabled": true,
  "snapshot_enabled": true,
  "zones": {
    "yard": {
      "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]]
    }
  },
  "objects": ["person", "car"]
}
```

### Delete Camera

```http
DELETE /api/v1/cameras/{camera_id}
```

Deletes an existing camera.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_id` | string | Camera ID |

#### Response

```json
{
  "success": true,
  "message": "Camera front_door deleted"
}
```

### Get Connection Status for All Cameras

```http
GET /api/v1/cameras/connection/status
```

Returns the connection status for all cameras.

#### Response

```json
{
  "cameras": {
    "front_door": {
      "status": "connected",
      "error": null,
      "reconnect_count": 0,
      "uptime": 3600.0,
      "last_connect_attempt": 1620000000.0
    },
    "back_door": {
      "status": "disconnected",
      "error": "Connection refused",
      "reconnect_count": 5,
      "uptime": 0.0,
      "last_connect_attempt": 1620000000.0
    }
  }
}
```

### Get Connection Status for a Specific Camera

```http
GET /api/v1/cameras/{camera_id}/connection/status
```

Returns the connection status for a specific camera.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_id` | string | Camera ID |

#### Response

```json
{
  "status": "connected",
  "error": null,
  "reconnect_count": 0,
  "uptime": 3600.0,
  "last_connect_attempt": 1620000000.0
}
```

### Reset Connection for a Specific Camera

```http
POST /api/v1/cameras/{camera_id}/connection/reset
```

Resets the connection for a specific camera.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_id` | string | Camera ID |

#### Response

```json
{
  "status": "connecting",
  "error": null,
  "reconnect_count": 1,
  "uptime": 0.0,
  "last_connect_attempt": 1620000000.0
}
```

## Error Responses

### Camera Not Found

```json
{
  "error": {
    "code": "camera_not_found",
    "message": "Camera front_door not found",
    "details": null
  }
}
```

### Camera Already Exists

```json
{
  "error": {
    "code": "camera_already_exists",
    "message": "Camera front_door already exists",
    "details": null
  }
}
```

### Reset Failed

```json
{
  "error": {
    "code": "reset_failed",
    "message": "Failed to reset connection for camera front_door",
    "details": null
  }
}
```

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/cameras` | `read` |
| `GET /api/v1/cameras/{camera_id}` | `read` |
| `POST /api/v1/cameras` | `admin` |
| `PUT /api/v1/cameras/{camera_id}` | `write` |
| `DELETE /api/v1/cameras/{camera_id}` | `admin` |
| `GET /api/v1/cameras/connection/status` | `read` |
| `GET /api/v1/cameras/{camera_id}/connection/status` | `read` |
| `POST /api/v1/cameras/{camera_id}/connection/reset` | `write` |

See the [Authentication](../authentication.md) documentation for details on permissions.
