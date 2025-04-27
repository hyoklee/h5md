import argparse
import os
from pathlib import Path

from . import HDF5Converter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert HDF5 files to markdown format"
    )
    parser.add_argument("file", help="HDF5 file to convert")
    args = parser.parse_args()

    converter = HDF5Converter()
    result = converter.convert(args.file)

    # Save to file with .md extension
    output_path = Path(args.file).with_suffix(".md")
    with open(output_path, "w") as f:
        f.write(result)


if __name__ == "__main__":
    main()
