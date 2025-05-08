# Initial Issues

This document lists the initial issues that should be created in the GitHub repository for the Arkos AI project. These issues are based on the [Project Roadmap](./project-roadmap.md) and are organized by milestone.

## How to Use This Document

1. Create a GitHub repository for the Arkos AI project
2. Set up the issue templates as described in [Issue Templates](./issue-templates.md)
3. Create the issues listed in this document, using the appropriate issue template for each
4. Assign the issues to the appropriate milestone
5. Prioritize the issues according to the [Dependency Graph](../architecture/dependency-graph.md)

## Phase 1: Core Foundation

### Milestone 1.1: Repository Setup

#### Issue 1: Fork Frigate repository

```markdown
---
name: Task
about: General task
title: '[TASK] Fork Frigate repository'
labels: setup
assignees: ''
---

## Description

Fork the Frigate NVR repository to create the base for Arkos AI.

## Tasks

- [ ] Create a new GitHub organization for Arkos AI
- [ ] Fork the Frigate NVR repository to the Arkos AI organization
- [ ] Clone the forked repository locally
- [ ] Update the remote URLs to point to the new repository

## Acceptance Criteria

- [ ] The Frigate repository is successfully forked to the Arkos AI organization
- [ ] The repository can be cloned locally
- [ ] The remote URLs are correctly configured

## Additional Context

This is the first step in setting up the Arkos AI project. The Frigate NVR repository will serve as the base for our enhanced NVR system.
```

#### Issue 2: Rename to Arkos AI

```markdown
---
name: Task
about: General task
title: '[TASK] Rename repository to Arkos AI'
labels: setup
assignees: ''
---

## Description

Rename the forked repository and update all references to Frigate to Arkos AI.

## Tasks

- [ ] Rename the repository to arkos-ai
- [ ] Update all references to Frigate in the code
- [ ] Update all references to Frigate in the documentation
- [ ] Update package names and imports
- [ ] Update Docker image names

## Acceptance Criteria

- [ ] The repository is renamed to arkos-ai
- [ ] All references to Frigate are updated to Arkos AI
- [ ] The code builds and runs successfully with the new name

## Additional Context

This task involves a global search and replace of "frigate" with "arkos" (case-insensitive) and "Frigate" with "Arkos AI" throughout the codebase and documentation.
```

#### Issue 3: Set up CI/CD pipeline

```markdown
---
name: Task
about: General task
title: '[TASK] Set up CI/CD pipeline'
labels: setup, devops
assignees: ''
---

## Description

Set up a CI/CD pipeline for the Arkos AI repository using GitHub Actions.

## Tasks

- [ ] Create GitHub Actions workflow for linting
- [ ] Create GitHub Actions workflow for testing
- [ ] Create GitHub Actions workflow for building Docker images
- [ ] Create GitHub Actions workflow for documentation
- [ ] Configure branch protection rules

## Acceptance Criteria

- [ ] CI/CD pipeline is set up and working
- [ ] All workflows run successfully on pull requests
- [ ] Branch protection rules are configured to require passing CI checks
- [ ] Docker images are built and published to GitHub Container Registry

## Additional Context

The CI/CD pipeline should include:
- Linting with flake8, black, and isort
- Testing with pytest
- Building Docker images for multiple architectures
- Building and publishing documentation
```

#### Issue 4: Create initial documentation structure

```markdown
---
name: Documentation Task
about: Tasks related to documentation
title: '[DOCS] Create initial documentation structure'
labels: documentation
assignees: ''
---

## Description

Create the initial documentation structure for the Arkos AI project.

## Type of Documentation

- [x] User Guide
- [x] Developer Guide
- [x] API Documentation
- [ ] Code Comments
- [ ] Other: [please specify]

## Scope

Create the following documentation structure:
- README.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- docs/
  - architecture/
  - modules/
  - development/
  - testing/
  - user/
  - api/

## Content Outline

- README.md: Project overview, features, installation, usage
- CONTRIBUTING.md: Contribution guidelines
- CODE_OF_CONDUCT.md: Code of conduct
- docs/architecture/: System architecture documentation
- docs/modules/: Module-specific documentation
- docs/development/: Development guides
- docs/testing/: Testing guides
- docs/user/: User guides
- docs/api/: API documentation

## Acceptance Criteria

- [ ] Documentation structure is created
- [ ] Basic content is added to each document
- [ ] Documentation is accessible and readable
- [ ] Documentation follows a consistent style

## Additional Context

This is the initial documentation structure. The content will be expanded as the project progresses.
```

