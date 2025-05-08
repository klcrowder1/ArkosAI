# Docker Development Environment

This document describes the Docker-based development environment for Arkos AI, including container configuration, development workflow, and testing procedures.

## Overview

Arkos AI uses Docker to provide a consistent development environment across different platforms. The Docker environment consists of multiple containers that work together to provide a complete development environment for the system.

## Prerequisites

Before setting up the Docker development environment, ensure you have the following prerequisites installed:

- **Docker**: Version 20.10.0 or later
- **Docker Compose**: Version 2.0.0 or later
- **Git**: For version control
- **Visual Studio Code** (recommended): With the Remote - Containers extension

## Container Architecture

The Docker development environment consists of the following containers:

```
arkos-dev/
├── arkos-core          # Core NVR functionality
├── arkos-web           # Web frontend with hot reloading
├── arkos-db            # Database (SQLite with extensions)
├── arkos-mqtt          # MQTT broker
└── arkos-turn          # TURN server
```

### Container Details

#### arkos-core

The `arkos-core` container provides the core NVR functionality:

- **Base Image**: Python 3.9
- **Exposed Ports**: 5001 (API)
- **Volumes**:
  - `./:/app`: Mount the project directory
  - `./data:/data`: Mount the data directory
- **Environment Variables**:
  - `PYTHONPATH=/app`
  - `DEBUG=true`
  - `LOG_LEVEL=debug`

#### arkos-web

The `arkos-web` container provides the web frontend with hot reloading:

- **Base Image**: Node 16
- **Exposed Ports**: 5000 (Web UI)
- **Volumes**:
  - `./web:/app`: Mount the web directory
- **Environment Variables**:
  - `NODE_ENV=development`
  - `VITE_API_URL=http://localhost:5001`

#### arkos-db

The `arkos-db` container provides the database:

- **Base Image**: Custom SQLite with vector extensions
- **Volumes**:
  - `./data/db:/data`: Mount the database directory

#### arkos-mqtt

The `arkos-mqtt` container provides the MQTT broker:

- **Base Image**: Eclipse Mosquitto
- **Exposed Ports**: 1883 (MQTT), 9001 (WebSockets)
- **Volumes**:
  - `./config/mosquitto:/mosquitto/config`: Mount the MQTT configuration

#### arkos-turn

The `arkos-turn` container provides the TURN server:

- **Base Image**: Coturn
- **Exposed Ports**: 3478 (TURN)
- **Volumes**:
  - `./config/coturn:/etc/coturn`: Mount the TURN configuration

## Docker Compose Configuration

The Docker Compose configuration is defined in `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  arkos-core:
    build:
      context: .
      dockerfile: docker/dev/core.Dockerfile
    ports:
      - "5001:5001"
    volumes:
      - ./:/app
      - ./data:/data
    environment:
      - PYTHONPATH=/app
      - DEBUG=true
      - LOG_LEVEL=debug
      - DB_PATH=/data/db/arkos.db
      - MQTT_HOST=arkos-mqtt
      - MQTT_PORT=1883
    depends_on:
      - arkos-db
      - arkos-mqtt
    restart: unless-stopped
    
  arkos-web:
    build:
      context: ./web
      dockerfile: ../docker/dev/web.Dockerfile
    ports:
      - "5000:5000"
    volumes:
      - ./web:/app
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:5001
    restart: unless-stopped
    
  arkos-db:
    build:
      context: .
      dockerfile: docker/dev/db.Dockerfile
    volumes:
      - ./data/db:/data
    restart: unless-stopped
    
  arkos-mqtt:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./config/mosquitto:/mosquitto/config
    restart: unless-stopped
    
  arkos-turn:
    image: coturn/coturn:latest
    ports:
      - "3478:3478"
      - "3478:3478/udp"
    volumes:
      - ./config/coturn:/etc/coturn
    restart: unless-stopped
```

## Development Workflow

### Starting the Development Environment

To start the development environment:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This will build and start all the containers in the background.

### Viewing Logs

To view the logs from all containers:

```bash
docker-compose -f docker-compose.dev.yml logs -f
```

To view logs from a specific container:

```bash
docker-compose -f docker-compose.dev.yml logs -f arkos-core
```

### Stopping the Development Environment

To stop the development environment:

```bash
docker-compose -f docker-compose.dev.yml down
```

### Rebuilding Containers

If you make changes to the Dockerfiles or dependencies, you may need to rebuild the containers:

```bash
docker-compose -f docker-compose.dev.yml build
```

To rebuild a specific container:

```bash
docker-compose -f docker-compose.dev.yml build arkos-core
```

### Executing Commands in Containers

To execute commands in a container:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core bash
```

This will open a bash shell in the `arkos-core` container.

### Running Tests

To run tests in the `arkos-core` container:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core pytest
```

### Hot Reloading

The development environment is configured for hot reloading:

- **arkos-core**: Python code changes are automatically detected and the server is restarted
- **arkos-web**: JavaScript/TypeScript code changes are automatically detected and the browser is refreshed

## Container Configuration

### Dockerfile: arkos-core

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Install development tools
RUN pip install --no-cache-dir pytest pytest-cov black isort flake8 debugpy

# Set environment variables
ENV PYTHONPATH=/app
ENV DEBUG=true
ENV LOG_LEVEL=debug

# Expose ports
EXPOSE 5001

