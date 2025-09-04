# Contributing to AI Fitness Coach

Thank you for your interest in contributing to the AI Fitness Coach project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Code Style](#code-style)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/AI-Fitness.git
   cd AI-Fitness
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/original-owner/AI-Fitness.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)

### Environment Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Fixes**: Fix existing issues
2. **Feature Additions**: Add new functionality
3. **Documentation**: Improve or add documentation
4. **Testing**: Add or improve tests
5. **Performance**: Optimize existing code
6. **UI/UX**: Improve user interface and experience

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** for significant changes to discuss the approach
3. **Fork the repository** and create a feature branch

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/

# Run linting
flake8 .
black --check .

# Run type checking (if applicable)
mypy .
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: real-time pose tracking with voice feedback"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots (for UI changes)
- Testing instructions

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, etc.)
5. **Screenshots** or error messages
6. **Log files** (if applicable)

### Feature Requests

For feature requests, please include:

1. **Clear description** of the feature
2. **Use case** and motivation
3. **Proposed implementation** (if you have ideas)
4. **Alternative solutions** considered

## Development Workflow

### Branch Naming Convention

- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `test/description`: Test improvements
- `refactor/description`: Code refactoring

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat(pose): add real-time pose tracking
fix(api): resolve video upload timeout issue
docs(readme): update installation instructions
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Write tests for new functionality
- Aim for good test coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

Example test structure:

```python
def test_video_analysis_success():
    """Test successful video analysis"""
    # Arrange
    mock_video = create_mock_video()
    
    # Act
    result = analyzer.analyze_video(mock_video)
    
    # Assert
    assert result['success'] == True
    assert 'analysis' in result
```

## Documentation

### Code Documentation

- Use docstrings for functions and classes
- Follow Google docstring format
- Include type hints where appropriate
- Add inline comments for complex logic

Example:

```python
def analyze_form_quality(exercise_type: str, features: dict, coords: dict) -> dict:
    """
    Analyze form quality for a specific exercise.
    
    Args:
        exercise_type: Type of exercise being performed
        features: Extracted features from pose landmarks
        coords: Coordinate data for landmarks
        
    Returns:
        Dictionary containing analysis results with scores and recommendations
        
    Raises:
        ValueError: If exercise_type is not supported
    """
    # Implementation here
```

### README Updates

- Update README.md for significant changes
- Include installation instructions
- Add usage examples
- Update feature list

## Code Style

### Python Style

We follow PEP 8 with some modifications:

- Line length: 127 characters
- Use Black for code formatting
- Use flake8 for linting
- Use type hints where appropriate

### Formatting

```bash
# Format code with Black
black .

# Check formatting
black --check .

# Lint with flake8
flake8 .
```

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List

# Third-party imports
import cv2
import numpy as np
from flask import Flask

# Local imports
from features import extract_comprehensive_features
from smart_coach import SmartCoach
```

## Review Process

### Pull Request Review

1. **Automated checks** must pass (tests, linting, formatting)
2. **Code review** by maintainers
3. **Testing** by reviewers
4. **Documentation** review
5. **Approval** and merge

### Review Criteria

- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Security considerations
- Backward compatibility

## Release Process

1. **Version bump** in appropriate files
2. **Update changelog**
3. **Create release notes**
4. **Tag release** in Git
5. **Deploy** to production

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check existing docs first
- **Code Comments**: Read inline code documentation

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to AI Fitness Coach! 🏋️‍♂️
