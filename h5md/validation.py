from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import re
import h5py
import numpy as np

@dataclass
class ValidationRule:
    """Rules for validating HDF5 datasets."""
    path: str  # HDF5 path pattern
    dtype: Optional[str] = None  # Expected dtype
    shape: Optional[Tuple[Optional[int], ...]] = None  # Expected shape (None for variable dimension)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required_attrs: Optional[List[str]] = None
    custom_validator: Optional[Callable[[h5py.Dataset], List[str]]] = None
    allow_nan: bool = True
    allow_inf: bool = True

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, path: str) -> None:
        self.message = message
        self.path = path
        super().__init__(f"{path}: {message}")

class DataValidator:
    def __init__(self) -> None:
        self.rules: Dict[str, ValidationRule] = {}

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules[rule.path] = rule

    def load_schema(self, schema_file: str) -> None:
        """Load validation rules from JSON schema file."""
        with open(schema_file, "r") as f:
            schema = json.load(f)
        
        for rule_dict in schema.get("rules", []):
            rule = ValidationRule(**rule_dict)
            self.add_rule(rule)

    def _match_path(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern."""
        regex = re.compile(pattern.replace("*", ".*"))
        return bool(regex.match(path))

    def validate_dataset(self, dataset: h5py.Dataset, path: str) -> List[str]:
        """Validate a dataset against matching rules."""
        errors: List[str] = []
        
        for rule in self.rules.values():
            if self._match_path(path, rule.path):
                # Check dtype
                if rule.dtype and str(dataset.dtype) != rule.dtype:
                    errors.append(f"Invalid dtype: expected {rule.dtype}, got {dataset.dtype}")
                
                # Check shape
                if rule.shape:
                    if len(dataset.shape) != len(rule.shape):
                        errors.append(f"Invalid shape length: expected {len(rule.shape)}, got {len(dataset.shape)}")
                    else:
                        for i, (actual, expected) in enumerate(zip(dataset.shape, rule.shape)):
                            if expected is not None and actual != expected:
                                errors.append(f"Invalid shape at dimension {i}: expected {expected}, got {actual}")
                
                # Check value range for numeric datasets
                if np.issubdtype(dataset.dtype, np.number):
                    data = dataset[:]
                    if not rule.allow_nan and np.any(np.isnan(data)):
                        errors.append("NaN values not allowed")
                    if not rule.allow_inf and np.any(np.isinf(data)):
                        errors.append("Infinite values not allowed")
                    if rule.min_value is not None and np.any(data < rule.min_value):
                        errors.append(f"Values below minimum: {rule.min_value}")
                    if rule.max_value is not None and np.any(data > rule.max_value):
                        errors.append(f"Values above maximum: {rule.max_value}")
                
                # Check required attributes
                if rule.required_attrs:
                    for attr in rule.required_attrs:
                        if attr not in dataset.attrs:
                            errors.append(f"Missing required attribute: {attr}")
                
                # Run custom validator if provided
                if rule.custom_validator:
                    custom_errors = rule.custom_validator(dataset)
                    errors.extend(custom_errors)
        
        return errors

    def validate_file(self, file: h5py.File) -> Dict[str, List[str]]:
        """Validate an entire HDF5 file."""
        errors: Dict[str, List[str]] = {}

        def visit_item(name: str, item: Union[h5py.Dataset, h5py.Group]) -> None:
            if isinstance(item, h5py.Dataset):
                dataset_errors = self.validate_dataset(item, name)
                if dataset_errors:
                    errors[name] = dataset_errors

        file.visititems(visit_item)
        return errors

def format_validation_results_markdown(results: Dict[str, List[str]]) -> str:
    """Format validation results as markdown"""
    lines = ["# HDF5 Validation Results\n"]

    # Summary
    total = len(results)
    valid = sum(1 for errors in results.values() if not errors)
    avg_error_count = np.mean([len(errors) for errors in results.values()])

    lines.extend(
        [
            "## Summary",
            f"- Total datasets validated: {total}",
            f"- Valid datasets: {valid} ({valid/total*100:.1f}%)",
            f"- Average error count: {avg_error_count:.2f}\n",
        ]
    )

    # Detailed results
    lines.append("## Detailed Results")

    for path, errors in sorted(results.items()):
        status_emoji = "✅" if not errors else "❌"
        lines.extend(
            [
                f"### {status_emoji} Dataset: `{path}`",
            ]
        )

        if errors:
            lines.append("- Errors:")
            for error in errors:
                lines.append(f"  - {error}")
        lines.append("")

    return "\n".join(lines)
