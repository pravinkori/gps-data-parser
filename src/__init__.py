"""
GPS Data Parser Package
~~~~~~~~~~~~~~~~~~~~~~

A robust package for parsing and storing GPS data from NMEA devices.

Features:
    - Automatic serial port detection
    - NMEA sentence parsing (GNGGA, GNVTG)
    - Database storage with connection pooling
    - Configurable logging
    - Error handling and recovery
"""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Set up package logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Package metadata
__title__ = 'gps-data-parser'
__version__ = '0.2.0'
__author__ = 'Your Name'
__author_email__ = 'your.email@example.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024 Your Name'

# Import main components
from .gps_parser import (
    GPSParser,
    GPSConfig,
)

from .utils import (
    GPSCoordinate,
    GPSData,
    DatabaseManager,
    NMEAParser,
    GPSConnectionError,
    DatabaseConnectionError,
    NMEAParseError
)

@dataclass
class Version:
    """Version information for the package."""
    major: int = 0
    minor: int = 2
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

VERSION = Version()

def get_version() -> str:
    """Return the current version of the package."""
    return str(VERSION)

def setup_logging(
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure package-wide logging with rotation support.

    Args:
        log_file: Path to log file. If None, logs to stderr
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        None
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if log_file:
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)

def get_config_path() -> Path:
    """Return the default configuration directory path."""
    return Path(__file__).parent.parent / 'config'

def initialize(
    config_file: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: int = logging.INFO
) -> Dict[str, Any]:
    """
    Initialize the package with configuration and logging.

    Args:
        config_file: Optional path to configuration file
        log_file: Optional path to log file
        log_level: Logging level to use

    Returns:
        Dict containing initialization status and configuration
    """
    if config_file is None:
        config_file = str(get_config_path() / 'config.ini')

    # Setup logging first
    setup_logging(log_file=log_file, level=log_level)
    logger = logging.getLogger(__name__)

    try:
        # Verify config file exists
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        config: Dict[str, Any] = {
            'version': get_version(),
            'config_path': config_file,
            'log_file': log_file,
            'log_level': log_level,
            'initialized': True
        }

        logger.info(f"Package initialized successfully (version {get_version()})")
        return config

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return {
            'version': get_version(),
            'initialized': False,
            'error': str(e)
        }

__all__ = [
    # Main classes
    'GPSParser',
    'GPSConfig',
    'DatabaseManager',
    'NMEAParser',
    
    # Data classes
    'GPSCoordinate',
    'GPSData',
    
    # Exceptions
    'GPSConnectionError',
    'DatabaseConnectionError',
    'NMEAParseError',
    
    # Functions
    'get_version',
    'setup_logging',
    'initialize',
    
    # Package metadata
    '__version__',
    '__author__',
    '__license__',
]