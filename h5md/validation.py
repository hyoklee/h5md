import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import h5py
import numpy as np


@dataclass
class ValidationRule:
    path: str  # HDF5 path pattern
    dtype: Optional[str] = None  # Expected dtype
    shape: Optional[Tuple[Optional[int], ...]] = (
        None  # Expected shape (None for variable dimension)
    )
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required_attrs: Optional[List[str]] = None
    custom_validator: Optional[callable] = None
    allow_nan: bool = True
    allow_inf: bool = True


@dataclass
class ValidationResult:
    path: str
    is_valid: bool
    issues: List[str]
    quality_score: float  # 0.0 to 1.0


class DataValidator:
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}

    def add_rule(self, rule: ValidationRule):
        self.rules[rule.path] = rule

    def load_schema(self, schema_file: str):
        """Load validation rules from JSON schema file"""
        with open(schema_file, "r") as f:
            schema = json.load(f)

        for path, rules in schema.items():
            shape = tuple(rules.get("shape", [None]))
            self.add_rule(
                ValidationRule(
                    path=path,
                    dtype=rules.get("dtype"),
                    shape=shape if shape != (None,) else None,
                    min_value=rules.get("min_value"),
                    max_value=rules.get("max_value"),
                    required_attrs=rules.get("required_attrs", []),
                    allow_nan=rules.get("allow_nan", True),
                    allow_inf=rules.get("allow_inf", True),
                )
            )

    def _check_numeric_constraints(
        self, data: np.ndarray, rule: ValidationRule
    ) -> List[str]:
        issues = []

        if not rule.allow_nan and np.any(np.isnan(data)):
            issues.append("Contains NaN values")

        if not rule.allow_inf and np.any(np.isinf(data)):
            issues.append("Contains infinite values")

        if rule.min_value is not None and np.any(data < rule.min_value):
            issues.append(f"Values below minimum ({rule.min_value})")

        if rule.max_value is not None and np.any(data > rule.max_value):
            issues.append(f"Values above maximum ({rule.max_value})")

        return issues

    def _calculate_quality_score(self, data: np.ndarray, issues: List[str]) -> float:
        """Calculate a quality score based on various metrics"""
        score = 1.0

        if issues:
            score -= len(issues) * 0.1

        if np.issubdtype(data.dtype, np.number):
            # Check for data spread
            if np.all(data == data.flat[0]):
                score -= 0.2  # Constant values

            # Check for outliers using IQR
            q1, q3 = np.percentile(data, [25, 75])
            iqr = q3 - q1
            outliers = np.logical_or(data < q1 - 1.5 * iqr, data > q3 + 1.5 * iqr)
            score -= np.mean(outliers) * 0.3

            # Check for missing values
            if np.issubdtype(data.dtype, np.floating):
                score -= np.mean(np.isnan(data)) * 0.4

        return max(0.0, min(1.0, score))

    def validate_dataset(
        self, dataset: h5py.Dataset, rule: ValidationRule
    ) -> ValidationResult:
        issues = []

        # Check dtype
        if rule.dtype and str(dataset.dtype) != rule.dtype:
            issues.append(
                f"Incorrect dtype: expected {rule.dtype}, got {dataset.dtype}"
            )

        # Check shape
        if rule.shape:
            if len(dataset.shape) != len(rule.shape):
                issues.append(
                    f"Incorrect number of dimensions: expected {len(rule.shape)}, got {len(dataset.shape)}"
                )
            else:
                for expected, actual in zip(rule.shape, dataset.shape):
                    if expected is not None and expected != actual:
                        issues.append(
                            f"Incorrect dimension size: expected {expected}, got {actual}"
                        )

        # Check attributes
        if rule.required_attrs:
            missing_attrs = set(rule.required_attrs) - set(dataset.attrs.keys())
            if missing_attrs:
                issues.append(
                    f"Missing required attributes: {', '.join(missing_attrs)}"
                )

        # Check numeric constraints
        if np.issubdtype(dataset.dtype, np.number):
            issues.extend(self._check_numeric_constraints(dataset[()], rule))

        # Run custom validator if provided
        if rule.custom_validator:
            custom_issues = rule.custom_validator(dataset)
            if custom_issues:
                issues.extend(custom_issues)

        # Calculate quality score
        quality_score = self._calculate_quality_score(dataset[()], issues)

        return ValidationResult(
            path=dataset.name,
            is_valid=len(issues) == 0,
            issues=issues,
            quality_score=quality_score,
        )

    def validate_file(self, file_path: str) -> Dict[str, ValidationResult]:
        results = {}

        with h5py.File(file_path, "r") as f:
            # Validate each dataset against matching rules
            def validate_group(name, obj):
                if isinstance(obj, h5py.Dataset):
                    # Find matching rule (support wildcards)
                    for rule_path, rule in self.rules.items():
                        if re.match(rule_path.replace("*", ".*"), name):
                            results[name] = self.validate_dataset(obj, rule)
                            break

            f.visititems(validate_group)

        return results


def format_validation_results_markdown(results: Dict[str, ValidationResult]) -> str:
    """Format validation results as markdown"""
    lines = ["# HDF5 Validation Results\n"]

    # Summary
    total = len(results)
    valid = sum(1 for r in results.values() if r.is_valid)
    avg_quality = np.mean([r.quality_score for r in results.values()])

    lines.extend(
        [
            "## Summary",
            f"- Total datasets validated: {total}",
            f"- Valid datasets: {valid} ({valid/total*100:.1f}%)",
            f"- Average quality score: {avg_quality:.2f}\n",
        ]
    )

    # Detailed results
    lines.append("## Detailed Results")

    for path, result in sorted(results.items()):
        status_emoji = "✅" if result.is_valid else "❌"
        lines.extend(
            [
                f"### {status_emoji} Dataset: `{path}`",
                f"- Quality Score: {result.quality_score:.2f}",
            ]
        )

        if result.issues:
            lines.append("- Issues:")
            for issue in result.issues:
                lines.append(f"  - {issue}")
        lines.append("")

    return "\n".join(lines)
