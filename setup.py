from setuptools import setup, find_packages

setup(
    name="hexgame",
    version="0.1",
    packages=find_packages(),
    package_dir={'': 'src'}
) 

# pip install -e .