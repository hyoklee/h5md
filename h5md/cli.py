import sys
import argparse
from . import HDF5Converter

def main():
    parser = argparse.ArgumentParser(description='Convert HDF5 files to Markdown')
    parser.add_argument('input', help='Input HDF5 file')
    parser.add_argument('-o', '--output', help='Output Markdown file (default: input file with .md extension)')
    
    args = parser.parse_args()
    
    # Set up output file path
    output_path = args.output
    if not output_path:
        output_path = args.input.rsplit('.', 1)[0] + '.md'
    
    # Convert file
    converter = HDF5Converter()
    markdown_content = converter.convert(args.input)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

if __name__ == '__main__':
    main()
