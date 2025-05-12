# Client Libraries

This document describes the client libraries available for the Arkos AI API.

## Overview

Arkos AI provides official client libraries for various programming languages to make it easier to interact with the API. These libraries handle authentication, request formatting, and response parsing, allowing you to focus on your application logic.

## Available Libraries

### Python

The official Python client library for Arkos AI.

#### Installation

```bash
pip install arkos-client
```

#### Usage

```python
from arkos_client import ArkosClient

# Initialize the client with API key authentication
client = ArkosClient(
    host="http://localhost:5000",
    api_key="your_api_key"
)

# Or initialize with JWT authentication
client = ArkosClient(
    host="http://localhost:5000",
    username="admin",
    password="password"
)

# Camera operations
cameras = client.cameras.list()
camera = client.cameras.get("front_door")
new_camera = client.cameras.create({
    "name": "back_door",
    "url": "rtsp://example.com/back_door"
})
client.cameras.update("back_door", {
    "url": "rtsp://example.com/updated_back_door"
})
client.cameras.delete("back_door")
status = client.cameras.get_connection_status("front_door")
client.cameras.reset_connection("front_door")
latest_frame = client.cameras.get_latest_frame("front_door", format="jpg", bbox=True)
mjpeg_url = client.cameras.get_mjpeg_feed("front_door", fps=5, height=720)
ptz_info = client.cameras.get_ptz_info("front_door")

# Event operations
events = client.events.list(
    camera="front_door",
    after=1620000000.0,
    before=1620001000.0,
    has_clip=1,
    has_snapshot=1
)
event = client.events.get("event_id")
new_event = client.events.create("front_door", "person", score=0.9, duration=30)
client.events.end("event_id")
client.events.set_retain("event_id")
client.events.delete_retain("event_id")
client.events.set_sub_label("event_id", "car", sub_label_score=0.95)
client.events.set_description("event_id", "Car in driveway")
client.events.regenerate_description("event_id", source="thumbnails")
client.events.delete_multiple(["event_id1", "event_id2"])
snapshot = client.events.get_snapshot("event_id", bbox=1, timestamp=1)
thumbnail = client.events.get_thumbnail("event_id", extension="jpg")
clip = client.events.get_clip("event_id")
search_results = client.events.search(query="car in driveway", limit=10)
summary = client.events.get_summary(timezone="America/New_York")

# Recording operations
recordings = client.recordings.list("front_door", after=1620000000.0, before=1620001000.0)
storage_usage = client.recordings.get_storage_usage()
summary = client.recordings.get_summary(timezone="America/New_York", cameras="front_door,back_door")
camera_summary = client.recordings.get_camera_summary("front_door", timezone="America/New_York")
clip = client.recordings.get_clip("front_door", 1620000000.0, 1620001000.0)
snapshot = client.recordings.get_snapshot("front_door", 1620000500.0, format="jpg", height=720)
export = client.recordings.export("front_door", 1620000000.0, 1620001000.0, name="Front Door Recording")
exports = client.recordings.get_exports()
export_details = client.recordings.get_export("export_id")
client.recordings.rename_export("export_id", "New Name")
client.recordings.delete_export("export_id")
preview = client.recordings.get_preview("front_door", 1620000000.0, 1620001000.0, format="gif")

# Health operations
health = client.health.get()
system_health = client.health.get_system()
camera_health = client.health.get_cameras()
storage_health = client.health.get_storage()
stats = client.health.get_stats()
stats_history = client.health.get_stats_history(keys="cpu,memory,disk")
metrics = client.health.get_metrics()
ffprobe = client.health.get_ffprobe(paths="/path/to/video.mp4")
vainfo = client.health.get_vainfo()
nvinfo = client.health.get_nvinfo()
logs = client.health.get_logs("arkos", start=0, end=100)

# Storage operations
storage = client.storage.get()
usage = client.storage.get_usage()
backups = client.storage.get_backups()
backup = client.storage.create_backup(name="Backup 1", include_recordings=True)
backup_details = client.storage.get_backup("backup_id")
client.storage.delete_backup("backup_id")
restore = client.storage.restore(backup_id="backup_id", restore_recordings=True)
restore_status = client.storage.get_restore_status("restore_id")

# System operations
info = client.system.get_info()
stats = client.system.get_stats()
config = client.system.get_config()
client.system.update_config({"detectors": {"cpu": {"type": "cpu"}}}, requires_restart=True)
client.system.restart()
logs = client.system.get_logs("arkos", start=0, end=100)
version = client.system.get_version()
schema = client.system.get_config_schema()
raw_config = client.system.get_raw_config()
client.system.save_config("config content", "backup")
labels = client.system.get_labels(camera="front_door")
sub_labels = client.system.get_sub_labels(split_joined=1)
license_plates = client.system.get_recognized_license_plates(split_joined=1)
timeline = client.system.get_timeline(camera="front_door", limit=100)
hourly_timeline = client.system.get_hourly_timeline(cameras="front_door", timezone="America/New_York")
```

