from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="h5md",
    version="0.1.0",
    description="A command-line tool to convert HDF5 files to markdown",
    author="Joe Lee",
    author_email="joe@example.com",
    packages=find_packages(),
    install_requires=[
        "h5py>=3.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'h5md=h5md.cli:main',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/markitdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
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
