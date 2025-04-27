from typing import Dict, Optional
import h5py
import numpy as np


def format_value(value: object) -> object:
    """Format a value for JSON output."""
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def process_attributes(item: h5py.Group | h5py.Dataset) -> Dict:
    """Process attributes of an HDF5 object."""
    result = {}
    for key, value in item.attrs.items():
        result[key] = format_value(value)
    return result


def process_dataset(dataset: h5py.Dataset) -> Dict:
    """Process an HDF5 dataset."""
    result = {
        "type": "dataset",
        "shape": dataset.shape,
        "dtype": str(dataset.dtype),
        "attributes": process_attributes(dataset),
    }

    if dataset.compression:
        result["compression"] = dataset.compression

    try:
        if dataset.size <= 1000:  # Only include small datasets
            result["data"] = format_value(dataset[()])
    except Exception as e:
        result["error"] = str(e)

    return result


def process_group(group: h5py.Group) -> Dict:
    """Process an HDF5 group."""
    result = {
        "type": "group",
        "attributes": process_attributes(group),
        "children": {},
    }

    for name, item in group.items():
        if isinstance(item, h5py.Dataset):
            result["children"][name] = process_dataset(item)
        elif isinstance(item, h5py.Group):
            result["children"][name] = process_group(item)

    return result


def convert_to_json(file_path: str, output_path: Optional[str] = None) -> Dict:
    """Convert an HDF5 file to JSON format."""
    with h5py.File(file_path, "r") as f:
        result = process_group(f)
        result["file_path"] = file_path

    if output_path:
        import json

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

    return result