#### Error Handling

```python
from arkos_client import ArkosClient, ArkosApiError, ArkosAuthError, ArkosRateLimitError, ArkosConnectionError, ArkosTimeoutError

client = ArkosClient(host="http://localhost:5000", api_key="your_api_key")

try:
    cameras = client.cameras.list()
except ArkosAuthError as e:
    print(f"Authentication error: {e}")
except ArkosRateLimitError as e:
    print(f"Rate limit exceeded: {e}, reset at {e.reset_time}")
except ArkosApiError as e:
    print(f"API error: {e}, status code: {e.status_code}, error code: {e.error_code}")
except ArkosConnectionError as e:
    print(f"Connection error: {e}")
except ArkosTimeoutError as e:
    print(f"Timeout error: {e}")
```

### JavaScript

The official JavaScript client library for Arkos AI.

#### Installation

```bash
npm install arkos-client
```

#### Usage

```javascript
const { ArkosClient } = require('arkos-client');

// Initialize the client with API key authentication
const client = new ArkosClient({
  host: 'http://localhost:5000',
  apiKey: 'your_api_key'
});

// Or initialize with JWT authentication
const client = new ArkosClient({
  host: 'http://localhost:5000',
  username: 'admin',
  password: 'password'
});

// Camera operations
async function cameraOperations() {
  try {
    // List all cameras
    const cameras = await client.cameras.list();
    console.log(cameras);

    // Get a specific camera
    const camera = await client.cameras.get('front_door');
    console.log(camera);

    // Create a new camera
    const newCamera = await client.cameras.create({
      name: 'back_door',
      url: 'rtsp://example.com/back_door'
    });
    console.log(newCamera);

    // Update an existing camera
    await client.cameras.update('back_door', {
      url: 'rtsp://example.com/updated_back_door'
    });

    // Delete a camera
    await client.cameras.delete('back_door');

    // Get camera connection status
    const status = await client.cameras.getConnectionStatus('front_door');
    console.log(status);

    // Reset camera connection
    await client.cameras.resetConnection('front_door');

    // Get the latest frame from a camera
    const latestFrame = await client.cameras.getLatestFrame('front_door', {
      format: 'jpg',
      bbox: true,
      timestamp: true
    });
    console.log(latestFrame);

    // Get MJPEG feed URL
    const mjpegUrl = client.cameras.getMjpegFeed('front_door', {
      fps: 5,
      height: 720
    });
    console.log(mjpegUrl);

    // Get PTZ information
    const ptzInfo = await client.cameras.getPtzInfo('front_door');
    console.log(ptzInfo);
  } catch (error) {
    console.error(error);
  }
}

// Event operations
async function eventOperations() {
  try {
    // List events
    const events = await client.events.list({
      camera: 'front_door',
      after: 1620000000.0,
      before: 1620001000.0,
      has_clip: 1,
      has_snapshot: 1
    });
    console.log(events);

    // Get a specific event
    const event = await client.events.get('event_id');
    console.log(event);

    // Create a new event
    const newEvent = await client.events.create('front_door', 'person', {
      score: 0.9,
      duration: 30
    });
    console.log(newEvent);

    // End an event
    await client.events.end('event_id');

    // Set retain flag for an event
    await client.events.setRetain('event_id');

    // Delete retain flag for an event
    await client.events.deleteRetain('event_id');

    // Set sub-label for an event
    await client.events.setSubLabel('event_id', 'car', 0.95);

    // Set description for an event
    await client.events.setDescription('event_id', 'Car in driveway');

    // Regenerate description for an event
    await client.events.regenerateDescription('event_id', 'thumbnails');

    // Delete multiple events
    await client.events.deleteMultiple(['event_id1', 'event_id2']);

    // Get event snapshot
    const snapshot = await client.events.getSnapshot('event_id', {
      bbox: 1,
      timestamp: 1
    });
    console.log(snapshot);

    // Get event thumbnail
    const thumbnail = await client.events.getThumbnail('event_id', 'jpg');
    console.log(thumbnail);

    // Get event clip
    const clip = await client.events.getClip('event_id');
    console.log(clip);

    // Search events
    const searchResults = await client.events.search({
      query: 'car in driveway',
      limit: 10
    });
    console.log(searchResults);

    // Get events summary
    const summary = await client.events.getSummary({
      timezone: 'America/New_York'
    });
    console.log(summary);
  } catch (error) {
    console.error(error);
  }
}

// Recording operations
async function recordingOperations() {
  try {
    // List recordings
    const recordings = await client.recordings.list('front_door', {
      after: 1620000000.0,
      before: 1620001000.0
    });
    console.log(recordings);

    // Get storage usage
    const storageUsage = await client.recordings.getStorageUsage();
    console.log(storageUsage);

    // Get recordings summary
    const summary = await client.recordings.getSummary('America/New_York', 'front_door,back_door');
    console.log(summary);

    // Get camera recordings summary
    const cameraSummary = await client.recordings.getCameraSummary('front_door', 'America/New_York');
    console.log(cameraSummary);

    // Get recording clip
    const clip = await client.recordings.getClip('front_door', 1620000000.0, 1620001000.0);
    console.log(clip);

    // Get recording snapshot
    const snapshot = await client.recordings.getSnapshot('front_door', 1620000500.0, {
      format: 'jpg',
      height: 720
    });
    console.log(snapshot);

    // Export recording
    const exportData = await client.recordings.export('front_door', 1620000000.0, 1620001000.0, {
      name: 'Front Door Recording'
    });
    console.log(exportData);

    // Get exports
    const exports = await client.recordings.getExports();
    console.log(exports);

    // Get export details
    const exportDetails = await client.recordings.getExport('export_id');
    console.log(exportDetails);

    // Rename export
    await client.recordings.renameExport('export_id', 'New Name');

    // Delete export
    await client.recordings.deleteExport('export_id');

    // Get preview
    const preview = await client.recordings.getPreview('front_door', 1620000000.0, 1620001000.0, 'gif');
    console.log(preview);
  } catch (error) {
    console.error(error);
  }
}

// Health operations
async function healthOperations() {
  try {
    // Get health status
    const health = await client.health.get();
    console.log(health);

    // Get system health
    const systemHealth = await client.health.getSystem();
    console.log(systemHealth);

    // Get camera health
    const cameraHealth = await client.health.getCameras();
    console.log(cameraHealth);

    // Get storage health
    const storageHealth = await client.health.getStorage();
    console.log(storageHealth);

    // Get system statistics
    const stats = await client.health.getStats();
    console.log(stats);

    // Get system statistics history
    const statsHistory = await client.health.getStatsHistory('cpu,memory,disk');
    console.log(statsHistory);

    // Get system metrics
    const metrics = await client.health.getMetrics();
    console.log(metrics);

    // Get ffprobe information
    const ffprobe = await client.health.getFfprobe('/path/to/video.mp4');
    console.log(ffprobe);

    // Get VA-API information
    const vainfo = await client.health.getVainfo();
    console.log(vainfo);

    // Get NVIDIA information
    const nvinfo = await client.health.getNvinfo();
    console.log(nvinfo);

    // Get logs
    const logs = await client.health.getLogs('arkos', {
      start: 0,
      end: 100
    });
    console.log(logs);
  } catch (error) {
    console.error(error);
  }
}

// Storage operations
async function storageOperations() {
  try {
    // Get storage information
    const storage = await client.storage.get();
    console.log(storage);

    // Get storage usage
    const usage = await client.storage.getUsage();
    console.log(usage);

    // Get backups
    const backups = await client.storage.getBackups();
    console.log(backups);

    // Create backup
    const backup = await client.storage.createBackup({
      name: 'Backup 1',
      include_recordings: true
    });
    console.log(backup);

    // Get backup details
    const backupDetails = await client.storage.getBackup('backup_id');
    console.log(backupDetails);

    // Delete backup
    await client.storage.deleteBackup('backup_id');

    // Restore from backup
    const restore = await client.storage.restore({
      backup_id: 'backup_id',
      restore_recordings: true
    });
    console.log(restore);

    // Get restore status
    const restoreStatus = await client.storage.getRestoreStatus('restore_id');
    console.log(restoreStatus);
  } catch (error) {
    console.error(error);
  }
}

// System operations
async function systemOperations() {
  try {
    // Get system information
    const info = await client.system.getInfo();
    console.log(info);

    // Get system statistics
    const stats = await client.system.getStats();
    console.log(stats);

    // Get system configuration
    const config = await client.system.getConfig();
    console.log(config);

    // Update system configuration
    await client.system.updateConfig({
      detectors: {
        cpu: {
          type: 'cpu'
        }
      }
    }, true);

    // Restart the system
    await client.system.restart();

    // Get logs
    const logs = await client.system.getLogs('arkos', {
      start: 0,
      end: 100
    });
    console.log(logs);

    // Get version
    const version = await client.system.getVersion();
    console.log(version);

    // Get configuration schema
    const schema = await client.system.getConfigSchema();
    console.log(schema);

    // Get raw configuration
    const rawConfig = await client.system.getRawConfig();
    console.log(rawConfig);

    // Save configuration
    await client.system.saveConfig('config content', 'backup');

    // Get labels
    const labels = await client.system.getLabels('front_door');
    console.log(labels);

    // Get sub-labels
    const subLabels = await client.system.getSubLabels(1);
    console.log(subLabels);

    // Get recognized license plates
    const licensePlates = await client.system.getRecognizedLicensePlates(1);
    console.log(licensePlates);

    // Get timeline
    const timeline = await client.system.getTimeline('front_door', 100);
    console.log(timeline);

    // Get hourly timeline
    const hourlyTimeline = await client.system.getHourlyTimeline({
      cameras: 'front_door',
      timezone: 'America/New_York'
    });
    console.log(hourlyTimeline);
  } catch (error) {
    console.error(error);
  }
}
```

