# Contributing to Arkos AI

Thank you for your interest in contributing to Arkos AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Community](#community)

## Code of Conduct

Arkos AI is committed to fostering an open and welcoming environment. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Git
- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- Visual Studio Code (recommended)

### Repository Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/arkos-ai.git
   cd arkos-ai
   ```
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/original-organization/arkos-ai.git
   ```
4. Create a new branch for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

Arkos AI uses Docker for development to ensure a consistent environment across different platforms. See the [Development Environment Setup](docs/development/setup.md) guide for detailed instructions.

### Quick Start

```bash
# Build and start the development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Run tests
docker-compose -f docker-compose.dev.yml exec arkos-core pytest

# Stop the development environment
docker-compose -f docker-compose.dev.yml down
```

## Contribution Workflow

1. **Select an Issue**: Start by finding an issue to work on. Issues labeled `good first issue` are a great place to start.

2. **Create a Branch**: Create a new branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   Use a descriptive branch name that reflects the changes you're making.

3. **Make Changes**: Implement your changes, following the coding standards and testing guidelines.

4. **Commit Changes**: Commit your changes with a clear and descriptive commit message:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   Follow the [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages.

5. **Keep Updated**: Regularly sync your branch with the upstream repository:
   ```bash
   git fetch upstream
   git rebase upstream/dev
   ```

6. **Push Changes**: Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**: Open a pull request from your branch to the upstream `dev` branch.

## Coding Standards

Arkos AI follows strict coding standards to ensure code quality and consistency. See the [Coding Standards](docs/development/coding-standards.md) guide for detailed information.

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Include type hints for all functions and methods
- Write docstrings for all functions, classes, and modules

### JavaScript/TypeScript Code

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [ESLint](https://eslint.org/) for linting
- Use [Prettier](https://prettier.io/) for code formatting
- Use TypeScript for type safety
- Write JSDoc comments for all functions and classes

## Testing

All contributions must include appropriate tests. See the [Testing Strategy](docs/testing/strategy.md) guide for detailed information.

### Running Tests

```bash
# Run all tests
docker-compose -f docker-compose.dev.yml exec arkos-core pytest

# Run specific tests
docker-compose -f docker-compose.dev.yml exec arkos-core pytest tests/test_specific.py

# Run tests with coverage
docker-compose -f docker-compose.dev.yml exec arkos-core pytest --cov=arkos
```

### Test Requirements

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Maintain or improve test coverage
- Include both positive and negative test cases
- Mock external dependencies

## Documentation

Documentation is a crucial part of Arkos AI. All contributions should include appropriate documentation updates.

### Documentation Types

- **Code Documentation**: Docstrings, comments, and type hints
- **API Documentation**: Documentation for API endpoints
- **User Documentation**: User guides and tutorials
- **Developer Documentation**: Development guides and architecture documentation

### Documentation Guidelines

- Write clear and concise documentation
- Include examples where appropriate
- Keep documentation up-to-date with code changes
- Follow the documentation structure and format

## Pull Request Process

1. **Create a Pull Request**: Open a pull request from your branch to the upstream `dev` branch.

2. **Pull Request Template**: Fill out the pull request template with all required information.

3. **Continuous Integration**: Ensure all CI checks pass.

4. **Code Review**: Address any feedback from code reviewers.

5. **Approval**: Pull requests require approval from at least one maintainer.

6. **Merge**: Once approved, a maintainer will merge your pull request.

### Pull Request Checklist

- [ ] Code follows the style guidelines
- [ ] Code passes all tests
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow the Conventional Commits format
- [ ] Changes are rebased on the latest `dev` branch

## Issue Reporting

If you find a bug or have a suggestion for improvement, please open an issue on GitHub.

### Issue Template

When opening an issue, please use the appropriate issue template and provide as much information as possible:

- **Bug Reports**: Include steps to reproduce, expected behavior, actual behavior, and environment details
- **Feature Requests**: Include a clear description of the feature, use cases, and benefits
- **Questions**: Include a clear question and any relevant context

## Feature Requests

Feature requests are welcome! Please use the feature request template when opening an issue for a new feature.

### Feature Request Guidelines

- Clearly describe the feature and its benefits
- Provide use cases for the feature
- Consider the impact on existing functionality
- Be open to discussion and feedback

## Community

Arkos AI is a community project, and we value all contributions. Here are some ways to get involved:

- **Discord**: Join our [Discord server](https://discord.gg/arkos-ai) for real-time discussion
- **Forum**: Participate in discussions on our [forum](https://forum.arkos.ai/)
- **GitHub Discussions**: Ask questions and share ideas in [GitHub Discussions](https://github.com/original-organization/arkos-ai/discussions)
- **Contributing**: Submit pull requests for bug fixes and features
- **Documentation**: Help improve the documentation
- **Testing**: Test new features and report bugs

## License

By contributing to Arkos AI, you agree that your contributions will be licensed under the project's license.

## Acknowledgments

Thank you to all the contributors who have helped make Arkos AI better!
