# Arkos Client

JavaScript client library for the Arkos AI API.

## Installation

```bash
npm install arkos-client
```

Or with yarn:

```bash
yarn add arkos-client
```

## Usage

### CommonJS

```javascript
const { ArkosClient } = require('arkos-client');

// Initialize the client with API key authentication
const client = new ArkosClient({
  host: 'http://localhost:5001',
  apiKey: 'your_api_key'
});
```

### ES Modules

```javascript
import { ArkosClient } from 'arkos-client';

// Initialize the client with API key authentication
const client = new ArkosClient({
  host: 'http://localhost:5001',
  apiKey: 'your_api_key'
});
```

### TypeScript

```typescript
import { ArkosClient } from 'arkos-client';

// Initialize the client with API key authentication
const client = new ArkosClient({
  host: 'http://localhost:5001',
  apiKey: 'your_api_key'
});
```

## Authentication

The client supports two authentication methods:

### API Key Authentication

```javascript
const client = new ArkosClient({
  host: 'http://localhost:5001',
  apiKey: 'your_api_key'
});
```

### JWT Authentication

```javascript
const client = new ArkosClient({
  host: 'http://localhost:5001',
  username: 'admin',
  password: 'password'
});
```

## Examples

### Working with Cameras

```javascript
// Get a list of cameras
const cameras = await client.cameras.list();

// Get a specific camera
const camera = await client.cameras.get('front_door');

// Create a new camera
const newCamera = await client.cameras.create({
  name: 'back_door',
  url: 'rtsp://example.com/back_door'
});

// Update an existing camera
await client.cameras.update('back_door', {
  url: 'rtsp://example.com/updated_back_door'
});

// Delete a camera
await client.cameras.delete('back_door');

// Get camera connection status
const status = await client.cameras.getConnectionStatus('front_door');

// Reset camera connection
await client.cameras.resetConnection('front_door');
```

### Working with Events

```javascript
// Get a list of events
const events = await client.events.list({
  camera: 'front_door',
  after: 1620000000.0,
  before: 1620001000.0
});

// Get a specific event
const event = await client.events.get('event_id');

// Create a new event
const newEvent = await client.events.create('front_door', 'person', {
  score: 0.9,
  duration: 30
});

// Delete an event
await client.events.delete('event_id');

// Get event snapshot
const snapshot = await client.events.getSnapshot('event_id');

// Get event clip
const clip = await client.events.getClip('event_id');
```

### Working with Recordings

```javascript
// Get a list of recordings
const recordings = await client.recordings.list('front_door', {
  after: 1620000000.0,
  before: 1620001000.0
});

// Get recording clip
const clip = await client.recordings.getClip('front_door', 1620000000.0, 1620001000.0);

// Get recording snapshot
const snapshot = await client.recordings.getSnapshot('front_door', 1620000500.0);

// Export recording
const export = await client.recordings.export('front_door', 1620000000.0, 1620001000.0, {
  name: 'Front Door Recording',
  playback: 'realtime'
});
```

### Working with System

```javascript
// Get system information
const info = await client.system.getInfo();

// Get system statistics
const stats = await client.system.getStats();

// Get system configuration
const config = await client.system.getConfig();

// Update system configuration
await client.system.updateConfig({
  detectors: {
    cpu: {
      type: 'cpu'
    }
  }
});

// Restart the system
await client.system.restart();

// Get system logs
const logs = await client.system.getLogs('arkos');

// Get version
const version = await client.system.getVersion();
```

## API Resources

The client provides access to the following API resources:

- `client.cameras` - Camera management
- `client.events` - Event detection and management
- `client.recordings` - Video recording management
- `client.health` - Health monitoring
- `client.storage` - Storage management
- `client.system` - System management

## Error Handling

The client throws errors for API errors:

```javascript
try {
  const cameras = await client.cameras.list();
} catch (error) {
  if (error.isArkosError) {
    console.error(`API error: ${error.message}`);
    console.error(`Status code: ${error.statusCode}`);
    console.error(`Error code: ${error.errorCode}`);
  } else {
    console.error(`Network error: ${error.message}`);
  }
}
```

## Rate Limiting

The client automatically handles rate limiting by backing off and retrying requests when rate limits are encountered.

## Development

### Building

```bash
npm run build
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