# Start the development server with hot reloading
CMD ["python", "-m", "uvicorn", "frigate.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
```

### Dockerfile: arkos-web

```dockerfile
FROM node:16-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Set environment variables
ENV NODE_ENV=development

# Expose ports
EXPOSE 5000

# Start the development server with hot reloading
CMD ["npm", "run", "dev"]
```

### Dockerfile: arkos-db

```dockerfile
FROM alpine:3.15

WORKDIR /data

# Install SQLite and build dependencies
RUN apk add --no-cache \
    sqlite \
    build-base \
    git \
    cmake \
    && rm -rf /var/cache/apk/*

# Clone and build SQLite vector extension
RUN git clone https://github.com/asg017/sqlite-vss.git /tmp/sqlite-vss \
    && cd /tmp/sqlite-vss \
    && cmake -B build \
    && cmake --build build \
    && cp build/vss0.so /usr/lib/ \
    && rm -rf /tmp/sqlite-vss

# Create a script to initialize the database
COPY docker/dev/init-db.sh /init-db.sh
RUN chmod +x /init-db.sh

# Run the initialization script
CMD ["/init-db.sh"]
```

## Configuration Files

### MQTT Configuration

Create a file at `config/mosquitto/mosquitto.conf`:

```
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
```

### TURN Configuration

Create a file at `config/coturn/turnserver.conf`:

```
listening-port=3478
fingerprint
lt-cred-mech
use-auth-secret
static-auth-secret=arkos-dev-secret
realm=arkos.local
total-quota=100
stale-nonce=600
```

## Development Tools

### Visual Studio Code Integration

For the best development experience, use Visual Studio Code with the Remote - Containers extension:

1. Install the Remote - Containers extension
2. Open the Arkos AI project folder in VS Code
3. Click the "Reopen in Container" button in the bottom right corner
4. Select the container you want to develop in (e.g., `arkos-core`)

This will open VS Code connected to the selected container, with all the necessary extensions and configurations.

### Debugging

The `arkos-core` container is configured for debugging with VS Code:

1. Create a `.vscode/launch.json` file:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

2. Start the debugger in the container:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn frigate.api.fastapi_app:app --host 0.0.0.0 --port 5001
```

3. Start the debugging session in VS Code

### Database Access

To access the SQLite database:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-db sqlite3 /data/arkos.db
```

### MQTT Client

To connect to the MQTT broker:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-mqtt mosquitto_sub -t 'arkos/#' -v
```

## Testing Environment

The Docker development environment includes a testing environment for running tests:

### Unit Tests

To run unit tests:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core pytest tests/unit
```

### Integration Tests

To run integration tests:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core pytest tests/integration
```

### System Tests

To run system tests:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core pytest tests/system
```

### Coverage Reports

To generate coverage reports:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core pytest --cov=arkos --cov-report=html
```

The coverage report will be available in the `htmlcov` directory.

## Simulated Hardware Environment

For testing hardware-dependent features, the Docker environment includes a simulated hardware environment:

### GPIO Simulation

The `arkos-core` container includes a GPIO simulation library that emulates the GPIO pins on the LattePanda Sigma hardware:

```python
from arkos.io.hardware.gpio_simulator import GPIOSimulator

# Create a GPIO simulator
gpio = GPIOSimulator()

# Set up a pin as output
gpio.setup(18, gpio.OUT)

# Set the pin high
gpio.output(18, gpio.HIGH)

# Read the pin state
state = gpio.input(18)
```

### Camera Simulation

The Docker environment includes a camera simulation tool that generates simulated camera feeds:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -m arkos.tools.camera_simulator --camera front_door --fps 10
```

This will generate a simulated camera feed for the `front_door` camera at 10 FPS.

## Performance Testing

The Docker environment includes tools for performance testing:

### CPU Profiling

To profile CPU usage:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -m cProfile -o profile.out -m arkos.core
```

To analyze the profile:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -c "import pstats; p = pstats.Stats('profile.out'); p.sort_stats('cumulative').print_stats(30)"
```

### Memory Profiling

To profile memory usage:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -m memory_profiler -o memory.out -m arkos.core
```

To analyze the profile:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-core python -c "import memory_profiler; memory_profiler.show_results('memory.out')"
```

## Troubleshooting

### Container Fails to Start

If a container fails to start, check the logs:

```bash
docker-compose -f docker-compose.dev.yml logs arkos-core
```

### Port Conflicts

If you encounter port conflicts, you can change the port mapping in the `docker-compose.dev.yml` file:

```yaml
ports:
  - "5002:5001"  # Map container port 5001 to host port 5002
```

### Volume Mount Issues

If you encounter issues with volume mounts, ensure that the paths in the `docker-compose.dev.yml` file are correct for your system.

### Database Initialization Issues

If the database fails to initialize, you can manually initialize it:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-db sqlite3 /data/arkos.db < schema.sql
```

### MQTT Connection Issues

If you encounter issues connecting to the MQTT broker, check the MQTT configuration:

```bash
docker-compose -f docker-compose.dev.yml exec arkos-mqtt cat /mosquitto/config/mosquitto.conf
```

## Conclusion

The Docker development environment provides a consistent and reproducible environment for developing Arkos AI. By using Docker, developers can ensure that their development environment matches the production environment, reducing the likelihood of environment-specific issues.
