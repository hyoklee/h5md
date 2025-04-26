import argparse
import sys
from pathlib import Path
from .advanced_viewer import generate_advanced_markdown
from .validation import DataValidator, format_validation_results_markdown
from .diff import HDF5Differ, format_diff_markdown
from .html_report import generate_report

def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation and analysis for HDF5 files"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Input HDF5 file path"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: input_file_name.md)"
    )
    parser.add_argument(
        "--preview-size",
        type=int,
        default=5,
        help="Maximum number of elements to show in data previews (default: 5)"
    )
    parser.add_argument(
        "--format",
        choices=['markdown', 'html', 'json'],
        default='markdown',
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--validate",
        type=str,
        help="Path to validation schema file"
    )
    parser.add_argument(
        "--diff",
        type=str,
        help="Path to HDF5 file to compare against"
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter pattern for groups/datasets (e.g., '/data/*')"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for HTML report assets"
    )

    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not args.output:
        if args.format == 'html':
            output_path = Path(args.output_dir) / 'report.html'
        else:
            output_path = input_path.with_suffix(f'.{args.format}')
    else:
        output_path = Path(args.output)
    
    try:
        if args.format == 'html':
            # Generate HTML report
            output_path = generate_report(
                str(input_path),
                args.output_dir,
                args.validate,
                args.diff
            )
            print(f"Generated HTML report: {output_path}")
            
        elif args.format == 'markdown':
            # Generate markdown with optional validation and diff
            content = []
            
            # Main HDF5 content
            content.append(generate_advanced_markdown(
                str(input_path),
                max_preview=args.preview_size,
                filter_pattern=args.filter
            ))
            
            # Add validation results if requested
            if args.validate:
                validator = DataValidator()
                validator.load_schema(args.validate)
                results = validator.validate_file(str(input_path))
                content.append("\n" + format_validation_results_markdown(results))
            
            # Add diff results if requested
            if args.diff:
                differ = HDF5Differ()
                diff_results = differ.compare_files(str(input_path), args.diff)
                content.append("\n" + format_diff_markdown(diff_results))
            
            # Write output
            output_path.write_text("\n".join(content), encoding='utf-8')
            print(f"Generated markdown documentation: {output_path}")
            
        else:  # JSON
            import json
            from .json_export import export_to_json
            export_to_json(str(input_path), str(output_path))
            print(f"Generated JSON metadata: {output_path}")
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
