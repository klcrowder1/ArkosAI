# Object Detection Pipeline Refactoring Plan

This document outlines the plan for refactoring the object detection pipeline in Arkos AI (formerly Frigate). The goal is to improve the architecture, maintainability, and extensibility of the object detection system while maintaining compatibility with existing functionality.

## Current Architecture

The current object detection pipeline consists of:

1. **Base Classes**:
   - `ObjectDetector` (abstract) and `LocalObjectDetector` in `frigate/object_detection/base.py`
   - `DetectionApi` (abstract) in `frigate/detectors/detection_api.py`

2. **Detector Implementations**:
   - Various detector plugins in `frigate/detectors/plugins/` (CPU, EdgeTPU, OpenVINO, TensorRT, etc.)

3. **Configuration**:
   - `BaseDetectorConfig` and `ModelConfig` in `frigate/detectors/detector_config.py`
   - Detector-specific configurations in each plugin

4. **Factory Pattern**:
   - `create_detector` in `frigate/detectors/__init__.py`

5. **Object Processing**:
   - `TrackedObjectProcessor` in `frigate/track/object_processing.py`

## Issues with Current Implementation

1. **Tight Coupling**:
   - Detector implementations are tightly coupled with the core framework
   - Changes to the detection API require changes to all detector implementations

2. **Limited Extensibility**:
   - Adding new detector types requires modifying multiple files
   - No clear extension points for third-party detectors

3. **Inconsistent Patterns**:
   - Different detector implementations follow different patterns
   - Error handling is inconsistent across implementations

4. **Complex Configuration**:
   - Configuration structure is complex and redundant
   - Difficult to validate configurations

5. **Code Duplication**:
   - Common functionality is duplicated across detector implementations
   - Preprocessing and postprocessing logic is repeated

## Refactoring Goals

1. **Improve Modularity**:
   - Clearly separate the detection framework from specific implementations
   - Define clean interfaces between components

2. **Enhance Extensibility**:
   - Make it easier to add new detector types
   - Support third-party detector plugins

3. **Standardize Patterns**:
   - Establish consistent patterns across all detector implementations
   - Improve error handling and logging

4. **Simplify Configuration**:
   - Streamline the configuration structure
   - Improve validation of configurations

5. **Reduce Duplication**:
   - Extract common functionality into shared utilities
   - Centralize preprocessing and postprocessing logic

## Proposed Architecture

### 1. Core Components

#### `DetectorInterface` (Abstract)
- Defines the contract for all detectors
- Provides common functionality through default implementations
- Includes methods for initialization, detection, and cleanup

#### `DetectorRegistry`
- Manages registration of detector implementations
- Provides factory methods for creating detectors
- Supports dynamic loading of third-party detectors

#### `DetectionPipeline`
- Orchestrates the detection process
- Handles preprocessing and postprocessing
- Manages detector lifecycle

### 2. Configuration

#### `DetectorConfig` (Base)
- Simplified base configuration for all detectors
- Common settings shared across all detector types

#### `ModelConfig` (Enhanced)
- Improved model configuration with better validation
- Support for different model types and formats

### 3. Utilities

#### `PreprocessingUtils`
- Centralized utilities for image preprocessing
- Support for different input formats and transformations

#### `PostprocessingUtils`
- Utilities for processing detection results
- Standardized format conversion

### 4. Detector Implementations

#### Built-in Detectors
- Refactored implementations of existing detectors
- Consistent error handling and logging
- Shared utilities for common tasks

#### Plugin System
- Clear extension points for third-party detectors
- Documentation for creating custom detectors

## Implementation Plan

### Phase 1: Core Framework

1. Create the new `DetectorInterface` abstract class
2. Implement the `DetectorRegistry` for detector management
3. Develop the `DetectionPipeline` orchestrator
4. Create utility classes for preprocessing and postprocessing

### Phase 2: Configuration Refactoring

1. Simplify the detector configuration structure
2. Improve validation of configurations
3. Create migration utilities for existing configurations

### Phase 3: Detector Implementations

1. Refactor existing detector implementations to use the new framework
2. Standardize error handling and logging
3. Extract common functionality into shared utilities

### Phase 4: Integration and Testing

1. Integrate the refactored pipeline with the existing codebase
2. Develop comprehensive tests for the new components
3. Ensure backward compatibility with existing configurations

## Backward Compatibility

To maintain backward compatibility:

1. Support existing configuration formats
2. Provide migration utilities for configurations
3. Ensure the same detection results with the refactored pipeline
4. Maintain the same performance characteristics

## Performance Considerations

The refactoring should not negatively impact performance:

1. Minimize overhead in the abstraction layers
2. Optimize critical paths in the detection process
3. Benchmark before and after refactoring to ensure comparable performance

## Documentation

1. Update API documentation to reflect the new architecture
2. Create guides for implementing custom detectors
3. Document the migration process for existing code

## Success Criteria

The refactoring will be considered successful if:

1. All existing functionality is maintained
2. The code is more modular and maintainable
3. Adding new detector types is easier
4. Performance is comparable to the current implementation
5. The configuration is simpler and more robust
