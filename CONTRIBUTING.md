# Contributing to KPI Pipeline

Thank you for your interest in contributing to the KPI Pipeline project! This document provides guidelines for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Reporting Bugs](#reporting-bugs)
4. [Suggesting Features](#suggesting-features)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Development Setup](#development-setup)

---

## Code of Conduct

This project adheres to a Code of Conduct that we expect all contributors to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as GitHub issues. Before creating a bug report, please:

1. **Check existing issues** - Your bug may already be reported
2. **Use the latest version** - The bug may already be fixed
3. **Verify it's reproducible** - Can you consistently reproduce it?

**When creating a bug report, include**:

- **Clear title** - Describe the issue concisely
- **Detailed description** - What happened vs. what you expected
- **Steps to reproduce** - Numbered list of exact steps
- **Environment details** - Python version, OS, package versions
- **Error messages** - Full error output/stack trace
- **Sample data** - If possible (anonymized)

**Use the bug report template** when creating an issue.

### Suggesting Features

Feature requests are welcome! Before suggesting:

1. **Check if it's already planned** - Review roadmap and existing issues
2. **Consider the scope** - Does it fit the project goals?
3. **Think about the users** - Who benefits and how?

**When suggesting a feature, include**:

- **Clear title** - What feature you'd like
- **Use case** - Why is this needed?
- **Proposed solution** - How might it work?
- **Alternatives considered** - Other approaches?
- **Additional context** - Screenshots, examples, etc.

**Use the feature request template** when creating an issue.

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or clarify wording
- Add examples or use cases
- Improve installation instructions
- Translate documentation

**Documentation files**:
- `README.md` - Project overview
- `docs/*.md` - Detailed documentation
- Code docstrings - In-code documentation

---

## Code Style Guidelines

### Python Style (PEP 8)

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some specific guidelines:

**General Rules**:
- Use 4 spaces for indentation (not tabs)
- Line length: 88 characters (Black default)
- Use meaningful variable names
- Add docstrings to all functions and classes

**Example**:

```python
def calculate_kpi(data, config):
    """
    Calculate KPI metrics from data.
    
    Args:
        data (pd.DataFrame): Input data
        config (dict): Configuration dictionary
        
    Returns:
        dict: KPI results with adherence rate and status
        
    Raises:
        ValueError: If required columns are missing
    """
    # Implementation here
    pass
```

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

**Examples**:
```python
# Good
def load_incidents(file_path, config):
    pass

class KPICalculator:
    pass

MAX_RETRIES = 3

def _internal_helper():
    pass

# Bad
def LoadIncidents(filePath, Config):  # Wrong case
    pass
```

### Imports

Order imports as follows:

```python
# 1. Standard library
import sys
from datetime import datetime

# 2. Third-party packages
import pandas as pd
import yaml

# 3. Local modules
from src import config_loader
from src import load_data
```

### Documentation

**Module docstring**:
```python
"""
Module for calculating KPI metrics.

This module provides functions for calculating various KPIs
from incident and request data.
"""
```

**Function docstring**:
```python
def calculate_sm001(incidents, config):
    """
    Calculate SM001: Major Incident Management KPI.
    
    Tracks P1 and P2 incidents against defined targets.
    
    Args:
        incidents (pd.DataFrame): Incident data with priority field
        config (dict): Configuration with targets and thresholds
        
    Returns:
        dict: KPI results including:
            - KPI_Code: 'SM001'
            - KPI_Name: Full KPI name
            - Adherence_Rate: Percentage adherence
            - Status: Meeting Target / Needs Improvement / Below Target
            - Business_Impact: Low / Medium / High
            - P1_Count: Number of P1 incidents
            - P2_Count: Number of P2 incidents
            
    Example:
        >>> config = load_config()
        >>> incidents = load_incidents('data.csv', config)
        >>> result = calculate_sm001(incidents, config)
        >>> print(result['Adherence_Rate'])
        95.5
    """
    pass
```

### Testing

**Write tests for**:
- All new features
- Bug fixes
- Edge cases

**Test structure**:
```python
def test_calculate_sm001_basic():
    """Test SM001 calculation with standard data."""
    # Arrange
    incidents = create_test_incidents()
    config = create_test_config()
    
    # Act
    result = calculate_sm001(incidents, config)
    
    # Assert
    assert result['KPI_Code'] == 'SM001'
    assert result['Adherence_Rate'] >= 0
    assert result['Adherence_Rate'] <= 100
```

---

## Pull Request Process

### Before Submitting

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clear, focused commits
   - Follow code style guidelines
   - Add/update tests
   - Update documentation

3. **Test your changes**:
   ```bash
   # Run validation
   python validate_project.py
   
   # Run test suite
   python tests/test_pipeline.py
   
   # Test with real data
   python main.py
   ```

4. **Update CHANGELOG.md** (if applicable):
   ```markdown
   ## [Unreleased]
   
   ### Added
   - Your new feature
   ```

5. **Commit with clear messages**:
   ```bash
   git commit -m "feat(kpi): Add SM005 calculation
   
   Implemented new KPI for response time tracking.
   Includes tests and documentation.
   
   Closes #15"
   ```

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**:
   - Go to the repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

3. **PR Title Format**:
   ```
   feat(scope): Brief description
   fix(scope): Brief description
   docs(scope): Brief description
   ```

4. **PR Description Should Include**:
   - Summary of changes
   - Motivation/context
   - Type of change (bug fix, feature, etc.)
   - Testing performed
   - Related issues
   - Screenshots (if UI changes)

### Code Review Expectations

**As a contributor**:
- Respond to feedback promptly
- Be open to suggestions
- Make requested changes
- Keep PR focused and manageable

**Reviews focus on**:
- Code quality and correctness
- Test coverage
- Documentation completeness
- Style consistency
- Performance implications

### After Approval

1. **Squash commits if needed**:
   ```bash
   git rebase -i HEAD~3
   ```

2. **Maintainer will merge**:
   - Usually via "Squash and merge"
   - PR will be closed automatically
   - Branch will be deleted

3. **Update your local repository**:
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/your-feature-name
   ```

---

## Development Setup

### Initial Setup

1. **Fork and clone**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/kpi-pipeline.git
   cd kpi-pipeline
   ```

2. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/kpi-pipeline.git
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install development dependencies** (optional):
   ```bash
   pip install black flake8 pytest
   ```

### Development Workflow

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes and test**:
   ```bash
   # Make your changes
   
   # Run tests
   python tests/test_pipeline.py
   
   # Check style (if using)
   black src/
   flake8 src/
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: My feature"
   git push origin feature/my-feature
   ```

5. **Create pull request** on GitHub

### Running Tests

```bash
# Run all tests
python tests/test_pipeline.py

# Run specific test
python -c "from tests.test_pipeline import test_config_loading; test_config_loading()"

# Generate and test with sample data
python tests/generate_sample_data.py
python tests/test_pipeline.py
```

### Code Formatting (Optional)

```bash
# Format code with Black
black src/ tests/

# Check style with flake8
flake8 src/ tests/
```

---

## Project Structure

Understanding the codebase:

```
kpi_pipeline/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config_loader.py    # Configuration management
│   ├── load_data.py        # Data loading
│   ├── transform.py        # Data transformation
│   └── calculate_kpis.py   # KPI calculations
├── tests/                  # Test suite
│   ├── test_pipeline.py
│   └── generate_sample_data.py
├── config/                 # Configuration files
│   └── kpi_config.yaml
├── docs/                   # Documentation
│   └── *.md
└── main.py                 # Entry point
```

---

## Need Help?

- **Questions?** Open an issue with the "question" label
- **Discussion?** Use GitHub Discussions (if enabled)
- **Contact?** See README.md for contact information

---

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors page
- Release notes (for significant contributions)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** Every contribution, no matter how small, helps improve the project. 🎉



