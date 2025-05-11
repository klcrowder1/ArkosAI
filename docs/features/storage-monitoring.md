# Storage Monitoring

Arkos AI includes a comprehensive storage monitoring system that provides detailed metrics and health status information for your storage system. This feature helps you monitor storage usage, performance, and health, allowing you to proactively manage your storage resources.

## Overview

The storage monitoring system tracks various metrics for both storage paths and cameras, including:

- Storage usage (total, used, free space)
- Storage health status
- I/O performance (read/write speeds)
- Camera-specific storage metrics
- Estimated time until storage is full

This information is available through the API and can be used to monitor the health of your storage system, identify potential issues, and plan for storage expansion.

## Storage Metrics

The storage monitoring system tracks the following metrics for each storage path:

- **Total Space**: Total storage capacity in MB
- **Used Space**: Used storage space in MB
- **Free Space**: Available storage space in MB
- **Usage Percentage**: Percentage of storage used
- **Read Speed**: Read speed in MB/s
- **Write Speed**: Write speed in MB/s
- **I/O Errors**: Number of I/O errors detected
- **Health Status**: Current health status (healthy, warning, critical, unknown)

## Camera Storage Metrics

For each camera, the following storage metrics are tracked:

- **Total Size**: Total storage used by the camera in MB
- **Event Size**: Storage used by event recordings in MB
- **Non-Event Size**: Storage used by non-event recordings in MB
- **Bandwidth**: Average bandwidth usage in MB/hour
- **Recording Count**: Number of recording segments
- **Event Count**: Number of events
- **Oldest Recording**: Timestamp of the oldest recording
- **Newest Recording**: Timestamp of the newest recording

## Health Status

The storage monitoring system assigns a health status to each storage path based on usage:

- **Healthy**: Usage is below 85%
- **Warning**: Usage is between 85% and 95%
- **Critical**: Usage is above 95%
- **Unknown**: Unable to determine health status

## API Endpoints

The storage monitoring system provides the following API endpoints:

### Get Overall Storage Status

```
GET /api/storage/status
```

Returns the overall storage status, including total space, used space, free space, usage percentage, and estimated time until full.

### Get All Storage Metrics

```
GET /api/storage/metrics
```

Returns all storage metrics, including overall metrics, storage path metrics, and camera metrics.

### Get Storage Path Metrics

```
GET /api/storage/paths
```

Returns metrics for all storage paths.

### Get Specific Storage Path Metrics

```
GET /api/storage/paths/{path}
```

Returns metrics for a specific storage path.

### Get Camera Storage Metrics

```
GET /api/storage/cameras
```

Returns storage metrics for all cameras.

### Get Specific Camera Storage Metrics

```
GET /api/storage/cameras/{camera_name}
```

Returns storage metrics for a specific camera.

### Run I/O Performance Check

```
POST /api/storage/check-io-performance
```

Runs an I/O performance check on all storage paths and returns the updated metrics.

## Configuration

The storage monitoring system is automatically enabled and requires no additional configuration. It integrates with the tiered storage system if enabled, monitoring all storage tiers.

## Notifications

The storage monitoring system can send notifications for storage-related issues:

- **Storage Critical**: Sent when a storage path reaches critical usage (>95%)
- **Storage Warning**: Sent when a storage path reaches warning usage (>85%)
- **Storage I/O Error**: Sent when I/O errors are detected on a storage path

Notifications are sent through the configured notification providers (MQTT, webhook, console).

## Integration with Health Monitoring

The storage monitoring system integrates with the health monitoring system, providing storage health information as part of the overall system health status.

## Performance Considerations

The storage monitoring system performs regular checks of storage metrics, which may have a small impact on system performance. The frequency of these checks can be adjusted if needed:

- **Basic Metrics**: Checked every 5 minutes by default
- **I/O Performance**: Checked every hour by default

These intervals can be adjusted in the configuration if needed.

## Troubleshooting

If you encounter issues with the storage monitoring system, check the following:

1. Ensure the storage paths are accessible and have appropriate permissions
2. Check the logs for any error messages related to storage monitoring
3. Verify that the notification system is properly configured if you're not receiving notifications

## Example API Response

Here's an example response from the `/api/storage/status` endpoint:

```json
{
  "total_space_mb": 1000000,
  "used_space_mb": 500000,
  "free_space_mb": 500000,
  "usage_percent": 50.0,
  "total_camera_size_mb": 450000,
  "total_event_size_mb": 150000,
  "total_non_event_size_mb": 300000,
  "total_bandwidth_mbh": 1000,
  "hours_until_full": 500,
  "days_until_full": 20.8,
  "health_status": "healthy",
  "last_updated": "2025-05-11T18:00:00.000Z"
}
