# Coding Standards

This document outlines the coding standards and best practices for the Arkos AI project. Following these standards ensures consistency across the codebase and makes it easier for developers to understand and maintain the code.

## General Guidelines

### Code Organization

- Follow the modular architecture outlined in the [architecture documentation](../architecture/overview.md)
- Keep files focused on a single responsibility
- Limit file size to maintain readability (aim for < 500 lines)
- Use meaningful file and directory names that reflect their purpose

### Documentation

- Document all public functions, classes, and modules
- Include examples in documentation where appropriate
- Keep documentation up-to-date with code changes
- Use clear and concise language in documentation

### Version Control

- Write meaningful commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) format
- Keep commits focused on a single change
- Rebase feature branches on dev before creating pull requests
- Squash commits before merging to maintain a clean history

### Error Handling

- Use appropriate error handling mechanisms for each language
- Provide meaningful error messages
- Log errors with appropriate context
- Handle errors at the appropriate level of abstraction

### Testing

- Write tests for all new functionality
- Maintain high test coverage (aim for > 80%)
- Use appropriate testing frameworks for each language
- Include both unit and integration tests

## Python Standards

### Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting

### Naming Conventions

- Use `snake_case` for variables, functions, and modules
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
- Use descriptive names that reflect purpose

### Type Hints

- Use type hints for all function parameters and return values
- Use appropriate types from the `typing` module
- Use `Optional` for parameters that can be `None`
- Use `Union` for parameters that can be multiple types

### Docstrings

- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Include parameter and return value descriptions
- Document exceptions that may be raised
- Include examples where appropriate

### Example

```python
from typing import List, Optional, Dict, Any

def process_camera_frame(
    frame: np.ndarray,
    camera_id: str,
    config: Dict[str, Any],
    timestamp: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Process a camera frame for object detection.
    
    Args:
        frame: The camera frame as a numpy array.
        camera_id: The ID of the camera.
        config: The configuration for the camera.
        timestamp: The timestamp of the frame, if available.
        
    Returns:
        A list of detected objects, each as a dictionary with keys:
        - id: The object ID
        - label: The object label
        - confidence: The detection confidence
        - bbox: The bounding box as [x, y, width, height]
        
    Raises:
        ValueError: If the frame is invalid or empty.
        ConfigError: If the camera configuration is invalid.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Frame is invalid or empty")
        
    # Implementation...
    
    return detected_objects
```

## JavaScript/TypeScript Standards

### Style Guide

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [ESLint](https://eslint.org/) for linting
- Use [Prettier](https://prettier.io/) for code formatting
- Use TypeScript for type safety

### Naming Conventions

- Use `camelCase` for variables and functions
- Use `PascalCase` for classes and React components
- Use `UPPER_CASE` for constants
- Use descriptive names that reflect purpose

### TypeScript Types

- Define interfaces for complex objects
- Use appropriate TypeScript types
- Use optional properties with `?` for properties that may be undefined
- Use union types for variables that can have multiple types

### JSDoc Comments

- Use JSDoc comments for all functions and classes
- Include parameter and return value descriptions
- Document exceptions that may be thrown
- Include examples where appropriate

### React Components

- Use functional components with hooks
- Use TypeScript for props and state
- Keep components focused on a single responsibility
- Use appropriate component composition

### Example

```typescript
/**
 * Interface for camera configuration.
 */
interface CameraConfig {
  id: string;
  name: string;
  url: string;
  enabled: boolean;
  detectObjects?: string[];
  zones?: Record<string, Zone>;
}

/**
 * Interface for a detection zone.
 */
interface Zone {
  coordinates: number[][];
  name: string;
  type: 'include' | 'exclude';
}

/**
 * Process camera configuration and return validated config.
 * 
 * @param config - The camera configuration to process.
 * @returns The processed and validated configuration.
 * @throws {Error} If the configuration is invalid.
 */
function processCameraConfig(config: CameraConfig): CameraConfig {
  if (!config.id || !config.url) {
    throw new Error('Camera configuration must include id and url');
  }
  
  // Implementation...
  
  return validatedConfig;
}

/**
 * Camera component for displaying a camera feed.
 */
const Camera: React.FC<{
  config: CameraConfig;
  onDetection?: (detection: Detection) => void;
}> = ({ config, onDetection }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Implementation...
  
  return (
    <div className="camera-container">
      {isLoading && <Spinner />}
      {error && <ErrorMessage message={error} />}
      <video ref={videoRef} className="camera-feed" />
    </div>
  );
};
```

## YAML Standards

### Style Guide

- Use 2 spaces for indentation
- Use lowercase for keys
- Use hyphens for list items
- Use meaningful key names

### Structure

- Organize configuration logically
- Group related configuration together
- Use comments to explain complex configuration
- Keep configuration files focused on a single purpose

### Example

```yaml
# Camera configuration
cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.1.100:554/stream
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
        - car
        - package
```

## SQL Standards

### Style Guide

- Use uppercase for SQL keywords
- Use lowercase for table and column names
- Use underscores for table and column names
- Use meaningful table and column names

### Structure

- Use appropriate data types
- Define appropriate indexes
- Use foreign key constraints
- Include comments for complex queries

### Example

```sql
-- Create events table
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  camera_id TEXT NOT NULL,
  label TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL,
  top_score REAL,
  false_positive INTEGER DEFAULT 0,
  zones TEXT,
  thumbnail TEXT,
  region TEXT,
  box TEXT,
  area INTEGER,
  has_snapshot INTEGER DEFAULT 0,
  has_clip INTEGER DEFAULT 0,
  plus_id TEXT,
  retain_indefinitely INTEGER DEFAULT 0,
  sub_label TEXT,
  current_zones TEXT,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

-- Index for efficient queries
CREATE INDEX events_camera_id ON events(camera_id);
CREATE INDEX events_start_time ON events(start_time);
```

## Shell Script Standards

### Style Guide

- Use 2 spaces for indentation
- Use lowercase for variable names
- Use meaningful variable names
- Include comments for complex logic

### Structure

- Include a shebang line
- Include usage information
- Handle errors appropriately
- Use functions for reusable code

### Example

```bash
#!/bin/bash
# Deploy Arkos AI to a target environment

set -e

# Display usage information
function usage() {
  echo "Usage: $0 [environment]"
  echo "  environment: The target environment (dev, test, prod)"
  exit 1
}

# Validate arguments
if [ $# -ne 1 ]; then
  usage
fi

environment=$1

# Validate environment
if [ "$environment" != "dev" ] && [ "$environment" != "test" ] && [ "$environment" != "prod" ]; then
  echo "Invalid environment: $environment"
  usage
fi

# Deploy to the target environment
echo "Deploying to $environment..."

# Implementation...

echo "Deployment complete"
```

## Code Review Guidelines

### What to Look For

- Adherence to coding standards
- Appropriate error handling
- Adequate test coverage
- Clear and concise documentation
- Performance considerations
- Security considerations

### Review Process

1. Review the code for adherence to coding standards
2. Run the tests to ensure they pass
3. Review the documentation for clarity and completeness
4. Provide constructive feedback
5. Approve the pull request when all issues are addressed

### Feedback Guidelines

- Be specific and constructive
- Focus on the code, not the person
- Provide examples where appropriate
- Explain the reasoning behind your feedback
- Be open to discussion and alternative approaches
