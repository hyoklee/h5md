import h5py
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import difflib

@dataclass
class DatasetDiff:
    path: str
    exists_in_both: bool
    shape_changed: bool
    dtype_changed: bool
    attr_changes: Dict[str, Tuple[Any, Any]]  # (old_value, new_value)
    data_changes: Optional[Dict[str, Any]] = None  # Statistical differences
    max_diff: Optional[float] = None
    mean_diff: Optional[float] = None
    changed_elements: Optional[int] = None
    total_elements: Optional[int] = None

@dataclass
class GroupDiff:
    path: str
    exists_in_both: bool
    attr_changes: Dict[str, Tuple[Any, Any]]
    added_children: List[str]
    removed_children: List[str]

class HDF5Differ:
    def __init__(self, 
                 rtol: float = 1e-5, 
                 atol: float = 1e-8,
                 max_diff_elements: int = 1000):
        self.rtol = rtol
        self.atol = atol
        self.max_diff_elements = max_diff_elements
        
    def _compare_attributes(self, 
                          attrs1: h5py.AttributeManager,
                          attrs2: h5py.AttributeManager) -> Dict[str, Tuple[Any, Any]]:
        """Compare attributes between two objects"""
        changes = {}
        
        # Check for changed or removed attributes
        for key in attrs1.keys():
            if key not in attrs2:
                changes[key] = (attrs1[key], None)
            elif not np.array_equal(attrs1[key], attrs2[key]):
                changes[key] = (attrs1[key], attrs2[key])
        
        # Check for new attributes
        for key in attrs2.keys():
            if key not in attrs1:
                changes[key] = (None, attrs2[key])
                
        return changes

    def _compare_datasets(self,
                         dset1: h5py.Dataset,
                         dset2: h5py.Dataset) -> DatasetDiff:
        """Compare two datasets"""
        shape_changed = dset1.shape != dset2.shape
        dtype_changed = dset1.dtype != dset2.dtype
        attr_changes = self._compare_attributes(dset1.attrs, dset2.attrs)
        
        data_changes = None
        max_diff = None
        mean_diff = None
        changed_elements = None
        total_elements = dset1.size
        
        # Compare data if shapes and dtypes match
        if not shape_changed and not dtype_changed and np.issubdtype(dset1.dtype, np.number):
            try:
                # Load data (might need chunking for large datasets)
                data1 = dset1[()]
                data2 = dset2[()]
                
                # Calculate differences
                abs_diff = np.abs(data1 - data2)
                rel_diff = abs_diff / (np.abs(data1) + self.atol)
                
                changed_mask = (abs_diff > self.atol) & (rel_diff > self.rtol)
                changed_elements = np.sum(changed_mask)
                
                if changed_elements > 0:
                    max_diff = float(np.max(abs_diff))
                    mean_diff = float(np.mean(abs_diff))
                    
                    # Get statistical differences
                    data_changes = {
                        'min_diff': float(np.min(abs_diff[changed_mask])),
                        'max_diff': max_diff,
                        'mean_diff': mean_diff,
                        'median_diff': float(np.median(abs_diff[changed_mask])),
                        'std_diff': float(np.std(abs_diff[changed_mask])),
                    }
                    
                    # Get some example differences if not too many
                    if changed_elements <= self.max_diff_elements:
                        changed_indices = np.where(changed_mask)
                        data_changes['examples'] = [
                            {
                                'index': tuple(int(i) for i in idx),
                                'old_value': float(data1[idx]),
                                'new_value': float(data2[idx]),
                                'difference': float(abs_diff[idx])
                            }
                            for idx in zip(*changed_indices)
                        ]
            except Exception as e:
                data_changes = {'error': str(e)}
        
        return DatasetDiff(
            path=dset1.name,
            exists_in_both=True,
            shape_changed=shape_changed,
            dtype_changed=dtype_changed,
            attr_changes=attr_changes,
            data_changes=data_changes,
            max_diff=max_diff,
            mean_diff=mean_diff,
            changed_elements=changed_elements,
            total_elements=total_elements
        )

    def compare_files(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compare two HDF5 files"""
        dataset_diffs = {}
        group_diffs = {}
        
        with h5py.File(file1_path, 'r') as f1, h5py.File(file2_path, 'r') as f2:
            # Compare file-level attributes
            file_attr_changes = self._compare_attributes(f1.attrs, f2.attrs)
            
            # Get all paths in both files
            paths1 = set(f1.keys())
            paths2 = set(f2.keys())
            
            # Process common paths
            for path in paths1 & paths2:
                obj1 = f1[path]
                obj2 = f2[path]
                
                if isinstance(obj1, h5py.Dataset) and isinstance(obj2, h5py.Dataset):
                    dataset_diffs[path] = self._compare_datasets(obj1, obj2)
                elif isinstance(obj1, h5py.Group) and isinstance(obj2, h5py.Group):
                    group_diffs[path] = GroupDiff(
                        path=path,
                        exists_in_both=True,
                        attr_changes=self._compare_attributes(obj1.attrs, obj2.attrs),
                        added_children=list(set(obj2.keys()) - set(obj1.keys())),
                        removed_children=list(set(obj1.keys()) - set(obj2.keys()))
                    )
            
            # Process paths only in file1
            for path in paths1 - paths2:
                obj = f1[path]
                if isinstance(obj, h5py.Dataset):
                    dataset_diffs[path] = DatasetDiff(
                        path=path,
                        exists_in_both=False,
                        shape_changed=False,
                        dtype_changed=False,
                        attr_changes={},
                        data_changes=None
                    )
                else:
                    group_diffs[path] = GroupDiff(
                        path=path,
                        exists_in_both=False,
                        attr_changes={},
                        added_children=[],
                        removed_children=list(obj.keys())
                    )
            
            # Process paths only in file2
            for path in paths2 - paths1:
                obj = f2[path]
                if isinstance(obj, h5py.Dataset):
                    dataset_diffs[path] = DatasetDiff(
                        path=path,
                        exists_in_both=False,
                        shape_changed=False,
                        dtype_changed=False,
                        attr_changes={},
                        data_changes=None
                    )
                else:
                    group_diffs[path] = GroupDiff(
                        path=path,
                        exists_in_both=False,
                        attr_changes={},
                        added_children=list(obj.keys()),
                        removed_children=[]
                    )
        
        return {
            'file_attr_changes': file_attr_changes,
            'dataset_diffs': dataset_diffs,
            'group_diffs': group_diffs
        }

def format_diff_markdown(diff_results: Dict[str, Any]) -> str:
    """Format diff results as markdown"""
    lines = ["# HDF5 File Comparison Results\n"]
    
    # File-level changes
    if diff_results['file_attr_changes']:
        lines.extend([
            "## File Attribute Changes",
            "| Attribute | Old Value | New Value |",
            "|-----------|-----------|-----------|"
        ])
        for attr, (old_val, new_val) in diff_results['file_attr_changes'].items():
            lines.append(f"| `{attr}` | `{old_val}` | `{new_val}` |")
        lines.append("")
    
    # Group changes
    if diff_results['group_diffs']:
        lines.append("## Group Changes")
        for path, diff in sorted(diff_results['group_diffs'].items()):
            if not diff.exists_in_both:
                status = "Removed from" if diff.removed_children else "Added to"
                lines.append(f"### 🗂️ Group `{path}` ({status} new file)")
                continue
                
            lines.append(f"### 🗂️ Group: `{path}`")
            
            if diff.attr_changes:
                lines.extend([
                    "#### Attribute Changes:",
                    "| Attribute | Old Value | New Value |",
                    "|-----------|-----------|-----------|"
                ])
                for attr, (old_val, new_val) in diff.attr_changes.items():
                    lines.append(f"| `{attr}` | `{old_val}` | `{new_val}` |")
            
            if diff.added_children:
                lines.append("#### Added Children:")
                for child in sorted(diff.added_children):
                    lines.append(f"- `{child}`")
            
            if diff.removed_children:
                lines.append("#### Removed Children:")
                for child in sorted(diff.removed_children):
                    lines.append(f"- `{child}`")
            
            lines.append("")
    
    # Dataset changes
    if diff_results['dataset_diffs']:
        lines.append("## Dataset Changes")
        for path, diff in sorted(diff_results['dataset_diffs'].items()):
            if not diff.exists_in_both:
                status = "Removed from" if diff.attr_changes else "Added to"
                lines.append(f"### 📊 Dataset `{path}` ({status} new file)")
                continue
            
            status = []
            if diff.shape_changed:
                status.append("shape changed")
            if diff.dtype_changed:
                status.append("dtype changed")
            if diff.data_changes:
                status.append("data changed")
            
            lines.append(f"### 📊 Dataset: `{path}` ({', '.join(status)})")
            
            if diff.shape_changed or diff.dtype_changed:
                lines.extend([
                    "#### Structure Changes:",
                    f"- Shape changed: {diff.shape_changed}",
                    f"- Dtype changed: {diff.dtype_changed}"
                ])
            
            if diff.attr_changes:
                lines.extend([
                    "#### Attribute Changes:",
                    "| Attribute | Old Value | New Value |",
                    "|-----------|-----------|-----------|"
                ])
                for attr, (old_val, new_val) in diff.attr_changes.items():
                    lines.append(f"| `{attr}` | `{old_val}` | `{new_val}` |")
            
            if diff.data_changes:
                lines.append("#### Data Changes:")
                if 'error' in diff.data_changes:
                    lines.append(f"Error comparing data: {diff.data_changes['error']}")
                else:
                    lines.extend([
                        f"- Changed elements: {diff.changed_elements:,} / {diff.total_elements:,} ({diff.changed_elements/diff.total_elements*100:.2f}%)",
                        f"- Maximum difference: {diff.max_diff:.6e}",
                        f"- Mean difference: {diff.mean_diff:.6e}",
                        "",
                        "Difference Statistics:",
                        "| Metric | Value |",
                        "|--------|--------|"
                    ])
                    
                    for metric, value in diff.data_changes.items():
                        if metric != 'examples':
                            lines.append(f"| {metric} | {value:.6e} |")
                    
                    if 'examples' in diff.data_changes:
                        lines.extend([
                            "",
                            "Example Differences:",
                            "| Index | Old Value | New Value | Absolute Difference |",
                            "|-------|-----------|-----------|-------------------|"
                        ])
                        for ex in diff.data_changes['examples'][:5]:  # Show first 5 examples
                            lines.append(
                                f"| {ex['index']} | {ex['old_value']:.6e} | {ex['new_value']:.6e} | {ex['difference']:.6e} |"
                            )
            
            lines.append("")
    
    return "\n".join(lines)
