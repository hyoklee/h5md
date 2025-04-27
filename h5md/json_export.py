import json
import os
from datetime import datetime

import h5py
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def get_dataset_metadata(dataset):
    """Extract metadata from a dataset"""
    metadata = {
        "type": "dataset",
        "shape": dataset.shape,
        "dtype": str(dataset.dtype),
        "size": dataset.size,
        "memory_size": dataset.size * dataset.dtype.itemsize,
        "compression": dataset.compression,
        "compression_opts": dataset.compression_opts,
        "chunks": dataset.chunks,
        "attributes": dict(dataset.attrs),
    }

    # Add statistics for numeric datasets
    if np.issubdtype(dataset.dtype, np.number):
        try:
            data = dataset[()]
            metadata["statistics"] = {
                "min": np.min(data),
                "max": np.max(data),
                "mean": np.mean(data),
                "median": np.median(data),
                "std": np.std(data),
                "unique_values": len(np.unique(data)),
            }
        except:
            pass

    return metadata


def get_group_metadata(group):
    """Extract metadata from a group"""
    return {
        "type": "group",
        "attributes": dict(group.attrs),
        "num_children": len(group.keys()),
    }


def process_hdf5(group, metadata_dict):
    """Recursively process HDF5 group structure"""
    for name, item in group.items():
        path = item.name

        if isinstance(item, h5py.Dataset):
            metadata_dict[path] = get_dataset_metadata(item)
        elif isinstance(item, h5py.Group):
            metadata_dict[path] = get_group_metadata(item)
            process_hdf5(item, metadata_dict)


def export_to_json(input_path, output_path):
    """Export HDF5 metadata to JSON format"""
    metadata = {
        "file_info": {
            "path": input_path,
            "size": os.path.getsize(input_path),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(input_path)),
            "created": datetime.fromtimestamp(os.path.getctime(input_path)),
        },
        "contents": {},
    }

    with h5py.File(input_path, "r") as f:
        # Add file-level attributes
        metadata["file_info"]["attributes"] = dict(f.attrs)

        # Process all groups and datasets
        process_hdf5(f, metadata["contents"])

    # Write to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, cls=NumpyEncoder, indent=2)
