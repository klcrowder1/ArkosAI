# Storage API Endpoints

This document describes the API endpoints for managing storage in Arkos AI.

## Overview

The Storage API provides endpoints for managing storage, including getting storage information, usage statistics, and managing backups and restores.

## Base URL

All storage endpoints are available under the base URL:

```
/api/v1/storage
```

## Authentication

All storage endpoints require authentication. See the [Authentication](../authentication.md) documentation for details.

## Endpoints

### Get Storage Information

```http
GET /api/v1/storage
```

Returns information about all storage paths.

#### Response

```json
{
  "recordings": {
    "path": "/recordings",
    "total": 1000000000000,
    "used": 300000000000,
    "free": 700000000000,
    "usage": 30.0,
    "type": "local",
    "tier": "hot",
    "read_only": false,
    "status": "ok"
  },
  "cache": {
    "path": "/cache",
    "total": 100000000000,
    "used": 20000000000,
    "free": 80000000000,
    "usage": 20.0,
    "type": "local",
    "tier": "hot",
    "read_only": false,
    "status": "ok"
  },
  "archive": {
    "path": "/archive",
    "total": 10000000000000,
    "used": 2000000000000,
    "free": 8000000000000,
    "usage": 20.0,
    "type": "network",
    "tier": "cold",
    "read_only": true,
    "status": "ok"
  }
}
```

### Get Storage Usage

```http
GET /api/v1/storage/usage
```

Returns storage usage statistics.

#### Response

```json
{
  "total": 11100000000000,
  "used": 2320000000000,
  "free": 8780000000000,
  "usage": 20.9,
  "by_camera": {
    "camera1": 1000000000000,
    "camera2": 800000000000,
    "camera3": 520000000000
  },
  "by_date": {
    "2021-05": 1000000000000,
    "2021-06": 800000000000,
    "2021-07": 520000000000
  },
  "by_type": {
    "recordings": 2000000000000,
    "events": 300000000000,
    "other": 20000000000
  }
}
```

### List Backups

```http
GET /api/v1/storage/backups
```

Returns a list of all backups.

#### Response

```json
[
  {
    "id": "backup1",
    "name": "Daily Backup",
    "path": "/backups/daily",
    "size": 1000000000,
    "created_at": 1620000000.0,
    "status": "completed",
    "type": "full",
    "retention": 7,
    "description": "Daily full backup"
  },
  {
    "id": "backup2",
    "name": "Weekly Backup",
    "path": "/backups/weekly",
    "size": 2000000000,
    "created_at": 1619000000.0,
    "status": "completed",
    "type": "full",
    "retention": 30,
    "description": "Weekly full backup"
  }
]
```

### Create Backup

```http
POST /api/v1/storage/backups
```

Creates a new backup.

#### Request Body

```json
{
  "name": "Daily Backup",
  "path": "/backups/daily",
  "type": "full",
  "retention": 7,
  "description": "Daily full backup",
  "include_recordings": true,
  "include_events": true,
  "include_config": true
}
```

#### Response

```json
{
  "id": "new_backup_id",
  "name": "Daily Backup",
  "path": "/backups/daily",
  "size": 0,
  "created_at": 1620000000.0,
  "status": "in_progress",
  "type": "full",
  "retention": 7,
  "description": "Daily full backup"
}
```

### Get Backup

```http
GET /api/v1/storage/backups/{backup_id}
```

Returns details for a specific backup.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `backup_id` | string | Backup ID |

#### Response

```json
{
  "id": "backup1",
  "name": "Daily Backup",
  "path": "/backups/daily",
  "size": 1000000000,
  "created_at": 1620000000.0,
  "status": "completed",
  "type": "full",
  "retention": 7,
  "description": "Daily full backup"
}
```

### Delete Backup

```http
DELETE /api/v1/storage/backups/{backup_id}
```

Deletes an existing backup.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `backup_id` | string | Backup ID |

#### Response

```json
{
  "success": true,
  "message": "Backup backup1 deleted"
}
```

### Restore from Backup

```http
POST /api/v1/storage/restore
```

Restores data from a backup.

#### Request Body

```json
{
  "backup_id": "backup1",
  "restore_path": "/restore",
  "include_recordings": true,
  "include_events": true,
  "include_config": true,
  "overwrite": false
}
```

#### Response

```json
{
  "id": "restore_id",
  "status": "in_progress",
  "progress": 0.0,
  "backup_id": "backup1",
  "restore_path": "/restore",
  "started_at": 1620000000.0,
  "completed_at": null,
  "error": null
}
```

### Get Restore Status

```http
GET /api/v1/storage/restore/{restore_id}
```

Returns the status of a restore operation.

#### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `restore_id` | string | Restore ID |

#### Response

```json
{
  "id": "restore_id",
  "status": "completed",
  "progress": 100.0,
  "backup_id": "backup_id",
  "restore_path": "/",
  "started_at": 1620000000.0,
  "completed_at": 1620001000.0,
  "error": null
}
```

## Status Codes

The storage endpoints use the following status codes:

- `ok`: The storage is functioning normally
- `warning`: The storage is functioning but with issues
- `error`: The storage is not functioning properly
- `critical`: The storage is in a critical state
- `unknown`: The storage's status is unknown

## Backup Status Codes

The backup endpoints use the following status codes:

- `in_progress`: The backup is in progress
- `completed`: The backup has completed successfully
- `failed`: The backup has failed
- `canceled`: The backup was canceled

## Restore Status Codes

The restore endpoints use the following status codes:

- `in_progress`: The restore is in progress
- `completed`: The restore has completed successfully
- `failed`: The restore has failed
- `canceled`: The restore was canceled

## Permissions

| Endpoint | Required Permission |
| -------- | ------------------- |
| `GET /api/v1/storage` | `read` |
| `GET /api/v1/storage/usage` | `read` |
| `GET /api/v1/storage/backups` | `read` |
| `POST /api/v1/storage/backups` | `admin` |
| `GET /api/v1/storage/backups/{backup_id}` | `read` |
| `DELETE /api/v1/storage/backups/{backup_id}` | `admin` |
| `POST /api/v1/storage/restore` | `admin` |
| `GET /api/v1/storage/restore/{restore_id}` | `read` |

See the [Authentication](../authentication.md) documentation for details on permissions.
