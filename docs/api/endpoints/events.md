# Event API Endpoints

This document describes the API endpoints for managing events in Arkos AI.

## Overview

The Event API provides endpoints for managing events, including listing events, getting event details, creating and updating events, and deleting events.

## Base URL

All event endpoints are available under the base URL:

```
/api/v1/events
```

## Authentication

All event endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### List Events

```http
GET /api/v1/events
```

Returns a list of events.

#### Query Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `camera` | string | null | Filter by camera |
| `label` | string | null | Filter by label |
| `zone` | string | null | Filter by zone |
| `after` | number | null | Filter by start time after |
| `before` | number | null | Filter by start time before |
| `has_clip` | boolean | null | Filter by has_clip |
| `has_snapshot` | boolean | null | Filter by has_snapshot |
| `limit` | integer | 100 | Maximum number of events to return |
| `offset` | integer | 0 | Number of events to skip |

#### Response

```json
{
  "items": [
    {
      "id": "event_id",
      "camera": "front_door",
      "label": "person",
      "start_time": 1620000000.0,
      "end_time": 1620000010.0,
      "thumbnail": "/api/v1/events/event_id/thumbnail.jpg",
      "has_clip": true,
      "has_snapshot": true,
      "zones": ["yard", "driveway"],
      "score": 0.9,
      "box": [100, 100, 200, 200],
      "area": 10000,
      "ratio": 1.0,
      "region": [0, 0, 1920, 1080],
      "stationary": false,
      "motionless_count": 0,
      "position_changes": 0,
      "current_zones": ["yard", "driveway"],
      "attributes": {
        "color": "red",
        "direction": "north"
      }
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

### Get Event

```http
GET /api/v1/events/{event_id}
```

Returns details for a specific event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Response

```json
{
  "id": "event_id",
  "camera": "front_door",
  "label": "person",
  "start_time": 1620000000.0,
  "end_time": 1620000010.0,
  "thumbnail": "/api/v1/events/event_id/thumbnail.jpg",
  "has_clip": true,
  "has_snapshot": true,
  "zones": ["yard", "driveway"],
  "score": 0.9,
  "box": [100, 100, 200, 200],
  "area": 10000,
  "ratio": 1.0,
  "region": [0, 0, 1920, 1080],
  "stationary": false,
  "motionless_count": 0,
  "position_changes": 0,
  "current_zones": ["yard", "driveway"],
  "attributes": {
    "color": "red",
    "direction": "north"
  }
}
```

### Create Event

```http
POST /api/v1/events/{camera_name}/{label}
```

Creates a new event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `camera_name` | string | Camera name |
| `label` | string | Object label |

#### Request Body

```json
{
  "score": 0.9,
  "box": [100, 100, 200, 200],
  "region": [0, 0, 1920, 1080],
  "zones": ["yard", "driveway"],
  "attributes": {
    "color": "red",
    "direction": "north"
  }
}
```

#### Response

```json
{
  "id": "new_event_id",
  "camera": "front_door",
  "label": "person",
  "start_time": 1620000000.0,
  "end_time": null,
  "thumbnail": "/api/v1/events/new_event_id/thumbnail.jpg",
  "has_clip": false,
  "has_snapshot": false,
  "zones": ["yard", "driveway"],
  "score": 0.9,
  "box": [100, 100, 200, 200],
  "area": 0,
  "ratio": 0.0,
  "region": [0, 0, 1920, 1080],
  "stationary": false,
  "motionless_count": 0,
  "position_changes": 0,
  "current_zones": ["yard", "driveway"],
  "attributes": {
    "color": "red",
    "direction": "north"
  }
}
```

### Update Event

```http
PUT /api/v1/events/{event_id}
```

Updates an existing event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Request Body

```json
{
  "end_time": 1620000010.0,
  "attributes": {
    "color": "red",
    "direction": "north"
  }
}
```

#### Response

```json
{
  "id": "event_id",
  "camera": "front_door",
  "label": "person",
  "start_time": 1620000000.0,
  "end_time": 1620000010.0,
  "thumbnail": "/api/v1/events/event_id/thumbnail.jpg",
  "has_clip": true,
  "has_snapshot": true,
  "zones": ["yard", "driveway"],
  "score": 0.9,
  "box": [100, 100, 200, 200],
  "area": 10000,
  "ratio": 1.0,
  "region": [0, 0, 1920, 1080],
  "stationary": false,
  "motionless_count": 0,
  "position_changes": 0,
  "current_zones": ["yard", "driveway"],
  "attributes": {
    "color": "red",
    "direction": "north"
  }
}
```

### Delete Event

```http
DELETE /api/v1/events/{event_id}
```

Deletes an existing event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Response

```json
{
  "success": true,
  "message": "Event event_id deleted"
}
```

## Media Endpoints

The following endpoints are available for accessing event media:

### Get Event Thumbnail

```http
GET /api/v1/events/{event_id}/thumbnail.jpg
```

Returns the thumbnail image for an event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Response

The thumbnail image in JPEG format.

### Get Event Snapshot

```http
GET /api/v1/events/{event_id}/snapshot.jpg
```

Returns the snapshot image for an event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Response

The snapshot image in JPEG format.

### Get Event Clip

```http
GET /api/v1/events/{event_id}/clip.mp4
```

Returns the video clip for an event.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `event_id` | string | Event ID |

#### Response

The video clip in MP4 format.

## Error Responses

### Event Not Found

```json
{
  "error": {
    "code": "event_not_found",
    "message": "Event event_id not found",
    "details": null
  }
}
```

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/events` | `read` |
| `GET /api/v1/events/{event_id}` | `read` |
| `POST /api/v1/events/{camera_name}/{label}` | `write` |
| `PUT /api/v1/events/{event_id}` | `write` |
| `DELETE /api/v1/events/{event_id}` | `write` |
| `GET /api/v1/events/{event_id}/thumbnail.jpg` | `read` |
| `GET /api/v1/events/{event_id}/snapshot.jpg` | `read` |
| `GET /api/v1/events/{event_id}/clip.mp4` | `read` |

See the [Authentication](../authentication.md) documentation for details on permissions.
