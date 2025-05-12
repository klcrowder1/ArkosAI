# Arkos Client

Python client library for the Arkos AI API.

## Installation

```bash
pip install arkos-client
```

## Usage

```python
from arkos_client import ArkosClient

# Initialize the client with API key authentication
client = ArkosClient(
    host="http://localhost:5001",
    api_key="your_api_key"
)

# Or initialize with JWT authentication
client = ArkosClient(
    host="http://localhost:5001",
    username="admin",
    password="password"
)

# Get a list of cameras
cameras = client.cameras.list()

# Get a specific camera
camera = client.cameras.get("front_door")

# Get events
events = client.events.list(
    camera="front_door",
    after=1620000000.0,
    before=1620001000.0
)

# Get recordings
recordings = client.recordings.list(
    camera="front_door",
    after=1620000000.0,
    before=1620001000.0
)

# Get system information
system_info = client.system.get_info()
```

## Authentication

The client supports two authentication methods:

### API Key Authentication

```python
client = ArkosClient(
    host="http://localhost:5001",
    api_key="your_api_key"
)
```

### JWT Authentication

```python
client = ArkosClient(
    host="http://localhost:5001",
    username="admin",
    password="password"
)
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

The client raises exceptions for API errors:

```python
from arkos_client.exceptions import ArkosApiError, ArkosAuthError

try:
    cameras = client.cameras.list()
except ArkosAuthError:
    print("Authentication failed")
except ArkosApiError as e:
    print(f"API error: {e}")
```

## Rate Limiting

The client automatically handles rate limiting by backing off and retrying requests when rate limits are encountered.

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Building Documentation

```bash
pip install -e ".[docs]"
cd docs
make html
