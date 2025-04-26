from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="markitdown-hdf5",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "h5py>=3.0.0",
        "markitdown @ git+https://github.com/microsoft/markitdown.git@main",
        "numpy>=1.19.0",
    ],
    entry_points={
        'console_scripts': [
            'h5md=markitdown_hdf5.cli:main',
        ],
        'markitdown.plugins': [
            'hdf5=markitdown_hdf5:register',
        ],
    },
    author="Cascade",
    author_email="your.email@example.com",
    description="A Markitdown plugin for HDF5 metadata visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/markitdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)
