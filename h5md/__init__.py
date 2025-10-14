from typing import List, Optional, Literal

import h5py
import numpy as np


class HDF5Converter:
    """Convert HDF5 files to markdown format with AI-friendly key-value output."""

    _output_lines: List[str]
    _max_rows: Optional[int]
    _max_cols: Optional[int]
    _sampling_strategy: Literal["first", "uniform", "edges"]
    _include_data_preview: bool

    def __init__(
        self,
        max_rows: Optional[int] = None,
        max_cols: Optional[int] = None,
        sampling_strategy: Literal["first", "uniform", "edges"] = "first",
        include_data_preview: bool = True,
    ) -> None:
        """Initialize the HDF5 converter.

        Args:
            max_rows: Maximum number of rows to include in dataset previews.
                     None means include all rows (use with caution for large datasets).
            max_cols: Maximum number of columns to include in dataset previews.
                     None means include all columns.
            sampling_strategy: How to sample data when limits are exceeded:
                - "first": Take first N rows/columns
                - "uniform": Sample uniformly across the dataset
                - "edges": Show first and last items with "..." in between
            include_data_preview: Whether to include actual data values in output.
        """
        self._output_lines = []
        self._max_rows = max_rows
        self._max_cols = max_cols
        self._sampling_strategy = sampling_strategy
        self._include_data_preview = include_data_preview

    def _format_value(self, value: object) -> str:
        """Format a value for markdown output."""
        if isinstance(value, (np.integer, np.floating)):
            return str(value.item())
        elif isinstance(value, np.ndarray):
            return str(value.tolist())
        elif isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def _subset_array(self, arr: np.ndarray, axis: int, limit: int) -> np.ndarray:
        """Subset an array along a specific axis based on sampling strategy.

        Args:
            arr: Input numpy array
            axis: Axis to subset along
            limit: Maximum number of elements to keep along this axis

        Returns:
            Subsetted array
        """
        size = arr.shape[axis]
        if size <= limit:
            return arr

        if self._sampling_strategy == "first":
            indices = np.arange(limit)
        elif self._sampling_strategy == "uniform":
            indices = np.linspace(0, size - 1, limit, dtype=int)
        elif self._sampling_strategy == "edges":
            # Take half from start, half from end
            half = limit // 2
            start_indices = np.arange(half)
            end_indices = np.arange(size - (limit - half), size)
            indices = np.concatenate([start_indices, end_indices])
        else:
            indices = np.arange(limit)

        return np.take(arr, indices, axis=axis)

    def _format_dataset_values(self, dataset: h5py.Dataset) -> str:
        """Format dataset values as key-value pairs for AI consumption.

        Args:
            dataset: HDF5 dataset to format

        Returns:
            Formatted string representation
        """
        try:
            # Load the data
            data = dataset[()]

            # Handle scalar values
            if dataset.shape == ():
                return f"**Value:** `{self._format_value(data)}`"

            # Convert to numpy array if needed
            if not isinstance(data, np.ndarray):
                data = np.array(data)

            # Apply subsetting if limits are set
            truncated_rows = False
            truncated_cols = False

            if self._max_rows is not None and len(data.shape) >= 1:
                if data.shape[0] > self._max_rows:
                    data = self._subset_array(data, 0, self._max_rows)
                    truncated_rows = True

            if self._max_cols is not None and len(data.shape) >= 2:
                if data.shape[1] > self._max_cols:
                    data = self._subset_array(data, 1, self._max_cols)
                    truncated_cols = True

            # Format the output
            result = []

            # For 1D arrays, show as key-value list
            if len(data.shape) == 1:
                result.append("**Data (Key-Value Format):**")
                result.append("")
                for i, val in enumerate(data):
                    result.append(f"- `index_{i}`: `{self._format_value(val)}`")
                if truncated_rows:
                    orig_shape = dataset.shape
                    msg = (
                        f"- *(showing {len(data)} of {orig_shape[0]} "
                        f"rows using '{self._sampling_strategy}' sampling)*"
                    )
                    result.append(msg)

            # For 2D arrays, show as structured format
            elif len(data.shape) == 2:
                result.append("**Data (Key-Value Format):**")
                result.append("")
                for i, row in enumerate(data):
                    result.append(f"- **Row {i}:**")
                    for j, val in enumerate(row):
                        result.append(f"  - `col_{j}`: `{self._format_value(val)}`")
                if truncated_rows or truncated_cols:
                    orig_shape = dataset.shape
                    msg = f"- *(showing {data.shape[0]} of {orig_shape[0]} rows"
                    if truncated_cols:
                        msg += f", {data.shape[1]} of {orig_shape[1]} cols"
                    msg += f" using '{self._sampling_strategy}' sampling)*"
                    result.append(msg)

            # For higher dimensional arrays, show summary
            else:
                result.append("**Data (Multi-dimensional Array):**")
                result.append("")
                result.append(f"- **Sample shape:** `{data.shape}`")
                result.append(f"- **Flattened preview (first 20 values):**")
                flat = data.flatten()[:20]
                for i, val in enumerate(flat):
                    result.append(f"  - `element_{i}`: `{self._format_value(val)}`")
                if len(data.flatten()) > 20:
                    result.append(
                        f"  - *(showing 20 of {len(data.flatten())} total elements)*"
                    )

            return "\n".join(result)

        except Exception as e:
            return f"**Data:** *(Unable to load data: {str(e)})*"

    def _process_attributes(
        self, item: h5py.Group | h5py.Dataset, header_level: int
    ) -> None:
        """Process attributes of an HDF5 object in key-value format."""
        if not item.attrs:
            return

        # Dynamic header for Attributes based on depth
        attr_header = "#" * header_level + " Attributes"
        self._output_lines.append(attr_header)
        self._output_lines.append("")

        for key, value in item.attrs.items():
            formatted_value = self._format_value(value)
            value_type = type(value).__name__
            self._output_lines.append(
                f"- **{key}:** `{formatted_value}` (type: `{value_type}`)"
            )
        self._output_lines.append("")

    def _process_dataset(self, dataset: h5py.Dataset, header_level: int) -> None:
        """Process an HDF5 dataset with key-value format."""
        # Dataset Properties in key-value format
        prop_header = "#" * (header_level + 1) + " Properties"
        self._output_lines.append(prop_header)
        self._output_lines.append("")

        # Basic properties
        self._output_lines.append(f"- **Shape:** `{dataset.shape}`")
        self._output_lines.append(f"- **Data Type:** `{dataset.dtype}`")
        self._output_lines.append(f"- **Size:** `{dataset.size}` elements")

        if dataset.compression:
            self._output_lines.append(f"- **Compression:** `{dataset.compression}`")

        # Add chunks info if available
        if dataset.chunks:
            self._output_lines.append(f"- **Chunks:** `{dataset.chunks}`")

        self._output_lines.append("")

        # Include data preview if enabled
        if self._include_data_preview:
            self._output_lines.append(self._format_dataset_values(dataset))
            self._output_lines.append("")

        # Process dataset attributes
        self._process_attributes(dataset, header_level + 1)

    def _process_group(self, group: h5py.Group, level: int = 1) -> None:
        """Process an HDF5 group."""
        if level > 1:
            header = "\n" + "#" * level + " Group: " + group.name
            self._output_lines.append(header)
            self._output_lines.append("")  # Blank line after heading

        # Pass group level to attributes for dynamic header
        self._process_attributes(group, level + 1)

        for name in group.keys():
            # Check for external link before accessing the item
            # get_external() returns (filename, path) tuple for external links
            link_info = group.get(name, getlink=True)

            if isinstance(link_info, h5py.ExternalLink):
                header = "\n" + "#" * (level + 1) + " External Link: " + name
                self._output_lines.append(header)
                self._output_lines.append("")  # Blank line after heading
                self._output_lines.append(f"- **Target File:** `{link_info.filename}`")
                self._output_lines.append(f"- **Target Path:** `{link_info.path}`")
                self._output_lines.append("")  # Blank line after details
            else:
                # Now access the actual item
                item = group[name]
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
