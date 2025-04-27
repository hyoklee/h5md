import h5py
from typing import List, Any

def register() -> 'HDF5Converter':
    """Register the HDF5 plugin"""
    return HDF5Converter()

class MarkdownBuilder:
    def __init__(self) -> None:
        self._content: List[str] = []

    def add_heading(self, text: str, level: int = 1) -> None:
        self._content.append(f"{'#' * level} {text}\n")

    def add_paragraph(self, text: str) -> None:
        self._content.append(f"{text}\n\n")

    def add_table(self, rows: List[List[str]]) -> None:
        if not rows:
            return

        # Add header row
        self._content.append("| " + " | ".join(rows[0]) + " |\n")
        
        # Add separator row
        self._content.append("| " + " | ".join(["---"] * len(rows[0])) + " |\n")
        
        # Add data rows
        for row in rows[1:]:
            self._content.append("| " + " | ".join(row) + " |\n")
        
        self._content.append("\n")

    def build(self) -> str:
        return "".join(self._content)

class HDF5Converter:
    def convert(self, file_path: str) -> str:
        """Convert an HDF5 file to markdown format."""
        builder = MarkdownBuilder()
        
        try:
            with h5py.File(file_path, 'r') as f:
                builder.add_heading(f"HDF5 File Structure: {file_path}")
                builder.add_paragraph("")  # Add empty line after heading
                self._process_group(f, builder)
        except Exception as e:
            builder.add_paragraph(f"Error processing HDF5 file: {str(e)}")
        
        return builder.build()

    def _process_group(self, group: h5py.Group, builder: MarkdownBuilder, indent: int = 0) -> None:
        # Process group attributes
        if len(group.attrs) > 0:
            builder.add_heading("Attributes:", indent + 2)
            builder.add_paragraph("")  
            attrs_table = [["Name", "Value", "Type"]]
            for key, value in group.attrs.items():
                attrs_table.append([
                    f"`{key}`",
                    f"`{str(value)}`",
                    f"`{type(value).__name__}`"
                ])
            builder.add_table(attrs_table)

        # Process datasets
        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                builder.add_heading(f"Dataset: {name}", indent + 2)
                builder.add_paragraph("")  
                dataset_info = [
                    ["Property", "Value"],
                    ["Shape", f"`{item.shape}`"],
                    ["Type", f"`{item.dtype}`"]
                ]
                builder.add_table(dataset_info)
                
                # Process dataset attributes
                if len(item.attrs) > 0:
                    builder.add_heading("Dataset Attributes:", indent + 3)
                    builder.add_paragraph("")  
                    dataset_attrs = [["Name", "Value", "Type"]]
                    for key, value in item.attrs.items():
                        dataset_attrs.append([
                            f"`{key}`",
                            f"`{str(value)}`",
                            f"`{type(value).__name__}`"
                        ])
                    builder.add_table(dataset_attrs)
            
            elif isinstance(item, h5py.Group):
                builder.add_heading(f"Group: {name}", indent + 2)
                builder.add_paragraph("")  
                self._process_group(item, builder, indent + 1)
