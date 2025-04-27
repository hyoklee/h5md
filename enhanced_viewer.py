import os
from datetime import datetime

import h5py
import numpy as np


def format_size(size_bytes):
    """Convert size in bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_dataset_stats(dataset):
    """Get basic statistics for numeric datasets"""
    try:
        if np.issubdtype(dataset.dtype, np.number):
            data = dataset[()]
            return {
                "min": np.min(data),
                "max": np.max(data),
                "mean": np.mean(data),
                "size": dataset.size,
            }
    except:
        pass
    return None


def generate_enhanced_markdown(file_path):
    markdown = []

    def add_line(text, indent=0):
        markdown.append("    " * indent + text)

    def process_attrs(item, indent=0):
        if len(item.attrs) > 0:
            add_line("📝 **Attributes:**", indent)
            for key, value in item.attrs.items():
                add_line(
                    f"- `{key}`: `{value}` (_type: {type(value).__name__}_)", indent + 1
                )

    def preview_data(dataset, max_elements=5):
        """Generate a preview of the dataset content"""
        try:
            if dataset.size <= max_elements:
                return str(dataset[()])
            elif len(dataset.shape) == 1:
                return f"{str(dataset[:max_elements])[:-1]}, ...]"
            else:
                return "Array too large for preview"
        except:
            return "Unable to preview data"

    def process_group(group, indent=0):
        process_attrs(group, indent)

        for name, item in sorted(group.items()):
            if isinstance(item, h5py.Dataset):
                add_line(f"### 📊 Dataset: `{name}`", indent)
                add_line("#### Properties:", indent + 1)
                add_line(f"- Shape: `{item.shape}`", indent + 1)
                add_line(f"- Type: `{item.dtype}`", indent + 1)
                add_line(
                    f"- Size in memory: `{format_size(item.size * item.dtype.itemsize)}`",
                    indent + 1,
                )

                # Add statistics for numeric datasets
                stats = get_dataset_stats(item)
                if stats:
                    add_line("#### Statistics:", indent + 1)
                    add_line(f"- Min: `{stats['min']:.3f}`", indent + 1)
                    add_line(f"- Max: `{stats['max']:.3f}`", indent + 1)
                    add_line(f"- Mean: `{stats['mean']:.3f}`", indent + 1)

                # Add data preview
                add_line("#### Preview:", indent + 1)
                add_line(f"```\n{preview_data(item)}\n```", indent + 1)

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
        add_line(f"# 📦 HDF5 File: `{os.path.basename(file_path)}`")
        add_line("\n## File Information:")
        add_line(f"- 📏 Size: `{format_size(file_size)}`")
        add_line(f"- 🕒 Last modified: `{datetime.fromtimestamp(file_mtime)}`")
        add_line(f"- 📅 Created: `{datetime.fromtimestamp(file_ctime)}`")
        add_line("")

        with h5py.File(file_path, "r") as f:
            add_line("## File Structure")
            process_group(f)

        return "\n".join(markdown)
    except Exception as e:
        return f"❌ Error processing HDF5 file: {str(e)}"


# Process the sample file
output = generate_enhanced_markdown("sample.h5")

# Save the output
with open("sample_output.md", "w", encoding="utf-8") as f:
    f.write(output)

print("Generated enhanced markdown output in sample_output.md")