#### Error Handling

```javascript
const { ArkosClient, ArkosError, ArkosApiError, ArkosAuthError, ArkosRateLimitError, ArkosConnectionError, ArkosTimeoutError } = require('arkos-client');

const client = new ArkosClient({
  host: 'http://localhost:5000',
  apiKey: 'your_api_key'
});

async function handleErrors() {
  try {
    const cameras = await client.cameras.list();
    console.log(cameras);
  } catch (error) {
    if (error instanceof ArkosAuthError) {
      console.error(`Authentication error: ${error.message}`);
    } else if (error instanceof ArkosRateLimitError) {
      console.error(`Rate limit exceeded: ${error.message}, resets at ${error.resetTime}`);
    } else if (error instanceof ArkosApiError) {
      console.error(`API error: ${error.message}, status code: ${error.statusCode}, error code: ${error.errorCode}`);
    } else if (error instanceof ArkosConnectionError) {
      console.error(`Connection error: ${error.message}`);
    } else if (error instanceof ArkosTimeoutError) {
      console.error(`Timeout error: ${error.message}`);
    } else if (error instanceof ArkosError) {
      console.error(`Arkos error: ${error.message}`);
    } else {
      console.error(`Unknown error: ${error.message}`);
    }
  }
}
```

### Go

The official Go client library for Arkos AI.

