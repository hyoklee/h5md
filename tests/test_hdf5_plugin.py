import h5py
import numpy as np
import pytest

from h5md import HDF5Converter


@pytest.fixture
def sample_hdf5_file(tmp_path):
    """Create a sample HDF5 file for testing"""
    file_path = tmp_path / "test.h5"

    with h5py.File(file_path, "w") as f:
        # Add file attributes
        f.attrs["description"] = "Test HDF5 file"

        # Create a group
        group = f.create_group("data")
        group.attrs["purpose"] = "testing"

        # Create datasets
        dset1 = group.create_dataset("array", data=np.array([1, 2, 3]))
        dset1.attrs["unit"] = "meters"

        # Create a matrix dataset
        group.create_dataset("matrix", data=np.ones((2, 2)))

        # Create an external link
        external_file_path = tmp_path / "external_target.h5"
        with h5py.File(external_file_path, "w") as ext_f:
            ext_f.create_dataset("linked_data", data=np.array([4, 5, 6]))
        
        f["external_link"] = h5py.ExternalLink(external_file_path.name, "/linked_data")

    return file_path


def test_hdf5_conversion(sample_hdf5_file):
    converter = HDF5Converter()
    result = converter.convert(str(sample_hdf5_file))

    # Check for expected content
    assert "Test HDF5 file" in result
    assert "data" in result
    assert "array" in result
    assert "matrix" in result
    assert "meters" in result


def test_hdf5_external_link_conversion(sample_hdf5_file):
    converter = HDF5Converter()
    result = converter.convert(str(sample_hdf5_file))

    assert "External Link: external_link" in result
    assert "Target File:" in result
    assert "external_target.h5" in result
    assert "Target Path:" in result
    assert "/linked_data" in result


def test_cli_basic(sample_hdf5_file):
    import sys

    from h5md.cli import main

    # Prepare command line arguments
    sys.argv = ["h5md", str(sample_hdf5_file)]

    # Run CLI (should create output file)
    main()

    # Check if output file exists
    output_file = sample_hdf5_file.with_suffix(".md")
    assert output_file.exists()

    # Check content
    content = output_file.read_text()
    assert "Test HDF5 file" in content
    assert "data" in content
