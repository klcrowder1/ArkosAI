# API Overview

This document provides an overview of the Arkos AI API, including design principles, authentication, endpoints, and usage examples.

## API Design Principles

The Arkos AI API follows these design principles:

1. **RESTful**: The API follows REST principles for resource-oriented design
2. **JSON**: All requests and responses use JSON format
3. **Versioned**: API endpoints are versioned to support backward compatibility
4. **Secure**: All endpoints require authentication and use HTTPS
5. **Consistent**: Endpoints follow consistent naming and behavior patterns
6. **Documented**: All endpoints are documented with OpenAPI/Swagger
7. **Rate Limited**: API requests are rate limited to prevent abuse

## API Base URL

The API is accessible at the following base URL:

```
https://<server-address>/api/v1
```

For local development:

```
http://localhost:5001/api/v1
```

## Authentication

The API supports multiple authentication methods:

### API Key Authentication

For server-to-server communication, API key authentication is used:

```http
GET /api/v1/cameras
X-API-Key: <api-key>
```

### JWT Authentication

For user authentication, JWT tokens are used:

```http
GET /api/v1/cameras
Authorization: Bearer <jwt-token>
```

To obtain a JWT token:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "role": "admin",
    "is_active": true
  }
}
```

For detailed information about authentication and authorization, including user management, API keys, sessions, and role-based access control, see the [Authentication and Authorization](./authentication.md) documentation.

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": {
      "camera_id": "Camera ID is required"
    }
  }
}
```

Common error codes:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Pagination

List endpoints support pagination using the following query parameters:

- `limit`: Maximum number of items to return (default: 100, max: 1000)
- `offset`: Number of items to skip (default: 0)

Response includes pagination metadata:

```json
{
  "items": [...],
  "pagination": {
    "total": 150,
    "limit": 100,
    "offset": 0,
    "next": "/api/v1/events?limit=100&offset=100"
  }
}
```

## Filtering

List endpoints support filtering using query parameters:

```http
GET /api/v1/events?camera_id=front_door&label=person&start_time=2023-01-01T00:00:00Z
```

## Sorting

List endpoints support sorting using the `sort` query parameter:

```http
GET /api/v1/events?sort=start_time:desc
```

Multiple sort fields are supported:

```http
GET /api/v1/events?sort=camera_id:asc,start_time:desc
```

## API Modules

The API is organized into the following modules:

### Core API

- **Cameras**: Camera management and control
- **Events**: Event detection and management
- **Recordings**: Video recording management
- **Clips**: Event clip management
- **Config**: System configuration

### Analytics API

- **Models**: Custom detection model management
- **Activities**: Activity recognition
- **Audio**: Audio analytics

### Health API

- **Status**: Camera health status
- **Connectivity**: Camera connectivity
- **Quality**: Video quality monitoring

### IO API

- **Hardware**: Hardware input/output management
- **MQTT**: MQTT integration
- **Triggers**: Event trigger management
- **Scheduler**: Scheduled action management

### IoT API

- **Devices**: IoT device management
- **Protocols**: Protocol support
- **Automation**: Automation rule management

### Notify API

- **Webhooks**: Webhook management
- **Notifications**: Notification management

### System API

- **Status**: System status
- **Logs**: System logs
- **Updates**: System updates
- **Users**: User management

## API Endpoints

### Core API Endpoints

#### Cameras

- `GET /api/v1/cameras`: List all cameras
- `GET /api/v1/cameras/{camera_id}`: Get camera details
- `PUT /api/v1/cameras/{camera_id}`: Update camera configuration
- `GET /api/v1/cameras/{camera_id}/snapshot`: Get camera snapshot
- `GET /api/v1/cameras/{camera_id}/stream`: Get camera stream (MJPEG)
- `POST /api/v1/cameras/{camera_id}/ptz`: Control PTZ camera

#### Events

- `GET /api/v1/events`: List events
- `GET /api/v1/events/{event_id}`: Get event details
- `DELETE /api/v1/events/{event_id}`: Delete event
- `GET /api/v1/events/{event_id}/clip`: Get event clip
- `GET /api/v1/events/{event_id}/snapshot`: Get event snapshot
- `PUT /api/v1/events/{event_id}/tags`: Update event tags

