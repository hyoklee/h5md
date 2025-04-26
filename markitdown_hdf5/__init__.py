import h5py
from abc import ABC, abstractmethod
from markitdown import MarkItDown

class Plugin(ABC):
    def __init__(self):
        self.name = ""
        self.description = ""

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def process_file(self, file_path: str, builder):
        pass

class HDF5Plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = "hdf5"
        self.description = "Plugin for visualizing HDF5 metadata"

    def process_file(self, file_path: str, builder):
        try:
            with h5py.File(file_path, 'r') as f:
                builder.add_heading(f"HDF5 File Structure: {file_path}", 1)
                self._process_group(f, builder)
        except Exception as e:
            builder.add_paragraph(f"Error processing HDF5 file: {str(e)}")

    def _process_group(self, group, builder, indent=0):
        # Process group attributes
        if len(group.attrs) > 0:
            builder.add_heading("Attributes:", indent + 2)
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
                dataset_info = [
                    ["Property", "Value"],
                    ["Shape", f"`{item.shape}`"],
                    ["Type", f"`{item.dtype}`"]
                ]
                builder.add_table(dataset_info)
                
                # Process dataset attributes
                if len(item.attrs) > 0:
                    builder.add_heading("Dataset Attributes:", indent + 3)
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
                self._process_group(item, builder, indent + 1)

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.h5', '.hdf5'))

# Register the plugin
def register():
    return HDF5Plugin()

# Register the plugin with markitdown
md = MarkItDown()
md.register_plugin(register())
