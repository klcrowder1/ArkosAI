<p align="center">
  <h1 align="center">Arkos AI</h1>
  <p align="center">Advanced Network Video Recorder with AI-powered Analytics</p>
</p>

# Arkos AI

Arkos AI is an advanced, customizable Network Video Recorder (NVR) system based on a fork of Frigate NVR, designed to provide comprehensive security, monitoring, and analytics capabilities. The system is optimized for LattePanda Sigma hardware and implements numerous enhanced features beyond standard NVR functionality.

## Key Features

- **Enhanced Video & Audio Analytics**: Advanced object detection, activity recognition, and audio event detection
- **Camera Health Monitoring**: Connectivity monitoring, dirty lens detection, and scene change detection
- **IO System with MQTT Integration**: Hardware integration, MQTT communications, and event-triggered actions
- **Event Clip Generation & Summarization**: Configurable clip generation with AI-powered summarization
- **Day in the Life Analytics**: Temporal pattern analysis, spatial activity mapping, and behavioral analytics
- **Timeline Report System**: Event correlation, interactive timeline interface, and video compilation
- **Situational Awareness**: Enhanced event & alarm model, monitoring center interface, and context enhancement
- **TURN Server & Remote Access**: NAT traversal, WebRTC support, and secure remote access
- **IoT Integration**: Support for ZigBee, Z-Wave, WiFi, and Bluetooth devices
- **Webhook Notification System**: Customizable event triggers and notification services

## Documentation

Comprehensive documentation is available in the [docs](./docs) directory:

- [Architecture Documentation](./docs/architecture/overview.md)
- [Module Documentation](./docs/modules)
- [API Documentation](./docs/api/overview.md)
- [Development Guide](./docs/development/setup.md)
- [Deployment Guide](./docs/deployment/installation.md)
- [User Guide](./docs/user/getting-started.md)

## Hardware Requirements

Arkos AI is optimized for the LattePanda Sigma hardware platform:
- Intel Core processor
- 16GB RAM
- Primary M.2 SSD for OS/software
- External storage for video recording
- Built-in IO capabilities for sensor integration
- Ethernet connectivity

## Getting Started

See the [Getting Started Guide](./docs/user/getting-started.md) for installation and setup instructions.

## Development

For development setup and contribution guidelines, see the [Development Guide](./docs/development/setup.md).

## License

This project is based on Frigate NVR and maintains the same license. See the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- [Frigate NVR](https://github.com/blakeblackshear/frigate) - The foundation for this project
- All contributors to the Frigate NVR project
