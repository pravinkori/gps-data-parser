from setuptools import setup, find_packages

setup(
    name='gps-data-parser',  # Name of package
    version='0.1.0',  # Initial version
    description='A GPS data parser for extracting, storing, and analyzing location data from GPS devices.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your_email@example.com',
    url='https://github.com/pravinkori/gps-data-parser',  # GitHub URL
    license='MIT',  # License type
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
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
            'gps-parser=gps_parser:main',  # Command-line entry point
        ],
    },
    include_package_data=True,  # Include non-code files from MANIFEST.in
    zip_safe=False,  # This ensures the package can be extracted if necessary
)
