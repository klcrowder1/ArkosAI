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

# Initialize the client
client = ArkosClient(
    host="http://localhost:5000",
    api_key="your_api_key"
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

### JavaScript

The official JavaScript client library for Arkos AI.

#### Installation

```bash
npm install arkos-client
```

#### Usage

```javascript
const { ArkosClient } = require('arkos-client');

// Initialize the client
const client = new ArkosClient({
  host: 'http://localhost:5000',
  apiKey: 'your_api_key'
});

// Get a list of cameras
client.cameras.list()
  .then(cameras => {
    console.log(cameras);
  })
  .catch(error => {
    console.error(error);
  });

// Get a specific camera
client.cameras.get('front_door')
  .then(camera => {
    console.log(camera);
  })
  .catch(error => {
    console.error(error);
  });

// Get events
client.events.list({
  camera: 'front_door',
  after: 1620000000.0,
  before: 1620001000.0
})
  .then(events => {
    console.log(events);
  })
  .catch(error => {
    console.error(error);
  });

// Get recordings
client.recordings.list({
  camera: 'front_door',
  after: 1620000000.0,
  before: 1620001000.0
})
  .then(recordings => {
    console.log(recordings);
  })
  .catch(error => {
    console.error(error);
  });

// Get system information
client.system.getInfo()
  .then(systemInfo => {
    console.log(systemInfo);
  })
  .catch(error => {
    console.error(error);
  });
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
