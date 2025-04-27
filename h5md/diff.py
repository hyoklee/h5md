from typing import Dict, Optional, Tuple
import h5py
import numpy as np


def format_value(value: object) -> object:
    """Format a value for comparison."""
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def compare_attributes(
    attrs1: h5py.AttributeManager, attrs2: h5py.AttributeManager
) -> Dict:
    """Compare attributes between two HDF5 objects."""
    attr_changes = {}
    keys1 = set(attrs1.keys())
    keys2 = set(attrs2.keys())

    # Find added and removed attributes
    added = keys2 - keys1
    removed = keys1 - keys2
    common = keys1 & keys2

    # Process added attributes
    for key in added:
        attr_changes[key] = (None, format_value(attrs2[key]))

    # Process removed attributes
    for key in removed:
        attr_changes[key] = (format_value(attrs1[key]), None)

    # Compare common attributes
    for key in common:
        val1 = format_value(attrs1[key])
        val2 = format_value(attrs2[key])
        if val1 != val2:
            attr_changes[key] = (val1, val2)

    return attr_changes


def compare_datasets(
    ds1: h5py.Dataset, ds2: h5py.Dataset, max_diff_elements: int = 1000
) -> Dict:
    """Compare two datasets."""
    result = {
        "exists_in_both": True,
        "shape_changed": ds1.shape != ds2.shape,
        "dtype_changed": ds1.dtype != ds2.dtype,
        "data_changes": None,
    }

    # Compare attributes
    attr_changes = compare_attributes(ds1.attrs, ds2.attrs)
    if attr_changes:
        result["attr_changes"] = attr_changes

    # Compare data if shapes and types match
    if not result["shape_changed"] and not result["dtype_changed"]:
        try:
            if np.issubdtype(ds1.dtype, np.number):
                data1 = ds1[()]
                data2 = ds2[()]
                if data1.size <= max_diff_elements:
                    diff = np.abs(data1 - data2)
                    result["data_changes"] = {
                        "changed_elements": int(np.sum(diff > 0)),
                        "total_elements": data1.size,
                        "max_diff": float(np.max(diff)),
                        "mean_diff": float(np.mean(diff)),
                    }
        except Exception as e:
            result["data_error"] = str(e)

    return result


def compare_hdf5_files(
    file1_path: str, file2_path: str, output_path: Optional[str] = None
) -> Dict:
    """Compare two HDF5 files."""
    result = {
        "file1": file1_path,
        "file2": file2_path,
        "file_attr_changes": {},
        "dataset_diffs": {},
        "group_changes": {"added": [], "removed": []},
    }

    with h5py.File(file1_path, "r") as f1, h5py.File(file2_path, "r") as f2:
        # Compare file attributes
        result["file_attr_changes"] = compare_attributes(f1.attrs, f2.attrs)

        # Get all paths in both files
        paths1 = set(get_all_paths(f1))
        paths2 = set(get_all_paths(f2))

        # Find added and removed paths
        added = paths2 - paths1
        removed = paths1 - paths2
        common = paths1 & paths2

        # Process added items
        for path in added:
            item = f2[path]
            if isinstance(item, h5py.Group):
                result["group_changes"]["added"].append(path)
            elif isinstance(item, h5py.Dataset):
                result["dataset_diffs"][path] = {
                    "exists_in_both": False,
                    "added": True,
                }

        # Process removed items
        for path in removed:
            item = f1[path]
            if isinstance(item, h5py.Group):
                result["group_changes"]["removed"].append(path)
            elif isinstance(item, h5py.Dataset):
                result["dataset_diffs"][path] = {
                    "exists_in_both": False,
                    "removed": True,
                }

        # Compare common items
        for path in common:
            item1 = f1[path]
            item2 = f2[path]

            if isinstance(item1, h5py.Dataset):
                if isinstance(item2, h5py.Dataset):
                    result["dataset_diffs"][path] = compare_datasets(item1, item2)

    if output_path:
        import json

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

    return result


def get_all_paths(group: h5py.Group) -> list:
    """Get all paths in an HDF5 file."""
    paths = []
    group.visit(paths.append)
    return paths
