import argparse
import sys
from pathlib import Path

from h5md import HDF5Converter


def main() -> None:
    """Command-line interface for HDF5 to markdown converter."""
    parser = argparse.ArgumentParser(
        description="Convert HDF5 files to markdown format"
    )
    parser.add_argument("file", help="HDF5 file to convert")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output markdown file path "
            "(defaults to input file with .md extension)"
        ),
        default=None,
    )
    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.file).is_file():
        msg = (
            f"Error: Input file '{args.file}' does not exist"
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    try:
        # If no output path is specified, use input path with .md extension
        output_path = args.output
        if output_path is None:
            output_path = str(Path(args.file).with_suffix(".md"))

        converter = HDF5Converter()
        converter.convert(args.file, output_path)
        print(f"Successfully converted {args.file} to {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
