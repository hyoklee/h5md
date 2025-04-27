import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import h5py
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .diff import HDF5Differ
from .validation import DataValidator, ValidationResult


class HTMLReportGenerator:
    def __init__(
        self, template_dir: Optional[str] = None, max_preview_size: int = 1000
    ):
        self.max_preview_size = max_preview_size
        self.validator = DataValidator()
        self.differ = HDF5Differ()

    def _create_dataset_preview(self, dataset: h5py.Dataset) -> Dict[str, Any]:
        """Create a visual preview of the dataset"""
        preview = {
            "path": dataset.name,
            "shape": dataset.shape,
            "dtype": str(dataset.dtype),
            "size": dataset.size,
            "plots": [],
        }

        try:
            if dataset.size <= self.max_preview_size:
                data = dataset[()]

                if np.issubdtype(dataset.dtype, np.number):
                    # Create histogram
                    fig = go.Figure(data=[go.Histogram(x=data.flatten())])
                    fig.update_layout(
                        title=f"Distribution of values in {dataset.name}",
                        xaxis_title="Value",
                        yaxis_title="Count",
                    )
                    preview["plots"].append(
                        {"type": "histogram", "data": fig.to_json()}
                    )

                    # Create box plot
                    fig = go.Figure(data=[go.Box(y=data.flatten())])
                    fig.update_layout(
                        title=f"Box plot of values in {dataset.name}",
                        yaxis_title="Value",
                    )
                    preview["plots"].append({"type": "boxplot", "data": fig.to_json()})

                    # For 2D data, create heatmap
                    if len(dataset.shape) == 2:
                        fig = px.imshow(data)
                        fig.update_layout(title=f"Heatmap of {dataset.name}")
                        preview["plots"].append(
                            {"type": "heatmap", "data": fig.to_json()}
                        )

                # Add basic statistics
                if np.issubdtype(dataset.dtype, np.number):
                    preview["statistics"] = {
                        "min": float(np.min(data)),
                        "max": float(np.max(data)),
                        "mean": float(np.mean(data)),
                        "median": float(np.median(data)),
                        "std": float(np.std(data)),
                    }
        except Exception as e:
            preview["error"] = str(e)

        return preview

    def generate_report(
        self,
        file_path: str,
        output_dir: str,
        validation_schema: Optional[str] = None,
        diff_file: Optional[str] = None,
    ) -> str:
        """Generate an interactive HTML report for an HDF5 file"""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        report_data = {
            "file_info": {
                "path": file_path,
                "size": Path(file_path).stat().st_size,
                "modified": datetime.fromtimestamp(
                    Path(file_path).stat().st_mtime
                ).isoformat(),
                "created": datetime.fromtimestamp(
                    Path(file_path).stat().st_ctime
                ).isoformat(),
            },
            "structure": {},
            "previews": [],
            "validation": None,
            "diff": None,
        }

        # Load validation schema if provided
        if validation_schema:
            self.validator.load_schema(validation_schema)

        with h5py.File(file_path, "r") as f:
            # Add file attributes
            report_data["file_info"]["attributes"] = dict(f.attrs)

            # Process structure and generate previews
            def process_group(name, obj):
                if isinstance(obj, h5py.Dataset):
                    report_data["previews"].append(self._create_dataset_preview(obj))

                info = {
                    "type": "dataset" if isinstance(obj, h5py.Dataset) else "group",
                    "attributes": dict(obj.attrs),
                }

                if isinstance(obj, h5py.Dataset):
                    info.update(
                        {"shape": obj.shape, "dtype": str(obj.dtype), "size": obj.size}
                    )

                report_data["structure"][name] = info

            f.visititems(process_group)

        # Run validation if schema was provided
        if validation_schema:
            validation_results = self.validator.validate_file(file_path)
            report_data["validation"] = {
                path: {
                    "is_valid": result.is_valid,
                    "issues": result.issues,
                    "quality_score": result.quality_score,
                }
                for path, result in validation_results.items()
            }

        # Generate diff if comparison file was provided
        if diff_file:
            diff_results = self.differ.compare_files(file_path, diff_file)
            report_data["diff"] = diff_results

        # Generate HTML
        html_content = self._generate_html(report_data)

        # Save report
        output_file = output_dir / "report.html"
        output_file.write_text(html_content, encoding="utf-8")

        # Save data for interactive features
        data_file = output_dir / "report_data.js"
        data_file.write_text(
            f"const reportData = {json.dumps(report_data, indent=2)};", encoding="utf-8"
        )

        return str(output_file)

    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate the HTML report"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDF5 File Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="report_data.js"></script>
    <style>
        .plot-container {{
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">HDF5 File Analysis Report</h1>
        
        <!-- File Information -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">File Information</h2>
            <div id="fileInfo"></div>
        </div>
        
        <!-- Structure Tree -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">File Structure</h2>
            <div id="structureTree"></div>
        </div>
        
        <!-- Dataset Previews -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Dataset Previews</h2>
            <div id="datasetPreviews"></div>
        </div>
        
        <!-- Validation Results -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8" id="validationSection">
            <h2 class="text-xl font-semibold mb-4">Validation Results</h2>
            <div id="validationResults"></div>
        </div>
        
        <!-- Diff Results -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8" id="diffSection">
            <h2 class="text-xl font-semibold mb-4">File Comparison</h2>
            <div id="diffResults"></div>
        </div>
    </div>
    
    <script>
        // File Information
        function renderFileInfo() {{
            const info = reportData.file_info;
            const el = document.getElementById('fileInfo');
            el.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div><strong>Path:</strong> ${{info.path}}</div>
                    <div><strong>Size:</strong> ${{formatBytes(info.size)}}</div>
                    <div><strong>Modified:</strong> ${{new Date(info.modified).toLocaleString()}}</div>
                    <div><strong>Created:</strong> ${{new Date(info.created).toLocaleString()}}</div>
                </div>
            `;
        }}
        
        // Structure Tree
        function renderStructureTree() {{
            const structure = reportData.structure;
            const el = document.getElementById('structureTree');
            el.innerHTML = `
                <div class="font-mono text-sm">
                    ${{renderTreeNode('/', structure)}}
                </div>
            `;
        }}
        
        function renderTreeNode(path, structure) {{
            let html = '<ul class="pl-4">';
            for (const [name, info] of Object.entries(structure)) {{
                const fullPath = path + name;
                const icon = info.type === 'group' ? '📁' : '📄';
                html += `
                    <li class="mb-2">
                        <div class="flex items-center">
                            <span class="mr-2">${{icon}}</span>
                            <span class="font-semibold">${{name}}</span>
                        </div>
                        ${{info.type === 'dataset' ? renderDatasetInfo(info) : ''}}
                    </li>
                `;
            }}
            html += '</ul>';
            return html;
        }}
        
        // Dataset Previews
        function renderDatasetPreviews() {{
            const previews = reportData.previews;
            const el = document.getElementById('datasetPreviews');
            
            previews.forEach(preview => {{
                const container = document.createElement('div');
                container.className = 'mb-8 p-4 border rounded';
                
                container.innerHTML = `
                    <h3 class="text-lg font-semibold mb-4">${{preview.path}}</h3>
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div><strong>Shape:</strong> ${{preview.shape.join(' × ')}}</div>
                        <div><strong>Type:</strong> ${{preview.dtype}}</div>
                    </div>
                `;
                
                // Add plots
                preview.plots.forEach(plot => {{
                    const plotDiv = document.createElement('div');
                    plotDiv.className = 'plot-container';
                    container.appendChild(plotDiv);
                    Plotly.newPlot(plotDiv, JSON.parse(plot.data));
                }});
                
                el.appendChild(container);
            }});
        }}
        
        // Validation Results
        function renderValidationResults() {{
            if (!reportData.validation) {{
                document.getElementById('validationSection').style.display = 'none';
                return;
            }}
            
            const validation = reportData.validation;
            const el = document.getElementById('validationResults');
            
            let html = '<div class="space-y-4">';
            for (const [path, result] of Object.entries(validation)) {{
                const icon = result.is_valid ? '✅' : '❌';
                html += `
                    <div class="border rounded p-4">
                        <h3 class="font-semibold mb-2">${{icon}} ${{path}}</h3>
                        <div><strong>Quality Score:</strong> ${{result.quality_score.toFixed(2)}}</div>
                        ${{result.issues.length ? `
                            <div class="mt-2">
                                <strong>Issues:</strong>
                                <ul class="list-disc pl-4">
                                    ${{result.issues.map(issue => `<li>${{issue}}</li>`).join('')}}
                                </ul>
                            </div>
                        ` : ''}}
                    </div>
                `;
            }}
            html += '</div>';
            el.innerHTML = html;
        }}
        
        // Diff Results
        function renderDiffResults() {{
            if (!reportData.diff) {{
                document.getElementById('diffSection').style.display = 'none';
                return;
            }}
            
            const diff = reportData.diff;
            const el = document.getElementById('diffResults');
            
            let html = '<div class="space-y-4">';
            
            // File attribute changes
            if (Object.keys(diff.file_attr_changes).length) {{
                html += `
                    <div class="mb-4">
                        <h3 class="font-semibold mb-2">File Attribute Changes</h3>
                        <table class="w-full">
                            <thead>
                                <tr>
                                    <th class="text-left">Attribute</th>
                                    <th class="text-left">Old Value</th>
                                    <th class="text-left">New Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{Object.entries(diff.file_attr_changes)
                                    .map(([attr, [old_val, new_val]]) => `
                                        <tr>
                                            <td>${{attr}}</td>
                                            <td>${{old_val}}</td>
                                            <td>${{new_val}}</td>
                                        </tr>
                                    `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
            }}
            
            // Dataset changes
            if (Object.keys(diff.dataset_diffs).length) {{
                html += `
                    <div class="mb-4">
                        <h3 class="font-semibold mb-2">Dataset Changes</h3>
                        ${{Object.entries(diff.dataset_diffs)
                            .map(([path, diff]) => `
                                <div class="border rounded p-4 mb-4">
                                    <h4 class="font-semibold">${{path}}</h4>
                                    ${{diff.exists_in_both ? `
                                        <div class="mt-2">
                                            <div>Shape changed: ${{diff.shape_changed}}</div>
                                            <div>Type changed: ${{diff.dtype_changed}}</div>
                                            ${{diff.data_changes ? `
                                                <div class="mt-2">
                                                    <strong>Data Changes:</strong>
                                                    <div>Changed elements: ${{diff.changed_elements}} / ${{diff.total_elements}}</div>
                                                    <div>Max difference: ${{diff.max_diff}}</div>
                                                    <div>Mean difference: ${{diff.mean_diff}}</div>
                                                </div>
                                            ` : ''}}
                                        </div>
                                    ` : `<div class="mt-2">Dataset ${{diff.removed_children ? 'removed' : 'added'}}</div>`}}
                                </div>
                            `).join('')}}
                    </div>
                `;
            }}
            
            html += '</div>';
            el.innerHTML = html;
        }}
        
        // Utility functions
        function formatBytes(bytes) {{
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            let value = bytes;
            let unit = 0;
            while (value > 1024 && unit < units.length - 1) {{
                value /= 1024;
                unit++;
            }}
            return `${{value.toFixed(1)}} ${{units[unit]}}`;
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            renderFileInfo();
            renderStructureTree();
            renderDatasetPreviews();
            renderValidationResults();
            renderDiffResults();
        }});
    </script>
</body>
</html>
"""


def generate_report(
    file_path: str,
    output_dir: str,
    validation_schema: Optional[str] = None,
    diff_file: Optional[str] = None,
) -> str:
    """Convenience function to generate an HTML report"""
    generator = HTMLReportGenerator()
    return generator.generate_report(
        file_path, output_dir, validation_schema, diff_file
    )
