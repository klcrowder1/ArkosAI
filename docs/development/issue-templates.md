# Issue Templates

This document provides templates for creating issues in the Arkos AI project. These templates ensure that issues are well-defined and contain all necessary information for developers to understand and address them.

## Overview

Arkos AI uses GitHub Issues for tracking bugs, feature requests, documentation tasks, and other work items. To ensure consistency and completeness, we use issue templates for different types of issues.

## Issue Types

We have the following issue types:

1. **Bug Report**: For reporting bugs or unexpected behavior
2. **Feature Request**: For requesting new features or enhancements
3. **Documentation Task**: For documentation-related tasks
4. **Refactoring Task**: For code refactoring tasks
5. **Testing Task**: For testing-related tasks
6. **Performance Issue**: For performance-related issues
7. **Security Issue**: For security-related issues

## Bug Report Template

```markdown
---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Description

A clear and concise description of the bug.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Screenshots

If applicable, add screenshots to help explain your problem.

## Environment

- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 98]
- Arkos AI Version: [e.g., 1.0.0]
- Hardware: [e.g., LattePanda Sigma]

## Additional Context

Add any other context about the problem here.

## Possible Solution

If you have a suggestion for how to fix the bug, please describe it here.
```

## Feature Request Template

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Problem Statement

A clear and concise description of the problem this feature would solve. For example, "I'm always frustrated when..."

## Proposed Solution

A clear and concise description of what you want to happen.

## Alternative Solutions

A clear and concise description of any alternative solutions or features you've considered.

## User Stories

As a [type of user], I want [some goal] so that [some reason].

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

Add any other context, screenshots, or mockups about the feature request here.

## Dependencies

List any dependencies this feature has on other features or components.
```

## Documentation Task Template

```markdown
---
name: Documentation Task
about: Tasks related to documentation
title: '[DOCS] '
labels: documentation
assignees: ''
---

## Description

A clear and concise description of the documentation task.

## Type of Documentation

- [ ] User Guide
- [ ] Developer Guide
- [ ] API Documentation
- [ ] Code Comments
- [ ] Other: [please specify]

## Scope

What parts of the documentation need to be created or updated?

## Content Outline

Provide an outline of the content to be created or updated.

## References

Provide any references or resources that would be helpful for completing this task.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

Add any other context about the documentation task here.
```

## Refactoring Task Template

```markdown
---
name: Refactoring Task
about: Tasks related to code refactoring
title: '[REFACTOR] '
labels: refactoring
assignees: ''
---

## Description

A clear and concise description of the refactoring task.

## Current Code

Describe the current code structure or provide code snippets.

## Proposed Changes

Describe the proposed changes or provide code snippets.

## Motivation

Why is this refactoring necessary?

## Benefits

What benefits will this refactoring bring?

## Risks

What are the potential risks of this refactoring?

## Testing Plan

How will the refactored code be tested?

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

Add any other context about the refactoring task here.
```

## Testing Task Template

```markdown
---
name: Testing Task
about: Tasks related to testing
title: '[TEST] '
labels: testing
assignees: ''
---

## Description

A clear and concise description of the testing task.

## Type of Testing

- [ ] Unit Testing
- [ ] Integration Testing
- [ ] System Testing
- [ ] Performance Testing
- [ ] Security Testing
- [ ] Other: [please specify]

## Scope

What parts of the system need to be tested?

## Test Cases

Provide an outline of the test cases to be created or updated.

## Test Environment

Describe the test environment required for this testing task.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

Add any other context about the testing task here.
```

## Performance Issue Template

```markdown
---
name: Performance Issue
about: Report a performance issue
title: '[PERF] '
labels: performance
assignees: ''
---

## Description

A clear and concise description of the performance issue.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. Observe performance issue

## Expected Performance

A clear and concise description of what performance you expected.

## Actual Performance

A clear and concise description of the actual performance.

## Performance Metrics

Provide any performance metrics you have collected.

## Environment

- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 98]
- Arkos AI Version: [e.g., 1.0.0]
- Hardware: [e.g., LattePanda Sigma]

## Additional Context

Add any other context about the performance issue here.

## Possible Solution

If you have a suggestion for how to fix the performance issue, please describe it here.
```

## Security Issue Template

```markdown
---
name: Security Issue
about: Report a security issue
title: '[SECURITY] '
labels: security
assignees: ''
---

## Description

A clear and concise description of the security issue.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. Observe security issue

## Potential Impact

Describe the potential impact of this security issue.

## Suggested Fix

If you have a suggestion for how to fix the security issue, please describe it here.

## Environment

- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 98]
- Arkos AI Version: [e.g., 1.0.0]
- Hardware: [e.g., LattePanda Sigma]

## Additional Context

Add any other context about the security issue here.
```

## Using Templates in GitHub

To use these templates in GitHub:

1. Create a `.github/ISSUE_TEMPLATE` directory in your repository
2. Create a separate Markdown file for each template (e.g., `bug_report.md`, `feature_request.md`)
3. Copy the template content into the corresponding file
4. Commit and push the changes to your repository

Once the templates are set up, users will be prompted to choose a template when creating a new issue.

## Template Configuration

You can also create a `config.yml` file in the `.github/ISSUE_TEMPLATE` directory to configure the issue templates:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Arkos AI Community Support
    url: https://forum.arkos.ai/
    about: Please ask and answer questions here.
  - name: Arkos AI Documentation
    url: https://docs.arkos.ai/
    about: Check the documentation for answers to common questions.
```

This configuration disables blank issues and provides links to community support and documentation.

## Conclusion

Using these issue templates will help ensure that issues are well-defined and contain all necessary information for developers to understand and address them. This will lead to more efficient issue resolution and a better overall development process.
