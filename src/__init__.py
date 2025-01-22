"""
GPS Data Parser
~~~~~~~~~~~~~~

A robust GPS data parsing and processing system for handling NMEA sentences.

This package provides tools for:
    - Parsing GPS NMEA sentences (GNGGA, GNVTG)
    - Real-time GPS data processing
    - Database storage of GPS data
    - Coordinate validation and conversion

Basic usage:
    >>> from src import GPSParser
    >>> parser = GPSParser()
    >>> parser.connect_to_serial()
    >>> parser.connect_to_database()
    >>> parser.start()

For more information, please see the README.md file.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Package metadata
__title__ = 'gps-data-parser'
__version__ = '0.1.0'
__author__ = 'Your Name'
__author_email__ = 'your.email@example.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024 Your Name'

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Import main components
from .gps_parser import GPSParser

# Version information
VERSION: Dict[str, int] = {
    'major': 0,
    'minor': 1,
    'patch': 0
}

def get_version() -> str:
    """Return the current version of the package."""
    return f"{VERSION['major']}.{VERSION['minor']}.{VERSION['patch']}"

def setup_logging(
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> None:
    """
    Configure package-wide logging.

    Args:
        log_file: Path to log file. If None, logs to stderr.
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages.
            If None, uses default format.

    Returns:
        None
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_string,
        filename=log_file,
        filemode='a' if log_file else 'w'
    )

def get_config_path() -> Path:
    """Return the default configuration directory path."""
    return Path(__file__).parent.parent / 'config'

def initialize(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize the package with configuration.

    Args:
        config_file: Optional path to configuration file.
            If None, uses default config path.

    Returns:
        Dict containing configuration settings.
    """
    if config_file is None:
        config_file = get_config_path() / 'config.ini'
    
    # Add initialization logic here
    config: Dict[str, Any] = {
        'version': get_version(),
        'config_path': str(config_file)
    }
    
    return config

__all__ = [
    'GPSParser',
    'get_version',
    'setup_logging',
    'initialize',
    '__version__',
    '__author__',
    '__license__'
]