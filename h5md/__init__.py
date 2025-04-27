from typing import Optional
import h5py
import numpy as np


class HDF5Converter:
    """Convert HDF5 files to markdown format."""

    def __init__(self) -> None:
        self._output_lines = []

    def _format_value(self, value: object) -> str:
        """Format a value for markdown output."""
        if isinstance(value, (np.integer, np.floating)):
            return str(value.item())
        elif isinstance(value, np.ndarray):
            return str(value.tolist())
        elif isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def _process_attributes(self, item: h5py.Group | h5py.Dataset) -> None:
        """Process attributes of an HDF5 object."""
        if not item.attrs:
            return

        self._output_lines.append("\n### Attributes:\n")
        self._output_lines.append("| Name | Value | Type |")
        self._output_lines.append("|------|--------|------|")

        for key, value in item.attrs.items():
            formatted_value = self._format_value(value)
            value_type = type(value).__name__
            self._output_lines.append(
                f"| `{key}` | `{formatted_value}` | `{value_type}` |"
            )
        self._output_lines.append("")

    def _process_dataset(self, dataset: h5py.Dataset) -> None:
        """Process an HDF5 dataset."""
        self._output_lines.append("\n### Dataset Properties:\n")
        self._output_lines.append("| Property | Value |")
        self._output_lines.append("|----------|--------|")
        self._output_lines.append(f"| Shape | `{dataset.shape}` |")
        self._output_lines.append(f"| Type | `{dataset.dtype}` |")

        if dataset.compression:
            self._output_lines.append(f"| Compression | `{dataset.compression}` |")
        self._output_lines.append("")

        self._process_attributes(dataset)

    def _process_group(self, group: h5py.Group, level: int = 1) -> None:
        """Process an HDF5 group."""
        if level > 1:
            self._output_lines.append("\n" + "#" * level + " Group: " + group.name)

        self._process_attributes(group)

        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                self._output_lines.append(
                    "\n" + "#" * (level + 1) + f" Dataset: {name}"
                )
                self._process_dataset(item)
            elif isinstance(item, h5py.Group):
                self._process_group(item, level + 1)

    def convert(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Convert an HDF5 file to markdown format."""
        self._output_lines = []
        self._output_lines.append(f"# HDF5 File Structure: {file_path}\n")

        with h5py.File(file_path, "r") as f:
            self._process_group(f)

        markdown_content = "\n".join(self._output_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(markdown_content)

        return markdown_content
