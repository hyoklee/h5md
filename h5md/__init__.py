from typing import List, Optional

import h5py
import numpy as np


class HDF5Converter:
    """Convert HDF5 files to markdown format."""

    _output_lines: List[str]

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

    def _process_attributes(
        self, item: h5py.Group | h5py.Dataset, header_level: int
    ) -> None:
        """Process attributes of an HDF5 object."""
        if not item.attrs:
            return

        # Dynamic header for Attributes based on depth
        attr_header = "#" * header_level + " Attributes:"
        self._output_lines.append(attr_header)
        self._output_lines.append("")  # Blank line before table
        self._output_lines.append("| Name | Value | Type |")
        self._output_lines.append("|------|--------|------|")

        for key, value in item.attrs.items():
            formatted_value = self._format_value(value)
            value_type = type(value).__name__
            row = ("| `{}` | `{}` | " "`{}` |").format(key, formatted_value, value_type)
            self._output_lines.append(row)
        self._output_lines.append("")  # Blank line after table

    def _process_dataset(self, dataset: h5py.Dataset, header_level: int) -> None:
        """Process an HDF5 dataset."""
        # Dynamic header for Dataset Properties based on depth
        prop_header = "#" * (header_level + 1) + " Dataset Properties:"
        self._output_lines.append(prop_header)
        self._output_lines.append("")  # Blank line before table
        self._output_lines.append("| Property | Value |")
        self._output_lines.append("|----------|--------|")
        self._output_lines.append(f"| Shape | `{dataset.shape}` |")
        self._output_lines.append(f"| Type | `{dataset.dtype}` |")

        if dataset.compression:
            row = "| Compression | " f"`{dataset.compression}` |"
            self._output_lines.append(row)
        self._output_lines.append("")  # Blank line after table

        # Pass same header_level for dataset attributes
        self._process_attributes(dataset, header_level + 1)

    def _process_group(self, group: h5py.Group, level: int = 1) -> None:
        """Process an HDF5 group."""
        if level > 1:
            header = "\n" + "#" * level + " Group: " + group.name
            self._output_lines.append(header)
            self._output_lines.append("")  # Blank line after heading

        # Pass group level to attributes for dynamic header
        self._process_attributes(group, level + 1)

        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                header = "\n" + "#" * (level + 1) + " Dataset: " + name
                self._output_lines.append(header)
                self._output_lines.append("")  # Blank line after heading
                # Pass dataset header level to process properties
                self._process_dataset(item, level + 1)
            elif isinstance(item, h5py.Group):
                self._process_group(item, level + 1)

    def convert(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Convert an HDF5 file to markdown format."""
        self._output_lines = []
        header = f"# HDF5 File Structure: {file_path}\n"
        self._output_lines.append(header)
        self._output_lines.append("")  # Blank line after heading

        with h5py.File(file_path, "r") as f:
            self._process_group(f)

        markdown_content = "\n".join(self._output_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(markdown_content)

        return markdown_content