### Milestone 1.2: Camera Management

#### Issue 5: Refactor camera integration code

```markdown
---
name: Refactoring Task
about: Tasks related to code refactoring
title: '[REFACTOR] Camera integration code'
labels: refactoring, camera
assignees: ''
---

## Description

Refactor the camera integration code to improve modularity, testability, and extensibility.

## Current Code

The current camera integration code in Frigate is tightly coupled and difficult to extend. It handles camera connection, frame acquisition, and preprocessing in a monolithic way.

## Proposed Changes

- Separate camera connection, frame acquisition, and preprocessing into distinct components
- Create interfaces for each component to allow for different implementations
- Implement a factory pattern for creating camera instances
- Add better error handling and recovery mechanisms

## Motivation

The refactoring is necessary to:
- Make it easier to add support for new camera types
- Improve testability by allowing components to be tested in isolation
- Enhance reliability with better error handling
- Prepare for future enhancements like camera health monitoring

## Benefits

- More modular and maintainable code
- Easier to extend with new camera types
- Better testability
- Improved error handling and recovery

## Risks

- Potential regression in existing functionality
- Performance impact if not carefully implemented

## Testing Plan

- Unit tests for each component
- Integration tests for the camera subsystem
- End-to-end tests with actual cameras

## Acceptance Criteria

- [ ] Camera integration code is refactored into modular components
- [ ] All existing camera types are supported
- [ ] Unit tests are written for each component
- [ ] Integration tests verify correct interaction between components
- [ ] No regression in functionality or performance

## Additional Context

This refactoring is a prerequisite for enhancing camera configuration options and adding support for additional camera types.
```

#### Issue 6: Enhance camera configuration options

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Enhanced camera configuration options'
labels: enhancement, camera
assignees: ''
---

## Problem Statement

The current camera configuration options are limited and don't provide enough flexibility for advanced use cases. Users need more control over camera settings to optimize for their specific environments.

## Proposed Solution

Enhance the camera configuration options to include:
- Fine-grained control over resolution and frame rate for different roles (detect, record, rtmp)
- Advanced RTSP options (transport protocol, authentication methods)
- Camera grouping for easier management
- Camera templates for quick configuration
- Dynamic configuration changes without restart

## Alternative Solutions

- Keep the current configuration structure but add more options
- Use a separate configuration file for advanced camera settings
- Implement a UI-based configuration wizard

## User Stories

- As a power user, I want to configure different resolutions for detection and recording so that I can optimize performance and storage.
- As an administrator, I want to group cameras by location so that I can manage them more easily.
- As a user, I want to apply templates to cameras so that I can quickly configure new cameras.
- As a user, I want to change camera settings without restarting the system so that I can experiment with different configurations.

## Acceptance Criteria

- [ ] Enhanced camera configuration options are implemented
- [ ] Configuration changes can be applied without system restart
- [ ] Camera grouping is supported
- [ ] Camera templates are implemented
- [ ] Documentation is updated with the new configuration options
- [ ] UI is updated to support the new configuration options

## Additional Context

This feature builds on the refactored camera integration code and prepares for the camera health monitoring feature.

## Dependencies

- Refactor camera integration code
```

#### Issue 7: Implement camera connection management

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Camera connection management'
labels: enhancement, camera
assignees: ''
---

## Problem Statement

The current system doesn't handle camera connection issues gracefully. When a camera disconnects, the system may not recover properly or may waste resources trying to reconnect too aggressively.

## Proposed Solution

Implement a robust camera connection management system that:
- Monitors camera connection status
- Implements exponential backoff for reconnection attempts
- Provides clear status information about camera connections
- Logs connection events for troubleshooting
- Notifies users of persistent connection issues

## Alternative Solutions

- Implement a simpler reconnection strategy with fixed intervals
- Rely on external monitoring tools to detect and handle camera connection issues
- Implement connection management at the RTSP library level

## User Stories

- As a user, I want the system to automatically recover from camera disconnections so that I don't lose recordings.
- As an administrator, I want to see the connection status of all cameras so that I can identify issues.
- As a user, I want to be notified of persistent camera connection issues so that I can address them.

## Acceptance Criteria

- [ ] Camera connection status is monitored and reported
- [ ] Exponential backoff is implemented for reconnection attempts
- [ ] Connection events are logged for troubleshooting
- [ ] Users are notified of persistent connection issues
- [ ] System recovers gracefully from camera disconnections
- [ ] UI displays camera connection status

## Additional Context

This feature is a prerequisite for the camera health monitoring feature and will improve the overall reliability of the system.

## Dependencies

- Refactor camera integration code
```

