# CI/CD Pipeline for Arkos AI

This directory contains the GitHub Actions workflows that make up the CI/CD pipeline for the Arkos AI project.

## Workflows

### Continuous Integration (`ci.yml`)

This workflow runs on pushes to the `dev` and `master` branches, and on manual triggers. It builds and tests the Arkos AI application for multiple architectures and platforms.

Key features:
- Builds for AMD64 and ARM64 architectures
- Specialized builds for Raspberry Pi, Rockchip, and Jetson platforms
- Publishes Docker images to GitHub Container Registry
- Creates multi-architecture manifests

### Pull Request Checks (`pull_request.yml`)

This workflow runs on pull requests to verify that the changes meet the project's quality standards.

Key features:
- Builds the development container
- Lints and tests the web frontend
- Runs Python code formatting and linting checks
- Runs unit tests

### Documentation (`documentation.yml`)

This workflow builds and deploys the project documentation.

Key features:
- Builds documentation on changes to the `docs/` directory
- Deploys documentation to GitHub Pages on pushes to `dev` and `master`
- Validates documentation during pull requests

### Release (`release.yml`)

This workflow runs when a new release is published on GitHub.

Key features:
- Tags and pushes Docker images with version numbers
- Creates stable tags for release versions
- Publishes Docker images for all supported architectures and platforms

### Branch Protection (`branch-protection.yml`)

This workflow applies branch protection rules to the repository.

Key features:
- Configures required status checks for protected branches
- Sets up pull request review requirements
- Prevents force pushes and deletions on protected branches

## Configuration

The CI/CD pipeline is configured through the following files:

- `.github/branch-protection.yml`: Defines branch protection rules
- `.github/actions/setup/action.yml`: Sets up common build environment
- `docker/*/Dockerfile`: Docker build configurations for different platforms

## Required Secrets

The following secrets are required for the workflows to function properly:

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `ADMIN_TOKEN`: A personal access token with admin permissions (for branch protection)

## Adding a New Workflow

To add a new workflow:

1. Create a new YAML file in the `.github/workflows/` directory
2. Define the workflow triggers, jobs, and steps
3. Test the workflow using the `workflow_dispatch` trigger
4. Document the workflow in this README

## Best Practices

- Keep workflows focused on a single responsibility
- Reuse steps and jobs where possible
- Use the latest versions of actions
- Pin action versions to specific commits for stability
- Document workflow changes in pull requests
