
from setuptools import setup, find_packages
import pathlib

readme = pathlib.Path(__file__).parent / "README.md"
long_description = readme.read_text()

setup(
    name='multasker',
    version='0.3.3',
    packages=find_packages(),
    install_requires=[],  # List any external dependencies here
    author='kalanik0a',
    author_email='seanjklum@gmail.com',
    description='A package for managing multiprocessing and multithreading tasks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://pypi.org/project/multasker/',  # Replace with your repository URL
    project_urls={
        "Source": "https://github.com/kalanik0a/multasker"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