#### Issue 8: Add support for additional camera types

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Support for additional camera types'
labels: enhancement, camera
assignees: ''
---

## Problem Statement

The current system supports a limited set of camera types, primarily RTSP and HTTP streams. Users have requested support for additional camera types and protocols.

## Proposed Solution

Extend the camera integration system to support:
- ONVIF cameras with automatic discovery
- USB cameras
- Local video files (for testing and demo purposes)
- MJPEG streams
- HLS streams
- WebRTC streams

## Alternative Solutions

- Focus on improving support for existing camera types
- Implement support for only the most requested camera types
- Rely on external tools to convert unsupported camera streams to supported formats

## User Stories

- As a user, I want to use ONVIF cameras so that I can take advantage of their advanced features.
- As a developer, I want to use local video files for testing so that I can develop without physical cameras.
- As a user, I want to use USB cameras so that I can use affordable local cameras.

## Acceptance Criteria

- [ ] ONVIF camera support is implemented with automatic discovery
- [ ] USB camera support is implemented
- [ ] Local video file support is implemented
- [ ] MJPEG stream support is implemented
- [ ] HLS stream support is implemented
- [ ] WebRTC stream support is implemented
- [ ] Documentation is updated with the new camera types
- [ ] UI is updated to support configuring the new camera types

## Additional Context

This feature builds on the refactored camera integration code and enhanced configuration options.

## Dependencies

- Refactor camera integration code
- Enhance camera configuration options
```

#### Issue 9: Develop camera status monitoring

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Camera status monitoring'
labels: enhancement, camera
assignees: ''
---

## Problem Statement

The current system provides limited information about camera status, making it difficult for users to troubleshoot issues or monitor the health of their cameras.

## Proposed Solution

Develop a comprehensive camera status monitoring system that:
- Tracks camera connection status
- Monitors frame rate and resolution
- Tracks bandwidth usage
- Monitors CPU and memory usage per camera
- Provides historical status data
- Alerts on status changes or issues

## Alternative Solutions

- Implement basic status monitoring with fewer metrics
- Rely on external monitoring tools
- Focus on real-time status only without historical data

## User Stories

- As an administrator, I want to see the status of all cameras so that I can identify issues.
- As a user, I want to monitor the bandwidth usage of my cameras so that I can optimize my network.
- As a user, I want to be alerted when a camera's status changes so that I can address issues promptly.

## Acceptance Criteria

- [ ] Camera connection status is tracked and displayed
- [ ] Frame rate and resolution are monitored
- [ ] Bandwidth usage is tracked
- [ ] CPU and memory usage per camera is monitored
- [ ] Historical status data is stored and can be viewed
- [ ] Alerts are generated for status changes or issues
- [ ] UI displays camera status information

## Additional Context

This feature is a foundation for the more advanced camera health monitoring features planned for Phase 2.

## Dependencies

- Refactor camera integration code
- Implement camera connection management
```

### Milestone 1.3: Object Detection

#### Issue 10: Refactor object detection pipeline

