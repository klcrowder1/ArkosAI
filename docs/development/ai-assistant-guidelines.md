# AI Assistant Guidelines

This document outlines the rules and guidelines for AI assistants working on the Arkos AI project. These guidelines ensure that AI assistants provide consistent, high-quality assistance that aligns with the project's standards and practices.

## Overview

AI assistants like Claude can be valuable collaborators in the development process. To maximize their effectiveness, we've established these guidelines to ensure they follow our project's standards and practices.

## General Rules

1. **Follow Project Documentation**: Always adhere to the project's documentation, including coding standards, architecture guidelines, and development workflows.

2. **Prioritize Quality**: Focus on delivering high-quality, well-tested code rather than quick solutions.

3. **Respect Project Structure**: Maintain the established project structure and organization.

4. **Be Explicit**: Provide clear explanations for your suggestions and decisions.

5. **Show Your Work**: When solving problems, explain your thought process and consider multiple approaches.

6. **Cite Sources**: When referencing external information, provide links to sources.

7. **Respect Scope**: Stay within the scope of the current task or discussion.

## Code Standards

1. **Follow Coding Standards**: Adhere to the [Coding Standards](./coding-standards.md) document.

2. **Use Consistent Style**: Maintain consistent coding style throughout the project.

3. **Write Clean Code**: Follow clean code principles:
   - Meaningful variable and function names
   - Single responsibility principle
   - DRY (Don't Repeat Yourself)
   - KISS (Keep It Simple, Stupid)

4. **Include Documentation**: Add appropriate comments and documentation to code.

5. **Write Tests**: Include tests for new functionality.

## Communication Guidelines

1. **Be Direct**: Provide direct, concise responses without unnecessary pleasantries.

2. **Be Technical**: Use precise technical language appropriate for developers.

3. **Avoid Assumptions**: Ask for clarification when requirements are ambiguous.

4. **Provide Context**: Include relevant context in your responses.

5. **Use Markdown**: Format responses using Markdown for readability.

6. **Use Code Blocks**: Present code in properly formatted code blocks with language specification.

## Task Workflow

1. **Understand Requirements**: Ensure you fully understand the requirements before starting work.

2. **Plan Before Coding**: Outline your approach before writing code.

3. **Break Down Complex Tasks**: Divide complex tasks into smaller, manageable steps.

4. **Test Your Work**: Verify that your solution works as expected.

5. **Review Your Work**: Check for errors, edge cases, and potential improvements.

6. **Document Changes**: Explain what changes you made and why.

## Specific Project Rules

### Architecture

1. **Respect Modularity**: Maintain the modular architecture as defined in the [Dependency Graph](../architecture/dependency-graph.md).

2. **Follow Data Flow**: Adhere to the established [Data Flow](../architecture/data-flow.md) patterns.

3. **Use Correct Database Schema**: Follow the [Database Schema](../architecture/database-schema.md) for data storage.

### Development Process

1. **Follow Project Roadmap**: Align work with the [Project Roadmap](./project-roadmap.md).

2. **Track Progress**: Update progress according to the [Project Tracking](./project-tracking.md) guidelines.

3. **Use Issue Templates**: Follow the [Issue Templates](./issue-templates.md) for creating and responding to issues.

### Testing

1. **Follow Testing Strategy**: Adhere to the [Testing Strategy](../testing/strategy.md) document.

2. **Include All Test Types**: Write unit, integration, and system tests as appropriate.

3. **Test on Target Hardware**: Consider testing requirements for the [LattePanda hardware](../testing/lattepanda-tests.md).

## How to Instruct AI Assistants

When working with AI assistants on the Arkos AI project, use the following approaches to ensure they follow these guidelines:

### Setting Context

Begin your interaction by setting the context:

```
You are assisting with the Arkos AI project. Please follow the AI Assistant Guidelines 
in docs/development/ai-assistant-guidelines.md. The current task is [description of task].
```

### Specifying Rules

To add specific rules for a task:

```
For this task, please follow these additional rules:
1. [Rule 1]
2. [Rule 2]
3. [Rule 3]
```

### Referencing Documentation

Direct the AI assistant to specific documentation:

```
Please refer to the [Document Name](path/to/document.md) for guidance on this task.
```

### Providing Feedback

When providing feedback on AI assistant work:

```
Your solution [meets/doesn't meet] our guidelines in the following ways:
- [Specific feedback point 1]
- [Specific feedback point 2]
Please adjust your approach to better align with our [specific guideline].
```

## Examples

### Example 1: Good Interaction

**User**:
```
You are assisting with the Arkos AI project. Please follow the AI Assistant Guidelines 
in docs/development/ai-assistant-guidelines.md. I need help implementing the camera 
health monitoring feature described in docs/modules/health/README.md. Please focus on 
the connectivity monitoring component first.
```

**AI Assistant**:
```
I'll help implement the camera health monitoring feature, focusing on connectivity monitoring.

After reviewing docs/modules/health/README.md, I understand we need to:
1. Create a connectivity monitoring component
2. Implement timeout and retry logic
3. Add bandwidth and latency checking

Let me outline the approach:

## Implementation Plan
1. Create a ConnectivityMonitor class
2. Implement basic connectivity checking
3. Add timeout and retry mechanisms
4. Implement bandwidth and latency measurements
5. Add alerting integration

Here's the proposed implementation for the ConnectivityMonitor class:

```python
from typing import Dict, Optional, Tuple
import time
import requests
from arkos.core.models import Camera
from arkos.health.alerts import AlertManager

class ConnectivityMonitor:
    """Monitors camera connectivity and network performance."""
    
    def __init__(self, timeout: int = 5, retry_count: int = 3):
        """Initialize the connectivity monitor.
        
        Args:
            timeout: Connection timeout in seconds
            retry_count: Number of retries before marking as disconnected
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.alert_manager = AlertManager()
        
    def check_connectivity(self, camera: Camera) -> bool:
        """Check if a camera is connected.
        
        Args:
            camera: The camera to check
            
        Returns:
            True if connected, False otherwise
        """
        # Implementation details...
```

### Example 2: Correcting an Interaction

**User**:
```
Can you create a quick script to process the camera feeds?
```

**AI Assistant**:
```
I notice this request doesn't provide enough context for me to follow the AI Assistant Guidelines for the Arkos AI project. 

To better assist you, I would need:

1. Specific requirements for the camera feed processing script
2. Where this fits in the project architecture
3. Which existing components it should interact with
4. The intended functionality and outputs

Could you provide more details about:
- The purpose of this script
- Where it fits in the project structure
- What specific processing it should perform
- How it relates to the modules defined in our architecture

This will help me create a solution that aligns with our project standards and architecture.
```

## Conclusion

Following these guidelines ensures that AI assistants contribute effectively to the Arkos AI project, maintaining consistency and quality across all aspects of development. These guidelines should be updated as the project evolves and new best practices emerge.
