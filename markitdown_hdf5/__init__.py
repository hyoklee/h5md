import h5py
from markitdown import Plugin, MarkdownBuilder

class HDF5Plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = "hdf5"
        self.description = "Plugin for visualizing HDF5 metadata"

    def process_file(self, file_path: str, builder: MarkdownBuilder):
        try:
            with h5py.File(file_path, 'r') as f:
                builder.heading(f"HDF5 File Structure: {file_path}", level=1)
                self._process_group(f, builder)
        except Exception as e:
            builder.paragraph(f"Error processing HDF5 file: {str(e)}")

    def _process_group(self, group, builder: MarkdownBuilder, indent=0):
        # Process group attributes
        if len(group.attrs) > 0:
            builder.heading("Attributes:", level=indent + 2)
            attrs_table = [["Name", "Value", "Type"]]
            for key, value in group.attrs.items():
                attrs_table.append([
                    f"`{key}`",
                    f"`{str(value)}`",
                    f"`{type(value).__name__}`"
                ])
            builder.table(attrs_table)

        # Process datasets
        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                builder.heading(f"Dataset: {name}", level=indent + 2)
                dataset_info = [
                    ["Property", "Value"],
                    ["Shape", f"`{item.shape}`"],
                    ["Type", f"`{item.dtype}`"]
                ]
                builder.table(dataset_info)
                
                # Process dataset attributes
                if len(item.attrs) > 0:
                    builder.heading("Dataset Attributes:", level=indent + 3)
                    dataset_attrs = [["Name", "Value", "Type"]]
                    for key, value in item.attrs.items():
                        dataset_attrs.append([
                            f"`{key}`",
                            f"`{str(value)}`",
                            f"`{type(value).__name__}`"
                        ])
                    builder.table(dataset_attrs)
            
            elif isinstance(item, h5py.Group):
                builder.heading(f"Group: {name}", level=indent + 2)
                self._process_group(item, builder, indent + 1)

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.h5', '.hdf5'))

# Register the plugin
def register():
    return HDF5Plugin()