```markdown
---
name: Refactoring Task
about: Tasks related to code refactoring
title: '[REFACTOR] Object detection pipeline'
labels: refactoring, detection
assignees: ''
---

## Description

Refactor the object detection pipeline to improve modularity, testability, and extensibility.

## Current Code

The current object detection pipeline is tightly coupled and difficult to extend. It handles motion detection, object detection, and object tracking in a monolithic way.

## Proposed Changes

- Separate motion detection, object detection, and object tracking into distinct components
- Create interfaces for each component to allow for different implementations
- Implement a plugin system for detection models
- Add better error handling and recovery mechanisms
- Improve the frame processing pipeline for better performance

## Motivation

The refactoring is necessary to:
- Make it easier to add support for new detection models
- Improve testability by allowing components to be tested in isolation
- Enhance reliability with better error handling
- Prepare for future enhancements like activity recognition

## Benefits

- More modular and maintainable code
- Easier to extend with new detection models
- Better testability
- Improved error handling and recovery
- Better performance through optimized frame processing

## Risks

- Potential regression in existing functionality
- Performance impact if not carefully implemented

## Testing Plan

- Unit tests for each component
- Integration tests for the detection pipeline
- Performance benchmarks to ensure no regression

## Acceptance Criteria

- [ ] Object detection pipeline is refactored into modular components
- [ ] All existing detection models are supported
- [ ] Unit tests are written for each component
- [ ] Integration tests verify correct interaction between components
- [ ] No regression in functionality or performance
- [ ] Documentation is updated to reflect the new architecture

## Additional Context

This refactoring is a prerequisite for optimizing motion detection, enhancing object tracking, and implementing multi-model support.
```

#### Issue 11: Optimize motion detection

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Optimized motion detection'
labels: enhancement, detection, performance
assignees: ''
---

## Problem Statement

The current motion detection system is not optimized for all environments and can generate false positives or miss motion in certain conditions. It also consumes more CPU resources than necessary.

## Proposed Solution

Optimize the motion detection system to:
- Implement adaptive thresholding based on scene conditions
- Add support for different motion detection algorithms
- Optimize for CPU usage
- Add more configuration options for fine-tuning
- Implement region-based sensitivity settings
- Add motion masks for ignoring areas with constant motion

## Alternative Solutions

- Use a machine learning approach for motion detection
- Rely on camera-based motion detection
- Implement a simpler but more efficient motion detection algorithm

## User Stories

- As a user, I want motion detection to work reliably in all lighting conditions so that I don't miss events.
- As a user, I want to configure motion sensitivity by region so that I can ignore areas with constant motion.
- As a system administrator, I want motion detection to use minimal CPU resources so that I can run more cameras on the same hardware.

## Acceptance Criteria

- [ ] Adaptive thresholding is implemented
- [ ] Multiple motion detection algorithms are supported
- [ ] CPU usage is optimized
- [ ] Region-based sensitivity settings are implemented
- [ ] Motion masks are supported
- [ ] Documentation is updated with the new features
- [ ] UI is updated to support configuring the new features

## Additional Context

This feature builds on the refactored object detection pipeline and will improve the overall reliability and performance of the system.

## Dependencies

- Refactor object detection pipeline
```

#### Issue 12: Enhance object tracking

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Enhanced object tracking'
labels: enhancement, detection
assignees: ''
---

## Problem Statement

The current object tracking system has limitations in tracking objects across frames, especially in complex scenes with multiple objects or when objects are temporarily occluded.

## Proposed Solution

Enhance the object tracking system to:
- Implement more advanced tracking algorithms (e.g., SORT, DeepSORT)
- Improve object ID persistence across frames
- Handle occlusions better
- Track objects across multiple cameras
- Provide more tracking metrics (speed, direction, etc.)
- Optimize for performance

## Alternative Solutions

- Use a simpler tracking algorithm with better performance
- Rely on detection-only without sophisticated tracking
- Implement tracking at a higher level (event level rather than frame level)

## User Stories

- As a user, I want objects to maintain the same ID across frames so that I can track their movement.
- As a user, I want to track objects across multiple cameras so that I can follow their path through my property.
- As a user, I want to see the speed and direction of objects so that I can better understand their behavior.

## Acceptance Criteria

- [ ] Advanced tracking algorithms are implemented
- [ ] Object ID persistence is improved
- [ ] Occlusion handling is improved
- [ ] Cross-camera tracking is implemented
- [ ] Tracking metrics (speed, direction) are provided
- [ ] Performance is optimized
- [ ] Documentation is updated with the new features
- [ ] UI is updated to display the new tracking information

## Additional Context

This feature builds on the refactored object detection pipeline and will improve the overall accuracy and usefulness of the system.

## Dependencies

- Refactor object detection pipeline
```

#### Issue 13: Implement multi-model support

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Multi-model support'
labels: enhancement, detection
assignees: ''
---

