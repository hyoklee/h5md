from markitdown import Markitdown
from markitdown_hdf5 import HDF5Plugin

# Initialize Markitdown
md = Markitdown()

# Register our plugin
plugin = HDF5Plugin()
md.register_plugin(plugin)

# Process the sample file
output = md.process_file('sample.h5')

# Save the output
with open('sample_output.md', 'w') as f:
    f.write(output)

print("Generated markdown output in sample_output.md")
