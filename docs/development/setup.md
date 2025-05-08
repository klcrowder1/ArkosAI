# Development Environment Setup

This guide provides instructions for setting up a development environment for Arkos AI.

## Prerequisites

Before setting up the development environment, ensure you have the following prerequisites installed:

- **Git**: For version control
- **Docker**: For containerized development and testing
- **Docker Compose**: For managing multi-container Docker applications
- **Python 3.9+**: For development and testing
- **Node.js 16+**: For frontend development
- **Visual Studio Code** (recommended): With the following extensions:
  - Python
  - Docker
  - ESLint
  - Prettier
  - YAML

## Repository Setup

1. Clone the repository:

```bash
git clone https://github.com/your-organization/arkos-ai.git
cd arkos-ai
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

4. Install frontend dependencies:

```bash
cd web
npm install
cd ..
```

## Docker Development Environment

Arkos AI uses Docker for development and testing to ensure consistency across different environments.

### Building the Development Containers

```bash
docker-compose -f docker-compose.dev.yml build
```

### Starting the Development Environment

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This will start the following containers:
- **arkos-core**: The core NVR functionality
- **arkos-web**: The web frontend with hot reloading
- **arkos-db**: The database
- **arkos-mqtt**: The MQTT broker
- **arkos-turn**: The TURN server

### Accessing the Development Environment

- Web UI: http://localhost:5000
- API: http://localhost:5001/api
- MQTT: localhost:1883
- TURN: localhost:3478

### Stopping the Development Environment

```bash
docker-compose -f docker-compose.dev.yml down
```

## LattePanda Development

For development on the LattePanda Sigma hardware:

1. Install Ubuntu Server on the LattePanda
2. Install Docker and Docker Compose
3. Clone the repository
4. Build and run the containers

### GPIO Access on LattePanda

To access GPIO pins on the LattePanda:

1. Install the required libraries:

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
pip install pyserial gpiozero
```

2. Add your user to the dialout and gpio groups:

```bash
sudo usermod -a -G dialout,gpio $USER
```

3. Reboot the LattePanda:

```bash
sudo reboot
```

## Development Workflow

### Code Structure

The Arkos AI codebase follows a modular structure:

```
arkos-ai/
├── core/               # Core NVR functionality
├── analytics/          # Enhanced video & audio analytics
├── health/             # Camera health monitoring
├── audio/              # Two-way audio capabilities
├── io/                 # IO integration module
├── iot/                # IoT device integration
├── turn/               # TURN server integration
├── notify/             # Webhook notification system
├── api/                # API server with extended endpoints
└── ui/                 # Enhanced user interface
```

### Branch Strategy

- **main**: Stable release branch
- **dev**: Development branch
- **feature/xxx**: Feature branches
- **bugfix/xxx**: Bug fix branches

### Development Cycle

1. Create a feature branch from dev:

```bash
git checkout dev
git pull
git checkout -b feature/my-feature
```

2. Implement your changes
3. Write tests for your changes
4. Run the tests:

```bash
pytest
```

5. Commit your changes:

```bash
git add .
git commit -m "feat: add my feature"
```

6. Push your changes:

```bash
git push origin feature/my-feature
```

7. Create a pull request to the dev branch

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_core.py

# Run tests with coverage
pytest --cov=arkos
```

### Testing on LattePanda

To test on the LattePanda hardware:

1. Deploy the application to the LattePanda:

```bash
./scripts/deploy.sh lattepanda
```

2. Run the hardware tests:

```bash
./scripts/run_hardware_tests.sh
```

## Debugging

### Debugging the Core Module

```bash
# Run the core module with debug logging
python -m arkos.core --debug

# Attach a debugger
python -m debugpy --listen 5678 --wait-for-client -m arkos.core
```

### Debugging the Web Frontend

```bash
# Start the web frontend in development mode
cd web
npm run dev
```

## Documentation

### Building the Documentation

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build the documentation
cd docs
mkdocs build

# Serve the documentation locally
mkdocs serve
```

## Continuous Integration

Arkos AI uses GitHub Actions for continuous integration:

- **Lint**: Runs linting checks on the code
- **Test**: Runs the test suite
- **Build**: Builds the Docker images
- **Docs**: Builds the documentation

## Troubleshooting

### Common Issues

#### Docker Permission Issues

If you encounter permission issues with Docker:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Python Virtual Environment Issues

If you encounter issues with the Python virtual environment:

```bash
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

#### Node.js Dependency Issues

If you encounter issues with Node.js dependencies:

```bash
cd web
rm -rf node_modules
npm install
```

## Getting Help

If you need help with the development environment:

- Check the [troubleshooting guide](./troubleshooting.md)
- Open an issue on GitHub
- Contact the development team