#### Recordings

- `GET /api/v1/recordings`: List recordings
- `GET /api/v1/recordings/{recording_id}`: Get recording details
- `DELETE /api/v1/recordings/{recording_id}`: Delete recording
- `GET /api/v1/recordings/{recording_id}/clip`: Get recording clip

#### Config

- `GET /api/v1/config`: Get system configuration
- `PUT /api/v1/config`: Update system configuration
- `POST /api/v1/config/validate`: Validate configuration
- `POST /api/v1/config/backup`: Create configuration backup
- `POST /api/v1/config/restore`: Restore configuration from backup

### Analytics API Endpoints

#### Models

- `GET /api/v1/analytics/models`: List all models
- `GET /api/v1/analytics/models/{model_id}`: Get model details
- `POST /api/v1/analytics/models`: Upload a new model
- `DELETE /api/v1/analytics/models/{model_id}`: Delete a model
- `POST /api/v1/analytics/models/{model_id}/test`: Test a model

#### Activities

- `GET /api/v1/analytics/activities`: List detected activities
- `GET /api/v1/analytics/activities/{activity_id}`: Get activity details
- `GET /api/v1/analytics/behaviors`: List detected behaviors
- `GET /api/v1/analytics/behaviors/{behavior_id}`: Get behavior details

#### Audio

- `GET /api/v1/analytics/audio/events`: List audio events
- `GET /api/v1/analytics/audio/events/{event_id}`: Get audio event details
- `GET /api/v1/analytics/audio/detectors`: List audio detectors
- `POST /api/v1/analytics/audio/detectors/{detector_id}/test`: Test audio detector

### Health API Endpoints

#### Status

- `GET /api/v1/health/status`: Get overall health status
- `GET /api/v1/health/status/{camera_id}`: Get health status for a specific camera

#### Connectivity

- `GET /api/v1/health/connectivity`: Get connectivity status for all cameras
- `GET /api/v1/health/connectivity/{camera_id}`: Get connectivity status for a specific camera
- `POST /api/v1/health/connectivity/{camera_id}/test`: Test connectivity for a specific camera

#### Quality

- `GET /api/v1/health/quality`: Get quality status for all cameras
- `GET /api/v1/health/quality/{camera_id}`: Get quality status for a specific camera
- `GET /api/v1/health/quality/{camera_id}/dirty_lens`: Get dirty lens status for a specific camera
- `POST /api/v1/health/quality/{camera_id}/dirty_lens/reset`: Reset dirty lens reference for a specific camera
- `GET /api/v1/health/quality/{camera_id}/scene_change`: Get scene change status for a specific camera
- `POST /api/v1/health/quality/{camera_id}/scene_change/reset`: Reset scene change reference for a specific camera

### IO API Endpoints

#### Hardware

- `GET /api/v1/io/hardware/inputs`: List all hardware inputs
- `GET /api/v1/io/hardware/inputs/{input_id}`: Get input details and state
- `GET /api/v1/io/hardware/outputs`: List all hardware outputs
- `GET /api/v1/io/hardware/outputs/{output_id}`: Get output details and state
- `PUT /api/v1/io/hardware/outputs/{output_id}`: Set output state

#### MQTT

- `GET /api/v1/io/mqtt/status`: Get MQTT connection status
- `GET /api/v1/io/mqtt/topics`: List all MQTT topics
- `POST /api/v1/io/mqtt/publish`: Publish a message to an MQTT topic

#### Triggers

- `GET /api/v1/io/triggers`: List all triggers
- `GET /api/v1/io/triggers/{trigger_id}`: Get trigger details
- `POST /api/v1/io/triggers`: Create a new trigger
- `PUT /api/v1/io/triggers/{trigger_id}`: Update a trigger
- `DELETE /api/v1/io/triggers/{trigger_id}`: Delete a trigger
- `POST /api/v1/io/triggers/{trigger_id}/test`: Test a trigger

#### Scheduler

