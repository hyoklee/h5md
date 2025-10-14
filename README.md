# HDF5 to Markdown Converter

A command-line tool to convert HDF5 files to AI-friendly markdown format with key-value structure. This tool helps you visualize the structure, metadata, and actual data from HDF5 files in a format optimized for both human readability and AI consumption.

## Features

- **AI-friendly key-value format** - Structured output optimized for AI parsing
- **Smart data subsetting** - Preview large datasets with configurable row/column limits
- **Multiple sampling strategies** - Choose how to sample data: first, uniform, or edges
- **Flexible data preview** - Include or exclude actual data values
- **Complete metadata** - Display file structure, groups, datasets, and attributes
- **External link support** - Detect and display HDF5 external links
- **Compression info** - Show dataset compression and chunking details

## Installation

```bash
# Clone the repository
git clone https://github.com/hyoklee/h5md.git
cd h5md

# Install in development mode
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/hyoklee/h5md.git
```

## Usage

### Command Line

**Basic conversion** (uses defaults: 10 rows/cols, 'first' sampling):

```bash
h5md input.h5
```

This will create `input.md` in the same directory.

**Custom output path:**

```bash
h5md input.h5 -o output.md
```

**Control data subsetting:**

```bash
# Limit to 5 rows and 5 columns
h5md input.h5 --max-rows 5 --max-cols 5

# Show all data (use carefully with large files!)
h5md input.h5 --max-rows 0 --max-cols 0

# Metadata only (no data values)
h5md input.h5 --no-data
```

**Choose sampling strategy:**

```bash
# Take first N items (default)
h5md input.h5 --sampling first

# Sample uniformly across dataset
h5md input.h5 --sampling uniform

# Show first and last items (useful for ranges)
h5md input.h5 --sampling edges
```

**Combined options:**

```bash
h5md data.h5 -o output.md --max-rows 20 --max-cols 10 --sampling edges
```

### Python API

```python
from h5md import HDF5Converter

# Basic conversion with defaults
converter = HDF5Converter()
markdown_content = converter.convert('input.h5', 'output.md')

# Advanced: customize subsetting and sampling
converter = HDF5Converter(
    max_rows=20,           # Limit to 20 rows per dataset
    max_cols=15,           # Limit to 15 columns per dataset
    sampling_strategy="edges",  # Show first and last items
    include_data_preview=True   # Include actual data values
)
markdown_content = converter.convert('data.h5', 'output.md')

# Metadata only (no data values)
converter = HDF5Converter(include_data_preview=False)
markdown_content = converter.convert('data.h5', 'metadata.md')
```

## Output Format

The generated markdown uses an AI-friendly key-value structure that includes:

1. **File-level attributes** - Metadata about the HDF5 file
2. **Group hierarchy** - Nested structure with group attributes
3. **Dataset properties** - Shape, data type, size, compression, chunks
4. **Dataset attributes** - Custom metadata for each dataset
5. **Data preview** - Actual data values in key-value format (configurable)
6. **External links** - Target file and path information

### Sample Key-Value Markdown Output

```markdown
# HDF5 File Structure: example.h5

## Attributes

- **title:** `Sample Scientific Dataset` (type: `str`)
- **version:** `1.0` (type: `str`)

## Group: /measurements

### Attributes

- **description:** `Experimental measurements` (type: `str`)

### Dataset: temperature

#### Properties

- **Shape:** `(100,)`
- **Data Type:** `float64`
- **Size:** `100` elements

**Data (Key-Value Format):**

- `index_0`: `22.935992117831265`
- `index_1`: `23.308188819527796`
- `index_2`: `20.582239974390227`
- `index_3`: `20.184652272470018`
- `index_4`: `23.397532910900622`
- *(showing 5 of 100 rows using 'first' sampling)*

#### Attributes

- **sensor:** `TH-100` (type: `str`)
- **unit:** `Celsius` (type: `str`)

### Dataset: correlation_matrix

#### Properties

- **Shape:** `(50, 20)`
- **Data Type:** `float64`
- **Size:** `1000` elements

**Data (Key-Value Format):**

- **Row 0:**
  - `col_0`: `0.175408510335`
  - `col_1`: `0.367993360963`
  - `col_2`: `0.361122287567`
- **Row 1:**
  - `col_0`: `0.504039513844`
  - `col_1`: `0.817406445579`
  - `col_2`: `0.900514954273`
- *(showing 2 of 50 rows, 3 of 20 cols using 'first' sampling)*

#### Attributes

- **description:** `Correlation coefficients` (type: `str`)
```

This format is designed to be:
- **Parseable** - Clear structure for AI to extract information
- **Readable** - Easy for humans to understand
- **Scalable** - Smart subsetting prevents overwhelming output from large datasets

## Requirements

- Python 3.10+
- h5py
- numpy

## License

BSD 3-Clause License

Copyright (c) 2025, Joe Lee
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
