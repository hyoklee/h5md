import h5py
import numpy as np
import os
from datetime import datetime
from typing import Dict, Any, Optional
import json

class HDF5Stats:
    def __init__(self, dataset):
        self.shape = dataset.shape
        self.dtype = str(dataset.dtype)
        self.size = dataset.size
        self.memory_size = dataset.size * dataset.dtype.itemsize
        self.compression = dataset.compression
        self.compression_opts = dataset.compression_opts
        self.chunks = dataset.chunks
        
        # Get numerical statistics if applicable
        self.numeric_stats = {}
        if np.issubdtype(dataset.dtype, np.number):
            try:
                data = dataset[()]
                self.numeric_stats = {
                    'min': float(np.min(data)),
                    'max': float(np.max(data)),
                    'mean': float(np.mean(data)),
                    'median': float(np.median(data)),
                    'std': float(np.std(data)),
                    'unique_values': int(len(np.unique(data)))
                }
            except:
                pass

def format_size(size_bytes: int) -> str:
    """Convert size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def preview_data(dataset, max_elements: int = 5) -> str:
    """Generate a smart preview of the dataset content"""
    try:
        if dataset.size <= max_elements:
            return str(dataset[()])
        elif len(dataset.shape) == 1:
            return f"{str(dataset[:max_elements])[:-1]}, ...]"
        else:
            # For 2D arrays, show first few rows and columns
            if len(dataset.shape) == 2:
                rows = min(3, dataset.shape[0])
                cols = min(3, dataset.shape[1])
                preview = dataset[:rows, :cols]
                return f"First {rows}x{cols} elements:\n{preview}"
            return f"Array shape: {dataset.shape}"
    except:
        return "Unable to preview data"

def generate_toc(markdown_lines):
    """Generate table of contents from markdown headings"""
    toc = ["# Table of Contents\n"]
    for line in markdown_lines:
        if line.startswith('#'):
            level = line.count('#') - 1
            title = line.strip('#').strip()
            # Create anchor link
            anchor = title.lower().replace(' ', '-').replace('`', '').replace(':', '')
            toc.append(f"{'  ' * (level-1)}- [{title}](#{anchor})")
    return '\n'.join(toc)

def generate_advanced_markdown(file_path: str, max_preview: int = 5) -> str:
    markdown = []
    stats: Dict[str, Any] = {
        'total_groups': 0,
        'total_datasets': 0,
        'total_size': 0,
        'compressed_datasets': 0
    }
    
    def add_line(text: str, indent: int = 0) -> None:
        markdown.append("    " * indent + text)
    
    def process_attrs(item, indent: int = 0) -> None:
        if len(item.attrs) > 0:
            add_line("📝 **Attributes:**", indent)
            attr_table = ["| Name | Value | Type |", "|------|--------|------|"]
            for key, value in sorted(item.attrs.items()):
                attr_table.append(f"| `{key}` | `{value}` | _{type(value).__name__}_ |")
            for line in attr_table:
                add_line(line, indent + 1)
            add_line("", indent)
    
    def process_group(group, indent: int = 0) -> None:
        stats['total_groups'] += 1
        process_attrs(group, indent)
        
        # Sort items by type (groups first) and name
        items = sorted(group.items(), key=lambda x: (not isinstance(x[1], h5py.Group), x[0]))
        
        for name, item in items:
            if isinstance(item, h5py.Dataset):
                stats['total_datasets'] += 1
                dataset_stats = HDF5Stats(item)
                stats['total_size'] += dataset_stats.memory_size
                
                if dataset_stats.compression:
                    stats['compressed_datasets'] += 1
                
                add_line(f"### 📊 Dataset: `{name}`", indent)
                
                # Basic Properties
                add_line("#### 📋 Properties:", indent + 1)
                properties = [
                    "| Property | Value |",
                    "|----------|--------|",
                    f"| Shape | `{dataset_stats.shape}` |",
                    f"| Type | `{dataset_stats.dtype}` |",
                    f"| Size in memory | `{format_size(dataset_stats.memory_size)}` |",
                    f"| Chunks | `{dataset_stats.chunks}` |",
                    f"| Compression | `{dataset_stats.compression or 'None'}` |"
                ]
                if dataset_stats.compression_opts:
                    properties.append(f"| Compression options | `{dataset_stats.compression_opts}` |")
                
                for line in properties:
                    add_line(line, indent + 1)
                add_line("", indent + 1)
                
                # Numerical Statistics
                if dataset_stats.numeric_stats:
                    add_line("#### 📈 Statistics:", indent + 1)
                    stats_table = [
                        "| Metric | Value |",
                        "|--------|--------|",
                        f"| Minimum | `{dataset_stats.numeric_stats['min']:.3f}` |",
                        f"| Maximum | `{dataset_stats.numeric_stats['max']:.3f}` |",
                        f"| Mean | `{dataset_stats.numeric_stats['mean']:.3f}` |",
                        f"| Median | `{dataset_stats.numeric_stats['median']:.3f}` |",
                        f"| Std Dev | `{dataset_stats.numeric_stats['std']:.3f}` |",
                        f"| Unique Values | `{dataset_stats.numeric_stats['unique_values']}` |"
                    ]
                    for line in stats_table:
                        add_line(line, indent + 1)
                    add_line("", indent + 1)
                
                # Data Preview
                add_line("#### 👁️ Preview:", indent + 1)
                add_line("```", indent + 1)
                add_line(preview_data(item, max_preview), indent + 1)
                add_line("```", indent + 1)
                add_line("", indent + 1)
                
                process_attrs(item, indent + 1)
            
            elif isinstance(item, h5py.Group):
                add_line(f"## 📁 Group: `{name}`", indent)
                process_group(item, indent + 1)
    
    try:
        # Get file information
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        file_ctime = os.path.getctime(file_path)
        
        # File header
        add_line(f"# 📦 HDF5 File: `{os.path.basename(file_path)}`\n")
        
        # File Information
        add_line("## 📑 File Information")
        file_info = [
            "| Property | Value |",
            "|----------|--------|",
            f"| Size on disk | `{format_size(file_size)}` |",
            f"| Last modified | `{datetime.fromtimestamp(file_mtime)}` |",
            f"| Created | `{datetime.fromtimestamp(file_ctime)}` |"
        ]
        for line in file_info:
            add_line(line)
        add_line("")
        
        with h5py.File(file_path, 'r') as f:
            add_line("## 🌳 File Structure")
            process_group(f)
        
        # Add summary statistics
        add_line("\n## 📊 Summary Statistics")
        summary = [
            "| Metric | Value |",
            "|--------|--------|",
            f"| Total Groups | `{stats['total_groups']}` |",
            f"| Total Datasets | `{stats['total_datasets']}` |",
            f"| Total Data Size | `{format_size(stats['total_size'])}` |",
            f"| Compressed Datasets | `{stats['compressed_datasets']}` |",
            f"| Compression Ratio | `{(file_size / stats['total_size']):.2f}x` |"
        ]
        for line in summary:
            add_line(line)
        
        # Generate and insert table of contents at the beginning
        content = '\n'.join(markdown)
        toc = generate_toc(markdown)
        return f"{toc}\n\n{content}"
        
    except Exception as e:
        return f"❌ Error processing HDF5 file: {str(e)}"

# Process the sample file
output = generate_advanced_markdown('sample.h5')

# Save the output
with open('sample_output.md', 'w', encoding='utf-8') as f:
    f.write(output)

print("Generated advanced markdown output in sample_output.md")