## Problem Statement

The current system supports a limited set of detection models and doesn't allow using multiple models simultaneously for different purposes or to improve accuracy.

## Proposed Solution

Implement multi-model support to:
- Allow using different models for different cameras
- Support running multiple models on the same camera for different object types
- Implement model chaining (e.g., general detection followed by specialized classification)
- Add support for model switching based on time, events, or other triggers
- Optimize resource usage when running multiple models

## Alternative Solutions

- Focus on improving a single model for all purposes
- Implement model specialization at the post-processing level
- Use external services for specialized detection

## User Stories

- As a user, I want to use different detection models for different cameras so that I can optimize for each camera's environment.
- As a user, I want to use specialized models for specific object types so that I can improve detection accuracy.
- As a user, I want to switch models based on time of day so that I can optimize for different lighting conditions.

## Acceptance Criteria

- [ ] Support for using different models for different cameras
- [ ] Support for running multiple models on the same camera
- [ ] Model chaining is implemented
- [ ] Model switching based on triggers is implemented
- [ ] Resource usage is optimized
- [ ] Documentation is updated with the new features
- [ ] UI is updated to support configuring multiple models

## Additional Context

This feature builds on the refactored object detection pipeline and will provide more flexibility and accuracy for users.

## Dependencies

- Refactor object detection pipeline
```

#### Issue 14: Add support for custom detection models

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Support for custom detection models'
labels: enhancement, detection
assignees: ''
---

## Problem Statement

The current system supports only a limited set of pre-defined detection models. Users want to use their own custom-trained models for specific detection tasks.

## Proposed Solution

Add support for custom detection models:
- Implement a plugin system for loading custom models
- Support common model formats (ONNX, TensorFlow, PyTorch)
- Provide tools for model conversion and optimization
- Add a UI for uploading and managing custom models
- Implement validation and testing tools for custom models
- Document the process for creating and using custom models

## Alternative Solutions

- Support only a specific model format
- Implement custom model support through external scripts
- Focus on providing more pre-trained models instead

## User Stories

- As a developer, I want to use my custom-trained models so that I can detect specific objects for my use case.
- As a user, I want to upload custom models through the UI so that I don't need to access the file system.
- As a user, I want to test my custom models before deploying them so that I can ensure they work correctly.

## Acceptance Criteria

- [ ] Plugin system for loading custom models is implemented
- [ ] Common model formats are supported
- [ ] Tools for model conversion and optimization are provided
- [ ] UI for uploading and managing custom models is implemented
- [ ] Validation and testing tools for custom models are implemented
- [ ] Documentation for creating and using custom models is created
- [ ] Performance impact of custom models is minimized

## Additional Context

This feature builds on the refactored object detection pipeline and multi-model support, and will provide more flexibility for advanced users.

## Dependencies

- Refactor object detection pipeline
- Implement multi-model support
```

## Additional Issues

The issues listed above cover the first two milestones of Phase 1 in detail. Similar issues should be created for the remaining milestones in Phase 1 and for subsequent phases based on the [Project Roadmap](./project-roadmap.md).

For each milestone, create issues for all the tasks listed in the roadmap, following the appropriate issue template for each. Ensure that dependencies between issues are clearly indicated.

## Issue Prioritization

Issues should be prioritized based on the [Dependency Graph](../architecture/dependency-graph.md) and the critical path identified in the roadmap. In general, the following prioritization should be followed:

1. Repository setup issues
2. Core infrastructure refactoring issues
3. Feature implementation issues
4. Enhancement and optimization issues
5. Documentation and testing issues (in parallel with other issues)

## Issue Assignment

Issues should be assigned to team members based on their skills and availability. Consider the following guidelines:

- Assign complex refactoring tasks to experienced developers
- Distribute tasks evenly across the team
- Consider dependencies when assigning tasks to minimize blocking
- Assign related tasks to the same developer when possible to leverage context

## Issue Tracking

Track issue progress using the methods described in [Project Tracking](./project-tracking.md). Regularly update issue status, add comments for progress updates, and close issues when they are completed.

## Conclusion

This document provides a starting point for creating the initial issues for the Arkos AI project. By following this approach, you can create a well-organized backlog of issues that align with the project roadmap and dependency graph.
