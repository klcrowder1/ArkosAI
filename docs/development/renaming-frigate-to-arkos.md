# Renaming Frigate to Arkos

This document outlines the process for renaming the "frigate" module to "arkos" throughout the codebase as part of the camera integration refactoring.

## Overview

The project has been renamed from Frigate to Arkos AI, but the codebase still uses the "frigate" namespace. As part of the camera integration refactoring, we will rename the "frigate" module to "arkos" to align with the new project name.

## Renaming Process

### 1. Directory Structure

1. Create a new `arkos` directory at the root level
2. Copy the existing directory structure from `frigate` to `arkos`
3. Update imports in all files to use `arkos` instead of `frigate`

### 2. Module Imports

Update all import statements in the codebase to use the new module name:

```python
# Before
from frigate.camera import CameraMetrics

# After
from arkos.camera import CameraMetrics
```

### 3. Class and Function Names

Update any class or function names that include "frigate" to use "arkos" instead:

```python
# Before
class FrigateApp:
    # ...

# After
class ArkosApp:
    # ...
```

### 4. Configuration Keys

Update any configuration keys that include "frigate" to use "arkos" instead:

```python
# Before
config = {
    "frigate": {
        # ...
    }
}

# After
config = {
    "arkos": {
        # ...
    }
}
```

### 5. Environment Variables

Update any environment variables that include "FRIGATE" to use "ARKOS" instead:

```python
# Before
os.environ.get("FRIGATE_VAR", default_value)

# After
os.environ.get("ARKOS_VAR", default_value)
```

### 6. Documentation

Update all documentation to use "Arkos" instead of "Frigate":

```markdown
<!-- Before -->
# Frigate Camera Integration

<!-- After -->
# Arkos Camera Integration
```

### 7. Comments

Update all comments to use "Arkos" instead of "Frigate":

```python
# Before
# This is a Frigate-specific implementation

# After
# This is an Arkos-specific implementation
```

### 8. Process Names

Update any process names that include "frigate" to use "arkos" instead:

```python
# Before
setproctitle(f"frigate.capture:{name}")

# After
setproctitle(f"arkos.capture:{name}")
```

## Implementation Strategy

To minimize the risk of breaking changes, we will implement the renaming in phases:

### Phase 1: Create New Module Structure

1. Create the new `arkos` directory structure
2. Copy the camera module files to the new structure
3. Update imports in the camera module files

### Phase 2: Update References

1. Update references to the camera module in other files
2. Update class and function names
3. Update configuration keys
4. Update environment variables

### Phase 3: Testing

1. Test the new module structure
2. Test the updated references
3. Fix any issues discovered during testing

### Phase 4: Cleanup

1. Remove the old `frigate` camera module files
2. Update documentation
3. Update comments

## Backward Compatibility

To maintain backward compatibility during the transition, we can:

1. Create alias imports in the old `frigate` module that point to the new `arkos` module:

```python
# frigate/camera/__init__.py
from arkos.camera import CameraMetrics, PTZMetrics, CameraActivityManager, CameraState, CameraManager

__all__ = [
    "CameraMetrics",
    "PTZMetrics",
    "CameraActivityManager",
    "CameraState",
    "CameraManager",
]
```

2. Add deprecation warnings to the old imports:

```python
import warnings

warnings.warn(
    "The 'frigate' module is deprecated and will be removed in a future version. "
    "Please use 'arkos' instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

## File Renaming Checklist

Here's a checklist of files that need to be renamed:

- [ ] `frigate/__init__.py` → `arkos/__init__.py`
- [ ] `frigate/app.py` → `arkos/app.py`
- [ ] `frigate/camera/__init__.py` → `arkos/camera/__init__.py`
- [ ] `frigate/camera/activity_manager.py` → `arkos/camera/activity.py`
- [ ] `frigate/camera/state.py` → `arkos/camera/state.py`
- [ ] `frigate/video.py` → `arkos/camera/capture.py` and `arkos/camera/processing.py`

## Import Update Checklist

Here's a checklist of import statements that need to be updated:

- [ ] `from frigate.camera import ...` → `from arkos.camera import ...`
- [ ] `from frigate.video import ...` → `from arkos.camera.capture import ...` or `from arkos.camera.processing import ...`
- [ ] `from frigate.app import ...` → `from arkos.app import ...`
- [ ] `import frigate.camera` → `import arkos.camera`
- [ ] `import frigate.video` → `import arkos.camera.capture` or `import arkos.camera.processing`
- [ ] `import frigate.app` → `import arkos.app`

## Conclusion

Renaming the "frigate" module to "arkos" is an important step in aligning the codebase with the new project name. By following this process, we can ensure a smooth transition with minimal disruption to the existing functionality.
