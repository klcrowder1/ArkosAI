# Arkos AI Modules

This directory contains documentation for each of the Arkos AI modules. Each module is designed to be self-contained with well-defined interfaces for interaction with other modules.

## Module Structure

Each module follows a consistent structure:

```
module_name/
├── __init__.py          # Module initialization
├── config.py            # Module configuration
├── models.py            # Data models
├── api.py               # API endpoints
├── service.py           # Core service functionality
├── utils.py             # Utility functions
└── tests/               # Unit and integration tests
```

## Module Documentation

Each module's documentation includes:

1. **Overview**: A high-level description of the module's purpose and functionality
2. **Architecture**: The internal architecture of the module
3. **Configuration**: Configuration options and examples
4. **API**: The module's API for interaction with other modules
5. **Dependencies**: Other modules or external dependencies
6. **Examples**: Usage examples

## Available Modules

- [Core](./core/README.md): Core NVR functionality (from Frigate)
- [Analytics](./analytics/README.md): Enhanced video & audio analytics
- [Health](./health/README.md): Camera health monitoring
- [Audio](./audio/README.md): Two-way audio capabilities
- [IO](./io/README.md): IO integration module
- [IoT](./iot/README.md): IoT device integration
- [TURN](./turn/README.md): TURN server integration
- [Notify](./notify/README.md): Webhook notification system
- [API](./api/README.md): API server with extended endpoints
- [UI](./ui/README.md): Enhanced user interface

## Module Interactions

Modules interact with each other through well-defined interfaces:

1. **Direct API Calls**: Modules can call each other's API functions directly
2. **Event System**: Modules can publish and subscribe to events
3. **Database**: Modules can share data through the database
4. **Configuration**: Modules can be configured to work together

## Adding New Modules

To add a new module:

1. Create a new directory in the `arkos-ai` package
2. Follow the module structure outlined above
3. Implement the required interfaces
4. Add documentation in this directory
5. Update the module list in this README
