import h5py
from markitdown import MarkdownBuilder
from markitdown_hdf5 import HDF5Plugin

# Create a markdown builder
builder = MarkdownBuilder()

# Initialize our plugin
plugin = HDF5Plugin()

# Process the sample file directly
plugin.process_file("sample.h5", builder)

# Get the markdown output
output = builder.build()

# Save the output
with open("sample_output.md", "w") as f:
    f.write(output)

print("Generated markdown output in sample_output.md")
