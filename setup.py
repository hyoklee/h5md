from setuptools import find_packages, setup

setup(
    name="h5md",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "h5py>=3.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "h5md=h5md.cli:main",
        ],
    },
    python_requires=">=3.10",
    author="Joe Lee",
    author_email="hyoklee@hdfgroup.org",
    description="A command-line tool to convert HDF5 files to markdown format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="hdf5, markdown, converter",
    url="https://github.com/hyoklee/h5md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
)
