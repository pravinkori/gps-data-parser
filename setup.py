import os
from setuptools import setup, find_packages

# Read the contents of README.md for the long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gps-data-parser',  # Name of package
    version='0.1.0',  # Initial version
    description='A GPS data parser for extracting, storing, and analyzing location data from GPS devices.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pravin Kori',
    author_email='pravinkori@protonmail.ch',
    url='https://github.com/pravinkori/gps-data-parser',  # GitHub URL
    license='MIT',  # License type
    license_files=('LICENSE',),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    keywords='GPS parser data analysis',
    packages=find_packages(where='src'),  # Automatically find packages in the 'src' directory
    package_dir={'': 'src'},  # Root of the packages is 'src'
    python_requires='>=3.8',  # Minimum Python version required
    install_requires=[
        'pytz>=2023.3',
        'mysql-connector-python>=8.0.33',
        'pyserial>=3.5',
    ],  # Dependencies
    extras_require={
        'dev': ['pytest>=7.0', 'flake8>=5.0'],  # Development dependencies
    },
    entry_points={
        'console_scripts': [
            'gps-parser=src.gps_parser:main',  # Command-line entry point
        ],
    },
    include_package_data=True,  # Include non-code files from MANIFEST.in
    zip_safe=False,  # This ensures the package can be extracted if necessary
)
