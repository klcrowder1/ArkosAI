# Health API Endpoints

This document describes the API endpoints for monitoring the health of Arkos AI.

## Overview

The Health API provides endpoints for monitoring the health of the system, cameras, and storage.

## Base URL

All health endpoints are available under the base URL:

```
/api/v1/health
```

## Authentication

All health endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### Get Health Status

```http
GET /api/v1/health
```

Returns the health status of the system, cameras, and storage.

#### Response

```json
{
  "system": {
    "status": "ok",
    "cpu_usage": 10.0,
    "memory_usage": 20.0,
    "disk_usage": 30.0,
    "gpu_usage": null,
    "uptime": 3600.0,
    "temperature": 40.0,
    "version": "1.0.0"
  },
  "cameras": {
    "front_door": {
      "name": "front_door",
      "status": "ok",
      "fps": 10.0,
      "bandwidth": 2.0,
      "latency": 50.0,
      "uptime": 3600.0,
      "reconnects": 0,
      "last_frame": 1620000000.0
    },
    "back_door": {
      "name": "back_door",
      "status": "ok",
      "fps": 10.0,
      "bandwidth": 2.0,
      "latency": 50.0,
      "uptime": 3600.0,
      "reconnects": 0,
      "last_frame": 1620000000.0
    }
  },
  "storage": {
    "recordings": {
      "path": "/recordings",
      "total": 1000000000000,
      "used": 300000000000,
      "free": 700000000000,
      "usage": 30.0,
      "read_speed": 100.0,
      "write_speed": 50.0
    },
    "cache": {
      "path": "/cache",
      "total": 100000000000,
      "used": 20000000000,
      "free": 80000000000,
      "usage": 20.0,
      "read_speed": 200.0,
      "write_speed": 100.0
    }
  }
}
```

### Get System Health

```http
GET /api/v1/health/system
```

Returns the health status of the system.

#### Response

```json
{
  "status": "ok",
  "cpu_usage": 10.0,
  "memory_usage": 20.0,
  "disk_usage": 30.0,
  "gpu_usage": null,
  "uptime": 3600.0,
  "temperature": 40.0,
  "version": "1.0.0"
}
```

### Get Camera Health

```http
GET /api/v1/health/cameras
```

Returns the health status of all cameras.

#### Response

```json
{
  "front_door": {
    "name": "front_door",
    "status": "ok",
    "fps": 10.0,
    "bandwidth": 2.0,
    "latency": 50.0,
    "uptime": 3600.0,
    "reconnects": 0,
    "last_frame": 1620000000.0
  },
  "back_door": {
    "name": "back_door",
    "status": "ok",
    "fps": 10.0,
    "bandwidth": 2.0,
    "latency": 50.0,
    "uptime": 3600.0,
    "reconnects": 0,
    "last_frame": 1620000000.0
  }
}
```

### Get Storage Health

```http
GET /api/v1/health/storage
```

Returns the health status of all storage paths.

#### Response

```json
{
  "recordings": {
    "path": "/recordings",
    "total": 1000000000000,
    "used": 300000000000,
    "free": 700000000000,
    "usage": 30.0,
    "read_speed": 100.0,
    "write_speed": 50.0
  },
  "cache": {
    "path": "/cache",
    "total": 100000000000,
    "used": 20000000000,
    "free": 80000000000,
    "usage": 20.0,
    "read_speed": 200.0,
    "write_speed": 100.0
  }
}
```

## Status Codes

The health endpoints use the following status codes:

- `ok`: The component is functioning normally
- `warning`: The component is functioning but with issues
- `error`: The component is not functioning properly
- `critical`: The component is in a critical state
- `unknown`: The component's status is unknown

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/health` | `read` |
| `GET /api/v1/health/system` | `read` |
| `GET /api/v1/health/cameras` | `read` |
| `GET /api/v1/health/storage` | `read` |

See the [Authentication](../authentication.md) documentation for details on permissions.
