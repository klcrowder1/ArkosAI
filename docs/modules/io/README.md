# IO Module

The IO module provides comprehensive input/output integration capabilities for Arkos AI, enabling interaction with physical devices and sensors through the LattePanda Sigma hardware and MQTT communication.

## Overview

The IO module is responsible for:

- Hardware integration with LattePanda GPIO
- MQTT communication for IoT integration
- Event-triggered actions
- Scheduling system for automated control
- Input/output state management

## Architecture

The IO module is structured as follows:

```
io/
├── hardware/            # Hardware integration components
│   ├── gpio/            # GPIO access
│   └── arduino/         # Arduino co-processor integration
├── mqtt/                # MQTT communication components
├── triggers/            # Event trigger components
├── scheduler/           # Scheduling components
├── api/                 # API endpoints
└── service/             # Core service functionality
```

### Key Components

1. **Hardware Manager**: Manages hardware interfaces like GPIO and Arduino
2. **MQTT Client**: Handles MQTT communication for input/output state
3. **Trigger Manager**: Manages event-triggered actions
4. **Scheduler**: Handles time-based and conditional scheduling
5. **State Manager**: Manages the state of inputs and outputs

## Configuration

The IO module is configured through the main configuration file. Here's an example configuration:

```yaml
io:
  # Global IO configuration
  enabled: true
  
  # Hardware configuration
  hardware:
    enabled: true
    
    # GPIO configuration
    gpio:
      enabled: true
      inputs:
        - pin: 17
          name: "motion_sensor"
          type: "digital"
          pull: "up"
          invert: true
        - pin: 27
          name: "door_sensor"
          type: "digital"
          pull: "up"
          invert: true
      
      outputs:
        - pin: 18
          name: "alarm_siren"
          type: "digital"
          initial_state: "off"
        - pin: 22
          name: "perimeter_lights"
          type: "digital"
          initial_state: "off"
    
    # Arduino co-processor configuration
    arduino:
      enabled: true
      port: "/dev/ttyACM0"
      baud_rate: 115200
      inputs:
        - pin: "A0"
          name: "temperature_sensor"
          type: "analog"
        - pin: "A1"
          name: "light_sensor"
          type: "analog"
      
      outputs:
        - pin: 9
          name: "fan_control"
          type: "pwm"
          initial_state: 0
  
  # MQTT configuration
  mqtt:
    enabled: true
    publish:
      inputs: true
      input_prefix: "arkos/io/input"
      status_interval: 60  # seconds
      retain_states: true
    subscribe:
      output_prefix: "arkos/io/output"
      config_prefix: "arkos/io/config"
  
  # Triggers configuration
  triggers:
    enabled: true
    definitions:
      - name: "Front Door Alert"
        event:
          type: "detection"
          source: "front_door_camera"
          object: ["person"]
          zone: "restricted_area"
        actions:
          - output: "alarm_siren"
            state: "on"
            duration: 60  # seconds
          - output: "perimeter_lights"
            state: "on"
            duration: 300  # seconds
      
      - name: "Temperature Control"
        event:
          type: "threshold"
          source: "temperature_sensor"
          condition: "above"
          value: 30  # degrees
        actions:
          - output: "fan_control"
            state: 255  # full speed
            duration: 0  # until reset
  
  # Scheduler configuration
  scheduler:
    enabled: true
    schedules:
      - name: "Night Lights"
        type: "time"
        time: "19:00:00"
        days: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        actions:
          - output: "perimeter_lights"
            state: "on"
      
      - name: "Morning Lights Off"
        type: "time"
        time: "07:00:00"
        days: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        actions:
          - output: "perimeter_lights"
            state: "off"
      
      - name: "Conditional Fan Control"
        type: "condition"
        condition:
          source: "temperature_sensor"
          operator: ">"
          value: 28
        actions:
          - output: "fan_control"
            state: 200  # 80% speed
```

## API

The IO module provides the following API endpoints:

### Hardware API

- `GET /api/io/hardware/inputs`: List all hardware inputs
- `GET /api/io/hardware/inputs/{input_id}`: Get input details and state
- `GET /api/io/hardware/outputs`: List all hardware outputs
- `GET /api/io/hardware/outputs/{output_id}`: Get output details and state
- `PUT /api/io/hardware/outputs/{output_id}`: Set output state

