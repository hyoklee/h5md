import sys
import argparse
from markitdown import MarkItDown
from . import HDF5Plugin

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
    md = MarkItDown(enable_plugins=True)  # Enable plugins to use our HDF5 plugin
    result = md.convert(args.input)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.text_content)

if __name__ == '__main__':
    main()
