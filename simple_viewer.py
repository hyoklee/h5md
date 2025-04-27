import h5py


def generate_markdown_for_hdf5(file_path):
    markdown = []

    def add_line(text, indent=0):
        markdown.append("    " * indent + text)

    def process_attrs(item, indent=0):
        if len(item.attrs) > 0:
            add_line("**Attributes:**", indent)
            for key, value in item.attrs.items():
                add_line(f"- `{key}`: `{value}` ({type(value).__name__})", indent + 1)

    def process_group(group, indent=0):
        process_attrs(group, indent)

        for name, item in group.items():
            if isinstance(item, h5py.Dataset):
                add_line(f"### Dataset: `{name}`", indent)
                add_line(f"- Shape: `{item.shape}`", indent + 1)
                add_line(f"- Type: `{item.dtype}`", indent + 1)
                process_attrs(item, indent + 1)

            elif isinstance(item, h5py.Group):
                add_line(f"## Group: `{name}`", indent)
                process_group(item, indent + 1)

    try:
        with h5py.File(file_path, "r") as f:
            add_line(f"# HDF5 File Structure: {file_path}")
            process_group(f)

        return "\n".join(markdown)
    except Exception as e:
        return f"Error processing HDF5 file: {str(e)}"


# Process the sample file
output = generate_markdown_for_hdf5("sample.h5")

# Save the output
with open("sample_output.md", "w") as f:
    f.write(output)

print("Generated markdown output in sample_output.md")
