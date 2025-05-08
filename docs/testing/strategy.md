# Testing Strategy

This document outlines the testing strategy for the Arkos AI project, including the types of tests, testing frameworks, and testing processes.

## Testing Philosophy

The Arkos AI testing philosophy is based on the following principles:

1. **Test-Driven Development**: Write tests before implementing features
2. **Comprehensive Coverage**: Test all aspects of the system
3. **Automation**: Automate testing as much as possible
4. **Continuous Integration**: Run tests on every commit
5. **Hardware Validation**: Test on actual hardware for production use cases

## Types of Tests

### Unit Tests

Unit tests verify that individual components work as expected in isolation. They focus on testing a single function, class, or module.

**Characteristics**:
- Fast execution
- No external dependencies
- Test a single unit of code
- High coverage

**Examples**:
- Testing a utility function
- Testing a class method
- Testing a React component

### Integration Tests

Integration tests verify that multiple components work together correctly. They focus on testing the interactions between components.

**Characteristics**:
- May involve external dependencies
- Test multiple components together
- Focus on interfaces between components
- Medium coverage

**Examples**:
- Testing API endpoints
- Testing database interactions
- Testing module interactions

### System Tests

System tests verify that the entire system works as expected. They focus on testing the system as a whole.

**Characteristics**:
- Involve the entire system
- May require a complete environment
- Test end-to-end functionality
- Lower coverage

**Examples**:
- Testing the complete video processing pipeline
- Testing the event detection and notification system
- Testing the web interface

### Hardware Tests

Hardware tests verify that the system works correctly on the target hardware. They focus on testing hardware-specific functionality.

**Characteristics**:
- Require specific hardware
- Test hardware interactions
- Focus on performance and reliability
- Limited coverage

**Examples**:
- Testing GPIO interactions on LattePanda
- Testing camera integration
- Testing hardware acceleration

## Testing Frameworks

### Python Testing

- **pytest**: Primary testing framework for Python code
- **unittest.mock**: For mocking dependencies
- **pytest-cov**: For measuring test coverage
- **pytest-asyncio**: For testing asynchronous code

### JavaScript/TypeScript Testing

- **Jest**: Primary testing framework for JavaScript/TypeScript code
- **React Testing Library**: For testing React components
- **Cypress**: For end-to-end testing of the web interface
- **MSW (Mock Service Worker)**: For mocking API requests

### Hardware Testing

- **Custom test harness**: For testing hardware interactions
- **Performance monitoring tools**: For measuring system performance
- **Stress testing tools**: For testing system stability

## Test Organization

Tests are organized to mirror the structure of the codebase:

```
arkos-ai/
├── tests/
│   ├── unit/                 # Unit tests
│   │   ├── core/             # Core module tests
│   │   ├── analytics/        # Analytics module tests
│   │   ├── health/           # Health module tests
│   │   └── ...
│   ├── integration/          # Integration tests
│   │   ├── api/              # API tests
│   │   ├── database/         # Database tests
│   │   └── ...
│   ├── system/               # System tests
│   │   ├── video/            # Video processing tests
│   │   ├── events/           # Event processing tests
│   │   └── ...
│   └── hardware/             # Hardware tests
│       ├── gpio/             # GPIO tests
│       ├── camera/           # Camera tests
│       └── ...
└── web/
    ├── src/
    │   └── ...
    └── tests/                # Frontend tests
        ├── unit/             # Frontend unit tests
        ├── integration/      # Frontend integration tests
        └── e2e/              # End-to-end tests
```

## Test Coverage

The goal is to maintain high test coverage across the codebase:

- **Unit tests**: > 90% coverage
- **Integration tests**: > 80% coverage
- **System tests**: Key functionality covered
- **Hardware tests**: All hardware interactions covered

Coverage is measured using pytest-cov for Python code and Jest for JavaScript/TypeScript code.

## Testing Process

### Local Development

Developers should follow this process during local development:

1. Write tests for the feature or bug fix
2. Implement the feature or bug fix
3. Run the tests locally to ensure they pass
4. Measure test coverage to ensure adequate coverage
5. Submit a pull request

### Continuous Integration

The CI pipeline includes the following testing stages:

1. **Lint**: Run linting checks on the code
2. **Unit Tests**: Run unit tests for all modules
3. **Integration Tests**: Run integration tests
4. **System Tests**: Run system tests
5. **Coverage**: Measure and report test coverage

### Hardware Testing

