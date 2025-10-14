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


@pytest.fixture
def large_hdf5_file(tmp_path):
    """Create a large HDF5 file for testing subsetting"""
    file_path = tmp_path / "large_test.h5"

    with h5py.File(file_path, "w") as f:
        # Create large 1D array
        f.create_dataset("large_array", data=np.arange(100))

        # Create large 2D matrix
        f.create_dataset("large_matrix", data=np.arange(300).reshape(30, 10))

        # Create 3D array
        f.create_dataset("cube", data=np.arange(1000).reshape(10, 10, 10))

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


def test_key_value_format(sample_hdf5_file):
    """Test that output uses key-value format"""
    converter = HDF5Converter()
    result = converter.convert(str(sample_hdf5_file))

    # Check for key-value format indicators
    assert "**Shape:**" in result
    assert "**Data Type:**" in result
    assert "**Size:**" in result
    assert "Data (Key-Value Format):" in result


def test_subsetting_max_rows(large_hdf5_file):
    """Test row subsetting with max_rows parameter"""
    converter = HDF5Converter(max_rows=5, include_data_preview=True)
    result = converter.convert(str(large_hdf5_file))

    # Check that subsetting information is included
    assert "showing 5 of 100" in result or "index_4" in result
    # Should not show all 100 rows
    assert "index_99" not in result


def test_subsetting_max_cols(large_hdf5_file):
    """Test column subsetting with max_cols parameter"""
    converter = HDF5Converter(max_rows=5, max_cols=5, include_data_preview=True)
    result = converter.convert(str(large_hdf5_file))

    # Check for column subsetting in 2D data
    assert "showing" in result and "cols" in result


def test_sampling_strategies(large_hdf5_file):
    """Test different sampling strategies"""
    # Test 'first' strategy
    converter_first = HDF5Converter(
        max_rows=5, sampling_strategy="first", include_data_preview=True
    )
    result_first = converter_first.convert(str(large_hdf5_file))
    assert "index_0" in result_first
    assert "index_4" in result_first

    # Test 'uniform' strategy
    converter_uniform = HDF5Converter(
        max_rows=5, sampling_strategy="uniform", include_data_preview=True
    )
    result_uniform = converter_uniform.convert(str(large_hdf5_file))
    assert "sampling" in result_uniform.lower()

    # Test 'edges' strategy
    converter_edges = HDF5Converter(
        max_rows=6, sampling_strategy="edges", include_data_preview=True
    )
    result_edges = converter_edges.convert(str(large_hdf5_file))
    assert "sampling" in result_edges.lower()


def test_no_data_preview(sample_hdf5_file):
    """Test conversion without data preview"""
    converter = HDF5Converter(include_data_preview=False)
    result = converter.convert(str(sample_hdf5_file))

    # Should have metadata but not data values
    assert "**Shape:**" in result
    assert "Data (Key-Value Format):" not in result


def test_multidimensional_arrays(large_hdf5_file):
    """Test handling of 3D and higher dimensional arrays"""
    converter = HDF5Converter(include_data_preview=True)
    result = converter.convert(str(large_hdf5_file))

    # Check for 3D array handling
    assert "cube" in result
    assert "Multi-dimensional Array" in result or "element_" in result


def test_cli_with_options(large_hdf5_file, tmp_path):
    """Test CLI with new subsetting options"""
    import sys

    from h5md.cli import main

    output_file = tmp_path / "output_with_options.md"

    sys.argv = [
        "h5md",
        str(large_hdf5_file),
        "-o",
        str(output_file),
        "--max-rows",
        "3",
        "--max-cols",
        "3",
        "--sampling",
        "edges",
    ]

    main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "showing" in content.lower() or "index_" in content


def test_cli_no_data_flag(sample_hdf5_file, tmp_path):
    """Test CLI with --no-data flag"""
    import sys

    from h5md.cli import main

    output_file = tmp_path / "output_no_data.md"

    sys.argv = ["h5md", str(sample_hdf5_file), "-o", str(output_file), "--no-data"]

    main()

    assert output_file.exists()
    content = output_file.read_text()
    # Should have properties but not data values
    assert "Properties" in content
    assert "Data (Key-Value Format):" not in content
