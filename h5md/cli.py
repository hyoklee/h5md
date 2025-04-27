import argparse
from h5md import HDF5Converter


def main() -> None:
    """Command-line interface for HDF5 to markdown converter."""
    parser = argparse.ArgumentParser(
        description="Convert HDF5 files to markdown format"
    )
    parser.add_argument("file", help="HDF5 file to convert")
    parser.add_argument(
        "-o", "--output", help="Output markdown file path", default=None
    )
    args = parser.parse_args()

    converter = HDF5Converter()
    converter.convert(args.file, args.output)


if __name__ == "__main__":
    main()