Hardware testing is performed on the LattePanda Sigma hardware:

1. Deploy the application to the LattePanda
2. Run the hardware test suite
3. Monitor system performance and stability
4. Report any issues or performance concerns

## Test Environment

### Development Environment

The development environment for testing includes:

- Docker containers for isolated testing
- Mock services for external dependencies
- Test databases for database testing
- Mock hardware for hardware testing

### CI Environment

The CI environment for testing includes:

- GitHub Actions runners
- Docker containers for isolated testing
- Mock services for external dependencies
- Test databases for database testing

### Hardware Environment

The hardware environment for testing includes:

- LattePanda Sigma hardware
- Connected cameras
- GPIO devices
- Network infrastructure

## Test Data

### Test Fixtures

Test fixtures provide consistent data for tests:

- Camera frames for video processing tests
- Events for event processing tests
- Configuration for system tests
- Mock hardware responses for hardware tests

### Test Generators

Test generators create dynamic test data:

- Random camera frames
- Simulated events
- Varied configurations
- Simulated hardware responses

## Mocking

### External Dependencies

External dependencies are mocked to isolate tests:

- Camera feeds
- MQTT broker
- External APIs
- Hardware devices

### Internal Dependencies

Internal dependencies may be mocked for unit tests:

- Database access
- File system access
- Network access
- Hardware access

## Test Documentation

### Test Requirements

Test requirements are documented for each feature:

- What should be tested
- Expected behavior
- Edge cases
- Performance requirements

### Test Reports

Test reports are generated for each test run:

- Test results
- Coverage reports
- Performance metrics
- Hardware test results

## Troubleshooting Tests

### Common Issues

- **Flaky tests**: Tests that fail intermittently
- **Slow tests**: Tests that take too long to run
- **Resource leaks**: Tests that don't clean up resources
- **Hardware dependencies**: Tests that require specific hardware

### Debugging Techniques

- **Logging**: Enable detailed logging during tests
- **Debugging**: Use debuggers to step through test execution
- **Isolation**: Run tests in isolation to identify issues
- **Mocking**: Mock problematic dependencies

## Example Tests

### Python Unit Test Example

```python
import pytest
from arkos.core.utils import parse_timestamp

def test_parse_timestamp():
    # Test valid timestamp
    assert parse_timestamp("2023-01-01T12:00:00Z") == 1672574400.0
    
    # Test invalid timestamp
    with pytest.raises(ValueError):
        parse_timestamp("invalid")
    
    # Test None input
    with pytest.raises(TypeError):
        parse_timestamp(None)
```

### Python Integration Test Example

```python
import pytest
from arkos.api.client import ApiClient
from arkos.core.models import Camera

@pytest.fixture
def api_client():
    client = ApiClient("http://localhost:5001")
    yield client
    client.close()

def test_get_cameras(api_client):
    # Get cameras from API
    cameras = api_client.get_cameras()
    
    # Verify response
    assert isinstance(cameras, list)
    assert len(cameras) > 0
    
    # Verify camera properties
    camera = cameras[0]
    assert isinstance(camera, Camera)
    assert camera.id is not None
    assert camera.name is not None
```

### JavaScript Unit Test Example

```javascript
import { render, screen } from '@testing-library/react';
import CameraView from '../components/CameraView';

describe('CameraView', () => {
  const mockCamera = {
    id: 'front_door',
    name: 'Front Door',
    url: 'http://example.com/stream',
    enabled: true,
  };
  
  test('renders camera name', () => {
    render(<CameraView camera={mockCamera} />);
    const nameElement = screen.getByText(/Front Door/i);
    expect(nameElement).toBeInTheDocument();
  });
  
  test('shows loading state initially', () => {
    render(<CameraView camera={mockCamera} />);
    const loadingElement = screen.getByText(/Loading/i);
    expect(loadingElement).toBeInTheDocument();
  });
});
```

### Hardware Test Example

```python
import pytest
from arkos.io.hardware import gpio_manager

@pytest.mark.hardware
def test_gpio_output():
    # Set up GPIO output
    pin = 18
    gpio_manager.setup_output(pin)
    
    # Set output high
    gpio_manager.set_output(pin, True)
    assert gpio_manager.get_output(pin) is True
    
    # Set output low
    gpio_manager.set_output(pin, False)
    assert gpio_manager.get_output(pin) is False
    
    # Clean up
    gpio_manager.cleanup(pin)
