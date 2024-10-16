from setuptools import setup, find_packages

setup(
    name='multasker',
    version='0.1',
    packages=find_packages(),
    install_requires=[],  # List any external dependencies here
    author='Sean Lum',
    author_email='seanjklum@gmail.com',
    description='A package for managing multiprocessing and multithreading tasks',
    url='https://github.com/seanlum/multasker',  # Replace with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)