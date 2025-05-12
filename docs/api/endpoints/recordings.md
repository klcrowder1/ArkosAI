# Recording API Endpoints

This document describes the API endpoints for managing recordings in Arkos AI.

## Overview

The Recording API provides endpoints for managing recordings, including listing recordings, getting recording details, creating and updating recordings, and exporting recordings.

## Base URL

All recording endpoints are available under the base URL:

```
/api/v1/recordings
```

## Authentication

All recording endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### List Recordings

```http
GET /api/v1/recordings
```

Returns a list of recordings.

#### Query Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `camera` | string | null | Filter by camera |
| `after` | number | null | Filter by start time after |
| `before` | number | null | Filter by start time before |
| `min_duration` | number | null | Filter by minimum duration |
| `max_duration` | number | null | Filter by maximum duration |
| `has_audio` | boolean | null | Filter by has_audio |
| `limit` | integer | 100 | Maximum number of recordings to return |
| `offset` | integer | 0 | Number of recordings to skip |

#### Response

```json
{
  "items": [
    {
      "id": "recording_id",
      "camera": "front_door",
      "start_time": 1620000000.0,
      "end_time": 1620000600.0,
      "duration": 600.0,
      "size": 100000000,
      "path": "/recordings/front_door/2021-05-03/12-00-00.mp4",
      "url": "/api/v1/recordings/recording_id/video.mp4",
      "thumbnail_url": "/api/v1/recordings/recording_id/thumbnail.jpg",
      "has_audio": true,
      "resolution": "1920x1080",
      "fps": 30.0,
      "events": ["event1", "event2"]
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

### Get Recording

```http
GET /api/v1/recordings/{recording_id}
```

Returns details for a specific recording.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Response

```json
{
  "id": "recording_id",
  "camera": "front_door",
  "start_time": 1620000000.0,
  "end_time": 1620000600.0,
  "duration": 600.0,
  "size": 100000000,
  "path": "/recordings/front_door/2021-05-03/12-00-00.mp4",
  "url": "/api/v1/recordings/recording_id/video.mp4",
  "thumbnail_url": "/api/v1/recordings/recording_id/thumbnail.jpg",
  "has_audio": true,
  "resolution": "1920x1080",
  "fps": 30.0,
  "events": ["event1", "event2"]
}
```

### Create Recording

```http
POST /api/v1/recordings
```

Creates a new recording.

#### Request Body

```json
{
  "camera": "front_door",
  "start_time": 1620000000.0,
  "end_time": 1620000600.0,
  "events": ["event1", "event2"]
}
```

#### Response

```json
{
  "id": "new_recording_id",
  "camera": "front_door",
  "start_time": 1620000000.0,
  "end_time": 1620000600.0,
  "duration": 600.0,
  "size": 0,
  "path": "/recordings/front_door/1620000000.0.mp4",
  "url": "/api/v1/recordings/new_recording_id/video.mp4",
  "thumbnail_url": "/api/v1/recordings/new_recording_id/thumbnail.jpg",
  "has_audio": true,
  "resolution": "1920x1080",
  "fps": 30.0,
  "events": ["event1", "event2"]
}
```

### Update Recording

```http
PUT /api/v1/recordings/{recording_id}
```

Updates an existing recording.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Request Body

```json
{
  "end_time": 1620000600.0,
  "events": ["event1", "event2"]
}
```

#### Response

```json
{
  "id": "recording_id",
  "camera": "front_door",
  "start_time": 1620000000.0,
  "end_time": 1620000600.0,
  "duration": 600.0,
  "size": 100000000,
  "path": "/recordings/front_door/2021-05-03/12-00-00.mp4",
  "url": "/api/v1/recordings/recording_id/video.mp4",
  "thumbnail_url": "/api/v1/recordings/recording_id/thumbnail.jpg",
  "has_audio": true,
  "resolution": "1920x1080",
  "fps": 30.0,
  "events": ["event1", "event2"]
}
```

### Delete Recording

```http
DELETE /api/v1/recordings/{recording_id}
```

Deletes an existing recording.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Response

```json
{
  "success": true,
  "message": "Recording recording_id deleted"
}
```

### Export Recording

```http
POST /api/v1/recordings/{recording_id}/export
```

Exports a recording to a different format.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Request Body

```json
{
  "format": "mp4",
  "quality": 80,
  "include_audio": true,
  "include_timestamp": true,
  "include_events": true,
  "output_path": "/exports/my_export.mp4"
}
```

#### Response

```json
{
  "id": "export_id",
  "status": "in_progress",
  "progress": 0.0,
  "output_path": "/exports/export_id.mp4",
  "url": "/api/v1/recordings/exports/export_id"
}
```

### Get Export Status

```http
GET /api/v1/recordings/exports/{export_id}
```

Returns the status of a recording export.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `export_id` | string | Export ID |

#### Response

```json
{
  "id": "export_id",
  "status": "completed",
  "progress": 100.0,
  "output_path": "/exports/export_id.mp4",
  "url": "/api/v1/recordings/exports/export_id"
}
```

## Media Endpoints

The following endpoints are available for accessing recording media:

### Get Recording Video

```http
GET /api/v1/recordings/{recording_id}/video.mp4
```

Returns the video file for a recording.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Response

The video file in MP4 format.

### Get Recording Thumbnail

```http
GET /api/v1/recordings/{recording_id}/thumbnail.jpg
```

Returns the thumbnail image for a recording.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `recording_id` | string | Recording ID |

#### Response

The thumbnail image in JPEG format.

## Error Responses

### Recording Not Found

```json
{
  "error": {
    "code": "recording_not_found",
    "message": "Recording recording_id not found",
    "details": null
  }
}
```

### Export Not Found

```json
{
  "error": {
    "code": "export_not_found",
    "message": "Export export_id not found",
    "details": null
  }
}
```

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/recordings` | `read` |
| `GET /api/v1/recordings/{recording_id}` | `read` |
| `POST /api/v1/recordings` | `write` |
| `PUT /api/v1/recordings/{recording_id}` | `write` |
| `DELETE /api/v1/recordings/{recording_id}` | `write` |
| `POST /api/v1/recordings/{recording_id}/export` | `write` |
| `GET /api/v1/recordings/exports/{export_id}` | `read` |
| `GET /api/v1/recordings/{recording_id}/video.mp4` | `read` |
| `GET /api/v1/recordings/{recording_id}/thumbnail.jpg` | `read` |

See the [Authentication](../authentication.md) documentation for details on permissions.
