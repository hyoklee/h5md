import argparse
import sys
from pathlib import Path

from h5md import HDF5Converter


def main() -> None:
    """Command-line interface for HDF5 to markdown converter."""
    parser = argparse.ArgumentParser(
        description="Convert HDF5 files to AI-friendly markdown format with key-value structure"
    )
    parser.add_argument("file", help="HDF5 file to convert")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output markdown file path " "(defaults to input file with .md extension)"
        ),
        default=None,
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=10,
        help="Maximum number of rows to include in dataset previews (default: 10, use 0 for all)",
    )
    parser.add_argument(
        "--max-cols",
        type=int,
        default=10,
        help="Maximum number of columns to include in dataset previews (default: 10, use 0 for all)",
    )
    parser.add_argument(
        "--sampling",
        choices=["first", "uniform", "edges"],
        default="first",
        help=(
            "Sampling strategy when limits are exceeded: "
            "'first' (default) takes first N items, "
            "'uniform' samples uniformly across dataset, "
            "'edges' shows first and last items"
        ),
    )
    parser.add_argument(
        "--no-data",
        action="store_true",
        help="Exclude actual data values from output (metadata only)",
    )
    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.file).is_file():
        msg = ("Error: Input file '{}' does not exist").format(args.file)
        print(msg, file=sys.stderr)
        sys.exit(1)

    try:
        # If no output path is specified, use input path with .md extension
        output_path = args.output
        if output_path is None:
            output_path = str(Path(args.file).with_suffix(".md"))

        # Convert 0 to None (meaning no limit)
        max_rows = None if args.max_rows == 0 else args.max_rows
        max_cols = None if args.max_cols == 0 else args.max_cols

        converter = HDF5Converter(
            max_rows=max_rows,
            max_cols=max_cols,
            sampling_strategy=args.sampling,
            include_data_preview=not args.no_data,
        )
        converter.convert(args.file, output_path)
        print(f"Successfully converted {args.file} to {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