#### Installation

```bash
go get github.com/arkosai/arkos-client-go
```

#### Usage

```go
package main

import (
	"fmt"
	"log"

	arkos "github.com/arkosai/arkos-client-go"
)

func main() {
	// Initialize the client
	client, err := arkos.NewClient(
		arkos.WithHost("http://localhost:5000"),
		arkos.WithAPIKey("your_api_key"),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Get a list of cameras
	cameras, err := client.Cameras.List(nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(cameras)

	// Get a specific camera
	camera, err := client.Cameras.Get("front_door")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(camera)

	// Get events
	events, err := client.Events.List(&arkos.EventListOptions{
		Camera: "front_door",
		After:  1620000000.0,
		Before: 1620001000.0,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(events)

	// Get recordings
	recordings, err := client.Recordings.List(&arkos.RecordingListOptions{
		Camera: "front_door",
		After:  1620000000.0,
		Before: 1620001000.0,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(recordings)

	// Get system information
	systemInfo, err := client.System.GetInfo()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(systemInfo)
}
```

## Community Libraries

In addition to the official client libraries, there are also community-maintained libraries for other programming languages:

- [Ruby Client](https://github.com/community/arkos-client-ruby)
- [PHP Client](https://github.com/community/arkos-client-php)
- [C# Client](https://github.com/community/arkos-client-csharp)

## Building Your Own Client

If you need to build your own client library, you can use the OpenAPI specification for the Arkos AI API:

```
/api/v1/openapi.json
```

This specification describes all the endpoints, request parameters, and response formats for the API.

## Authentication

All client libraries support the following authentication methods:

- API Key: A simple API key that is included in the `X-API-Key` header.
- JWT Token: A JWT token that is included in the `Authorization` header.

See the [Authentication](authentication.md) documentation for more details.

## Rate Limiting

The API has rate limits to prevent abuse. The client libraries handle rate limiting by backing off and retrying requests when rate limits are encountered.

See the [Rate Limiting](rate-limiting.md) documentation for more details.

## Error Handling

The client libraries provide error handling for API errors. Each library has its own error handling mechanism, but they all provide access to the error code, message, and details.

## Versioning

The client libraries follow semantic versioning and are versioned independently of the API. Each library supports a range of API versions.

See the [Versioning](versioning.md) documentation for more details.
