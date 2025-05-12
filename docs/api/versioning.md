# API Versioning

This document describes the API versioning system in Arkos AI, including how to use different API versions, how to configure versioning, and best practices for API clients.

## Overview

Arkos AI implements a robust API versioning system to ensure backward compatibility while allowing the API to evolve over time. The API version is specified in the URL path, and clients can also specify the desired version using HTTP headers.

## API Version Format

API versions are specified using a simple format: `v<number>`, where `<number>` is the version number. For example:

- `v1`: Version 1
- `v2`: Version 2

## Specifying API Version

There are several ways to specify the API version:

### URL Path

The most common way to specify the API version is in the URL path:

```
https://<server-address>/api/v1/cameras
```

### Accept Header

You can also specify the API version using the `Accept` header with a media type parameter:

```
Accept: application/json; version=v1
```

### X-API-Version Header

Alternatively, you can use the `X-API-Version` header:

```
X-API-Version: v1
```

## Version Negotiation

If no version is specified, the API will use the default version configured in the system. The current default version is `v1`.

## Version Status

API versions can have different statuses:

- **Current**: The current stable version of the API
- **Beta**: A beta version that may have breaking changes
- **Deprecated**: A deprecated version that will be removed in the future
- **Sunset**: A version that is no longer supported

## Version Headers

The API includes several headers in responses to provide information about API versions:

- `X-API-Version`: The version used for the request
- `X-API-Current-Version`: The current stable version of the API
- `X-API-Supported-Versions`: A comma-separated list of supported API versions
- `X-API-Version-Status`: The status of the version used for the request

For deprecated versions, additional headers are included:

- `Sunset`: The date when the version will be sunset (ISO 8601 format)
- `Deprecation`: The version that deprecates this version
- `Link`: A link to the successor version

## Version Endpoints

The API provides an endpoint to get information about available versions:

```
GET /api/versions
```

Response:

```json
{
  "versions": {
    "v1": {
      "version": "v1",
      "status": "current",
      "release_date": "2025-04-12T00:00:00Z",
      "description": "Initial API version"
    },
    "v2": {
      "version": "v2",
      "status": "beta",
      "release_date": "2025-05-12T00:00:00Z",
      "description": "Beta API version with enhanced features"
    }
  },
  "current_version": "v1",
  "default_version": "v1"
}
```

## Configuration

API versioning can be configured in the Arkos AI configuration file:

```yaml
api:
  versioning:
    default_version: v1
    current_version: v1
    supported_versions:
      - v1
      - v2
    redirect_deprecated: true
    allow_version_override: true
```

### Configuration Options

- `default_version`: The default API version to use if no version is specified
- `current_version`: The current stable version of the API
- `supported_versions`: A list of supported API versions
- `redirect_deprecated`: Whether to redirect deprecated versions to the current version
- `allow_version_override`: Whether to allow version override via headers

## Best Practices for API Clients

### Specify API Version Explicitly

Always specify the API version explicitly in your requests to ensure consistent behavior, even if the default version changes:

```
GET /api/v1/cameras
```

### Check Version Headers

Check the version headers in responses to ensure you're using a supported version:

```
X-API-Version: v1
X-API-Current-Version: v1
X-API-Supported-Versions: v1,v2
X-API-Version-Status: current
```

### Handle Version Redirects

Be prepared to handle HTTP redirects (301 Moved Permanently) when using deprecated versions:

```
HTTP/1.1 301 Moved Permanently
Location: /api/v2/cameras
```

### Migrate to New Versions

When a version is deprecated, migrate to the new version as soon as possible to avoid disruption when the deprecated version is sunset.

## Version Lifecycle

1. **Beta**: New versions start in beta status, where they may have breaking changes
2. **Current**: When a beta version is stable, it becomes the current version
3. **Deprecated**: When a newer version becomes current, the previous version is deprecated
4. **Sunset**: After a deprecation period, the version is sunset and no longer supported

## Version Differences

### v1 (Current)

The initial API version with basic functionality.

### v2 (Beta)

Enhanced API version with additional features and improvements.

## Conclusion

API versioning ensures that Arkos AI can evolve while maintaining backward compatibility. By following the best practices in this document, API clients can ensure a smooth experience when interacting with the Arkos AI API.
