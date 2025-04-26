import os
import h5py
import numpy as np
import pytest
from markitdown_hdf5 import HDF5Plugin
from markitdown import MarkdownBuilder

@pytest.fixture
def sample_hdf5_file(tmp_path):
    """Create a sample HDF5 file for testing"""
    file_path = tmp_path / "test.h5"
    
    with h5py.File(file_path, 'w') as f:
        # Add file attributes
        f.attrs['description'] = 'Test HDF5 file'
        
        # Create a group
        group = f.create_group('data')
        group.attrs['purpose'] = 'testing'
        
        # Create datasets
        dset1 = group.create_dataset('array', data=np.array([1, 2, 3]))
        dset1.attrs['unit'] = 'meters'
        
        dset2 = group.create_dataset('matrix', data=np.ones((2, 2)))
    
    return file_path

def test_plugin_initialization():
    plugin = HDF5Plugin()
    assert plugin.name == "hdf5"
    assert plugin.description == "Plugin for visualizing HDF5 metadata"

def test_plugin_can_handle():
    plugin = HDF5Plugin()
    assert plugin.can_handle('test.h5') is True
    assert plugin.can_handle('test.hdf5') is True
    assert plugin.can_handle('test.txt') is False

def test_plugin_process_file(sample_hdf5_file):
    plugin = HDF5Plugin()
    builder = MarkdownBuilder()
    
    plugin.process_file(str(sample_hdf5_file), builder)
    output = builder.build()
    
    # Check for expected content
    assert "Test HDF5 file" in output
    assert "data" in output
    assert "array" in output
    assert "matrix" in output
    assert "meters" in output

def test_cli_basic(sample_hdf5_file):
    from markitdown_hdf5.cli import main
    import sys
    
    # Prepare command line arguments
    sys.argv = ['h5md', str(sample_hdf5_file)]
    
    # Run CLI (should create output file)
    main()
    
    # Check if output file exists
    output_file = sample_hdf5_file.with_suffix('.md')
    assert output_file.exists()
    
    # Check content
    content = output_file.read_text()
    assert "Test HDF5 file" in content
    assert "data" in content
