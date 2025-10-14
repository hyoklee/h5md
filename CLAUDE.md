# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests with coverage
pytest tests/ --cov=h5md --cov-report=xml

# Run a single test file
pytest tests/test_hdf5_plugin.py

# Run tests with verbose output
pytest -v tests/
```

### Code Quality
```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8 . --count --show-source --statistics

# Type checking
mypy h5md/

# Run all linting checks (as done in CI)
black --check . && isort --check-only --diff . && flake8 . && mypy h5md/
```

### Building and Installation
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Build package
python -m build

# Check built package
twine check dist/*
```

### Environment Setup
```bash
# Using conda (recommended)
conda env create -f environment.yml
conda activate h5md-dev

# Using pip
pip install -r requirements.txt
```

## Architecture Overview

### Core Components

This is a Python package that converts HDF5 files to markdown format. The architecture consists of:

**Main Converter (`h5md/__init__.py`)**
- `HDF5Converter` class: Core conversion logic
- Handles recursive traversal of HDF5 file structure (groups, datasets, attributes)
- Supports HDF5 external links
- Generates markdown with formatted tables for metadata

**CLI Interface (`h5md/cli.py`)**
- Command-line entry point via `h5md` command
- Argument parsing for input/output file paths
- Error handling and user feedback

**Key Features:**
- Recursive processing of HDF5 groups and datasets
- Dynamic markdown header levels based on nesting depth
- Attribute formatting with type detection (numpy types, bytes, arrays)
- External link support showing target file and path
- Dataset property tables (shape, dtype, compression)

### File Structure
```
h5md/
├── __init__.py          # HDF5Converter class and core logic
└── cli.py              # Command-line interface

tests/
└── test_hdf5_plugin.py  # Test suite with fixtures for HDF5 files
```

### Dependencies
- **h5py**: HDF5 file reading
- **numpy**: Array and type handling
- **pytest**: Testing framework with coverage support

### Development Workflow
The project uses a complete CI/CD pipeline with:
- Multi-platform testing (Linux, macOS, Windows)
- Python 3.10+ support
- Code formatting (black, isort)
- Linting (flake8) and type checking (mypy)
- Package building and conda distribution