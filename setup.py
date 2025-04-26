from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="markitdown-hdf5",
    version="0.1.0",
    description="A plugin for markitdown to convert HDF5 files to markdown",
    author="H. Joe Lee",
    author_email="hyoklee@hdfgroup.org",
    packages=find_packages(),
    install_requires=[
        "markitdown>0.0.1",
        "h5py>=3.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'h5md=markitdown_hdf5.cli:main',
        ],
        "markitdown.plugins": [
            "hdf5 = markitdown_hdf5:register"
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/markitdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)
