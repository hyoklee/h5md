# Markitdown HDF5 Plugin

A plugin for [Markitdown](https://github.com/microsoft/markitdown/) that provides rich visualization of HDF5 file metadata, including:
- Complete group hierarchy
- Dataset information (shape, type, statistics)
- Attributes for both groups and datasets
- Interactive visualizations
- Data validation
- File comparison

## Installation

```bash
pip install .
```

## Usage

### Basic Usage

Generate markdown documentation for an HDF5 file:
```bash
h5md input.h5
```

### Interactive HTML Report

Generate an interactive HTML report with visualizations:
```bash
h5md input.h5 --format html --output-dir reports/
```

### Data Validation

Validate HDF5 file against a schema:
```bash
h5md input.h5 --validate schema.json
```

### File Comparison

Compare two HDF5 files:
```bash
h5md input.h5 --diff other.h5
```

### JSON Export

Export metadata to JSON:
```bash
h5md input.h5 --format json -o metadata.json
```

### Advanced Options

```bash
h5md --help
```

## Features

1. **Rich Metadata Visualization**
   - Group hierarchy
   - Dataset properties
   - Attribute information
   - Data statistics

2. **Interactive HTML Reports**
   - Dataset visualizations using Plotly
   - Interactive file structure tree
   - Statistical plots
   - Responsive design

3. **Data Validation**
   - Schema-based validation
   - Quality metrics
   - Custom validation rules
   - Detailed validation reports

4. **File Comparison**
   - Structure comparison
   - Data differences
   - Statistical analysis
   - Visual diff reports

5. **Multiple Output Formats**
   - Markdown
   - Interactive HTML
   - JSON

## Example

```bash
# Generate comprehensive HTML report with validation and comparison
h5md input.h5 \
    --format html \
    --validate schema.json \
    --diff reference.h5 \
    --output-dir reports/
```

## Development

Create a development environment:
```bash
conda env create -f environment.yml
conda activate markitdown-hdf5-dev
```

Run tests:
```bash
pytest tests/
