import json
from typing import Any, Dict, List, Optional, Union, cast
import h5py
import numpy as np
from datetime import datetime
import os

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)

def convert_to_json_serializable(value: Any) -> Any:
    """Convert HDF5/numpy values to JSON-serializable types."""
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, bytes):
        return value.decode('utf-8')
    return value

def get_dataset_metadata(dataset: h5py.Dataset) -> Dict[str, Any]:
    """Extract metadata from a dataset"""
    metadata: Dict[str, Any] = {
        "type": "dataset",
        "shape": dataset.shape,
        "size": dataset.size * dataset.dtype.itemsize,
        "dtype": str(dataset.dtype),
        "compression": dataset.compression,
        "compression_opts": dataset.compression_opts,
        "chunks": dataset.chunks,
        "attributes": {},
    }

    # Add attributes
    for key, value in dataset.attrs.items():
        metadata['attributes'][key] = convert_to_json_serializable(value)

    # Add statistics for numeric datasets
    if np.issubdtype(dataset.dtype, np.number):
        data = dataset[()]
        metadata.update({
            "statistics": {
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "mean": float(np.mean(data)),
                "std": float(np.std(data)),
                "unique_values": int(len(np.unique(data)))
            }
        })

    return metadata

def get_group_metadata(group: h5py.Group) -> Dict[str, Any]:
    """Extract metadata from a group"""
    metadata: Dict[str, Any] = {
        "type": "group",
        "attributes": {},
        "num_children": len(group.keys()),
    }
    
    # Add attributes
    for key, value in group.attrs.items():
        metadata['attributes'][key] = convert_to_json_serializable(value)
    
    return metadata

def process_hdf5(group: h5py.Group, metadata_dict: Dict[str, Dict[str, Any]]) -> None:
    """Recursively process HDF5 group structure"""
    for name, item in group.items():
        path = item.name
        if isinstance(item, h5py.Dataset):
            metadata_dict[path] = get_dataset_metadata(item)
        elif isinstance(item, h5py.Group):
            metadata_dict[path] = get_group_metadata(item)
            process_hdf5(item, metadata_dict)

def export_to_json(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Export HDF5 metadata to JSON format"""
    metadata: Dict[str, Any] = {
        "file_info": {
            "path": input_path,
            "size": os.path.getsize(input_path),
            "created": datetime.fromtimestamp(os.path.getctime(input_path)).isoformat(),
            "modified": datetime.fromtimestamp(os.path.getmtime(input_path)).isoformat(),
            "attributes": {}
        },
        "contents": {}
    }

    with h5py.File(input_path, "r") as f:
        # Add file-level attributes
        file_info = cast(Dict[str, Any], metadata["file_info"])
        file_info["attributes"] = {}
        for key, value in f.attrs.items():
            file_info["attributes"][key] = convert_to_json_serializable(value)

        # Process all groups and datasets
        contents = cast(Dict[str, Dict[str, Any]], metadata["contents"])
        process_hdf5(f, contents)

    # Write to JSON file or return string
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, cls=NumpyEncoder, indent=2)
        return None
    else:
        return json.dumps(metadata, cls=NumpyEncoder, indent=2)