### MQTT API

- `GET /api/io/mqtt/status`: Get MQTT connection status
- `GET /api/io/mqtt/topics`: List all MQTT topics
- `POST /api/io/mqtt/publish`: Publish a message to an MQTT topic

### Triggers API

- `GET /api/io/triggers`: List all triggers
- `GET /api/io/triggers/{trigger_id}`: Get trigger details
- `POST /api/io/triggers`: Create a new trigger
- `PUT /api/io/triggers/{trigger_id}`: Update a trigger
- `DELETE /api/io/triggers/{trigger_id}`: Delete a trigger
- `POST /api/io/triggers/{trigger_id}/test`: Test a trigger

### Scheduler API

- `GET /api/io/scheduler/schedules`: List all schedules
- `GET /api/io/scheduler/schedules/{schedule_id}`: Get schedule details
- `POST /api/io/scheduler/schedules`: Create a new schedule
- `PUT /api/io/scheduler/schedules/{schedule_id}`: Update a schedule
- `DELETE /api/io/scheduler/schedules/{schedule_id}`: Delete a schedule
- `POST /api/io/scheduler/schedules/{schedule_id}/run`: Run a schedule manually

## Integration with Other Modules

The IO module integrates with other Arkos AI modules through the following interfaces:

### Core Module

- Receives events from the Core module for triggering actions
- Provides input states to the Core module
- Integrates with the Core module's event system

### Analytics Module

- Receives analytics events for triggering actions
- Provides input data for analytics processing

### Audio Module

- Receives audio events for triggering actions
- Controls audio output devices

### IoT Module

- Provides a bridge between IoT devices and the IO system
- Shares MQTT broker for communication

### UI Module

- Provides IO status information for the dashboard
- Provides controls for manual IO operation

## Dependencies

The IO module depends on:

- GPIO libraries for hardware access
- PySerial for Arduino communication
- Paho MQTT for MQTT communication
- APScheduler for scheduling

## Examples

### Controlling Outputs

```python
from arkos.io.hardware import output_manager

# Turn on an output
output_manager.set_state("perimeter_lights", "on")

# Set a PWM output
output_manager.set_state("fan_control", 128)  # 50% duty cycle

# Turn on an output for a duration
output_manager.set_state("alarm_siren", "on", duration=60)  # 60 seconds
```

### Reading Inputs

```python
from arkos.io.hardware import input_manager

# Get the state of an input
state = input_manager.get_state("motion_sensor")
print(f"Motion sensor state: {state}")

# Get the value of an analog input
value = input_manager.get_value("temperature_sensor")
print(f"Temperature sensor value: {value}")

# Register a callback for input changes
def on_motion_detected(input_id, state):
    print(f"Motion detected: {input_id} = {state}")

input_manager.register_callback("motion_sensor", on_motion_detected)
```

### Managing Triggers

```python
from arkos.io.triggers import trigger_manager

# Create a new trigger
trigger = {
    "name": "Motion Light",
    "event": {
        "type": "input",
        "source": "motion_sensor",
        "state": "on"
    },
    "actions": [
        {
            "output": "perimeter_lights",
            "state": "on",
            "duration": 300  # 5 minutes
        }
    ]
}

trigger_id = trigger_manager.create_trigger(trigger)
print(f"Created trigger: {trigger_id}")

# Test a trigger
trigger_manager.test_trigger(trigger_id)
```

### Managing Schedules

```python
from arkos.io.scheduler import scheduler

# Create a new schedule
schedule = {
    "name": "Evening Lights",
    "type": "time",
    "time": "18:30:00",
    "days": ["mon", "tue", "wed", "thu", "fri"],
    "actions": [
        {
            "output": "perimeter_lights",
            "state": "on"
        }
    ]
}

schedule_id = scheduler.create_schedule(schedule)
print(f"Created schedule: {schedule_id}")

# Run a schedule manually
scheduler.run_schedule(schedule_id)
```

### MQTT Integration

```python
from arkos.io.mqtt import mqtt_client

# Publish a message
mqtt_client.publish("arkos/io/output/perimeter_lights", "on")

# Subscribe to a topic
def on_message(topic, payload):
    print(f"Received message on {topic}: {payload}")

mqtt_client.subscribe("arkos/io/input/motion_sensor", on_message)
