# HDF5 to Markdown Converter

A simple command-line tool to convert HDF5 files to markdown format. This tool helps you visualize the structure, metadata, and attributes of HDF5 files in a human-readable markdown format.

## Features

- Convert HDF5 files to markdown format
- Display file structure including groups and datasets
- Show dataset properties (shape, type)
- List attributes for groups and datasets
- Clean and readable markdown output

## Installation

```bash
pip install hdf5-to-markdown
```

## Usage

### Command Line

Convert an HDF5 file to markdown:

```bash
h5md input.h5
```

This will create `input.md` in the same directory. You can also specify a custom output path:

```bash
h5md input.h5 -o output.md
```

### Python API

```python
from markitdown_hdf5 import HDF5Converter

# Create a converter
converter = HDF5Converter()

# Convert HDF5 to markdown
markdown_content = converter.convert('input.h5')

# Save to file
with open('output.md', 'w') as f:
    f.write(markdown_content)
```

## Output Format

The generated markdown file includes:

1. File structure with groups and datasets
2. Dataset properties (shape, type)
3. Group and dataset attributes
4. Nicely formatted tables for metadata

Example output:

```markdown
# HDF5 File Structure: input.h5

## Group: data
### Attributes:
| Name | Value | Type |
|------|--------|------|
| `purpose` | `testing` | `str` |

### Dataset: array
| Property | Value |
|----------|--------|
| Shape | `(3,)` |
| Type | `float64` |

#### Dataset Attributes:
| Name | Value | Type |
|------|--------|------|
| `unit` | `meters` | `str` |
```

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