- `GET /api/v1/io/scheduler/schedules`: List all schedules
- `GET /api/v1/io/scheduler/schedules/{schedule_id}`: Get schedule details
- `POST /api/v1/io/scheduler/schedules`: Create a new schedule
- `PUT /api/v1/io/scheduler/schedules/{schedule_id}`: Update a schedule
- `DELETE /api/v1/io/scheduler/schedules/{schedule_id}`: Delete a schedule
- `POST /api/v1/io/scheduler/schedules/{schedule_id}/run`: Run a schedule manually

### System API Endpoints

#### Status

- `GET /api/v1/system/status`: Get system status
- `GET /api/v1/system/stats`: Get system statistics
- `GET /api/v1/system/storage`: Get storage status

#### Logs

- `GET /api/v1/system/logs`: Get system logs
- `GET /api/v1/system/logs/{log_id}`: Get specific log details
- `POST /api/v1/system/logs/download`: Download logs as a file

#### Updates

- `GET /api/v1/system/updates`: Check for updates
- `POST /api/v1/system/updates/install`: Install updates

#### Users

- `GET /api/v1/system/users`: List all users
- `GET /api/v1/system/users/{user_id}`: Get user details
- `POST /api/v1/system/users`: Create a new user
- `PUT /api/v1/system/users/{user_id}`: Update a user
- `DELETE /api/v1/system/users/{user_id}`: Delete a user
- `POST /api/v1/system/users/{user_id}/reset-password`: Reset user password

## WebSocket API

In addition to the REST API, Arkos AI provides a WebSocket API for real-time updates:

```
ws://<server-address>/api/v1/ws
```

Authentication is required using a query parameter:

```
ws://<server-address>/api/v1/ws?token=<jwt-token>
```

### WebSocket Messages

Messages are sent as JSON objects with a `type` field indicating the message type:

```json
{
  "type": "event",
  "data": {
    "id": "123456",
    "camera_id": "front_door",
    "label": "person",
    "start_time": "2023-01-01T12:00:00Z",
    "end_time": "2023-01-01T12:00:10Z",
    "thumbnail": "/api/v1/events/123456/snapshot",
    "clip": "/api/v1/events/123456/clip"
  }
}
```

### WebSocket Subscriptions

To subscribe to specific events, send a subscription message:

```json
{
  "type": "subscribe",
  "topics": ["events", "camera.front_door"]
}
```

To unsubscribe:

```json
{
  "type": "unsubscribe",
  "topics": ["camera.front_door"]
}
```

## API Client Libraries

Arkos AI provides client libraries for common programming languages:

### Python Client

```python
from arkos.client import ArkosClient

# Create client
client = ArkosClient("http://localhost:5001", api_key="your-api-key")

# Get cameras
cameras = client.cameras.list()

# Get events
events = client.events.list(
    camera_id="front_door",
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

# Control output
client.io.set_output_state("perimeter_lights", "on")
```

### JavaScript Client

```javascript
import { ArkosClient } from 'arkos-client';

// Create client
const client = new ArkosClient('http://localhost:5001', {
  apiKey: 'your-api-key'
});

// Get cameras
const cameras = await client.cameras.list();

// Get events
const events = await client.events.list({
  cameraId: 'front_door',
  startTime: '2023-01-01T00:00:00Z',
  endTime: '2023-01-02T00:00:00Z'
});

// Control output
await client.io.setOutputState('perimeter_lights', 'on');
```

## API Documentation

The complete API documentation is available using Swagger UI at:

```
http://<server-address>/api/docs
```

For local development:

```
http://localhost:5001/api/docs
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits are applied per API key or user and are specified in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1672574400
```

If the rate limit is exceeded, the API returns a `429 Too Many Requests` response.

## Cross-Origin Resource Sharing (CORS)

The API supports CORS for browser-based applications. The following headers are included in responses:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

## API Versioning

The API is versioned to ensure backward compatibility. The version is included in the URL path:

```
/api/v1/cameras
```

When breaking changes are introduced, a new API version is created:

```
/api/v2/cameras
```

Older API versions are supported for a transition period to allow clients to migrate to the new version.

For detailed information about API versioning, including how to specify versions, version negotiation, and best practices, see the [API Versioning](./versioning.md) documentation.
