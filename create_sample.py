import h5py
import numpy as np

# Create a sample HDF5 file
with h5py.File("sample.h5", "w") as f:
    # Add some file-level attributes
    f.attrs["description"] = "Sample HDF5 file for testing markitdown plugin"
    f.attrs["created_by"] = "markitdown-hdf5 test script"

    # Create a group for sensor data
    sensors = f.create_group("sensors")
    sensors.attrs["location"] = "Building A"

    # Add temperature data
    temp = sensors.create_dataset("temperature", data=np.random.rand(24))
    temp.attrs["unit"] = "celsius"
    temp.attrs["sampling_rate"] = "1 per hour"

    # Create a group for metadata
    meta = f.create_group("metadata")
    meta.attrs["version"] = "1.0"

    # Add configuration data
    config = meta.create_dataset(
        "config", data=np.array(["high", "medium", "low"], dtype="S10")
    )
    config.attrs["type"] = "settings"

    # Add some numeric data with different shapes
    data = f.create_group("data")
    data.create_dataset("matrix", data=np.random.rand(3, 3))
    data.create_dataset("timeseries", data=np.arange(100))

print("Created sample.h5 file with example data and metadata")
