"""
GPS Data Parser Utilities
~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive module for GPS data processing, validation, and database operations.

Features:
    - GPS coordinate validation and conversion
    - NMEA sentence parsing (GNGGA, GNVTG)
    - Timezone conversion utilities
    - Database operations with connection pooling
    - Rotating log management
    - Type-safe data structures
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union, Tuple

# Setup module logger
logger = logging.getLogger(__name__)

# Import all classes and utilities
from .helpers import (
    # Custom Exceptions
    GPSConnectionError,
    DatabaseConnectionError,
    NMEAParseError,

    # Data Classes
    GPSCoordinate,
    GPSData,

    # Database Management
    DatabaseManager,

    # NMEA Parsing
    NMEAParser,

    # Validation Functions
    is_valid_latitude,
    is_valid_longitude,
    
    # Conversion Functions
    knots_to_kmh,
    decimal_degrees_to_dms,
    utc_to_timezone,
    format_gps_datetime,
    
    # Helper Functions
    dataclass_to_dict,
    
    # Logging Setup
    setup_logging
)

def validate_coordinates(
    latitude: float,
    longitude: float
) -> Tuple[bool, Optional[str]]:
    """
    Validate a pair of coordinates.

    Args:
        latitude: Latitude value to validate
        longitude: Longitude value to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
        error_message is None if coordinates are valid
    """
    try:
        GPSCoordinate(latitude=latitude, longitude=longitude)
        return True, None
    except ValueError as e:
        return False, str(e)

def convert_coordinates(
    decimal_degrees: float,
    coordinate_type: str
) -> Dict[str, Union[int, float]]:
    """
    Convert decimal degrees to degrees, minutes, seconds format.

    Args:
        decimal_degrees: Coordinate in decimal degrees
        coordinate_type: Either 'latitude' or 'longitude'

    Returns:
        Dict[str, Union[int, float]]: Dictionary containing degrees, minutes, and seconds
    
    Raises:
        ValueError: If coordinate_type is invalid
    """
    if coordinate_type not in ['latitude', 'longitude']:
        raise ValueError("coordinate_type must be 'latitude' or 'longitude'")
    
    degrees, minutes, seconds = decimal_degrees_to_dms(decimal_degrees)
    
    return {
        'degrees': degrees,
        'minutes': minutes,
        'seconds': seconds
    }

def get_supported_sentences() -> List[str]:
    """Return list of supported NMEA sentence types."""
    return ['GNGGA', 'GNVTG']

def format_nmea_data(
    data: Dict[str, Any],
    include_raw: bool = False
) -> Dict[str, Any]:
    """
    Format parsed NMEA data for output.

    Args:
        data: Dictionary containing parsed NMEA data
        include_raw: Whether to include raw NMEA sentences

    Returns:
        Dict[str, Any]: Formatted data dictionary
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    formatted = {}
    
    # Copy basic fields
    basic_fields = ['latitude', 'longitude', 'speed_kmh', 'bearing']
    for field in basic_fields:
        if field in data:
            formatted[field] = data[field]
    
    # Format date/time if present
    if all(key in data for key in ['date', 'time']):
        formatted['timestamp'] = format_gps_datetime(data['date'], data['time'])
    
    # Add raw data if requested
    if include_raw and 'raw' in data:
        formatted['raw'] = data['raw']
    
    return formatted

# Define public API
__all__ = [
    # Exceptions
    'GPSConnectionError',
    'DatabaseConnectionError',
    'NMEAParseError',
    
    # Data Classes
    'GPSCoordinate',
    'GPSData',
    
    # Classes
    'DatabaseManager',
    'NMEAParser',
    
    # Validation Functions
    'is_valid_latitude',
    'is_valid_longitude',
    'validate_coordinates',
    
    # Conversion Functions
    'knots_to_kmh',
    'decimal_degrees_to_dms',
    'convert_coordinates',
    'utc_to_timezone',
    'format_gps_datetime',
    
    # NMEA Functions
    'get_supported_sentences',
    'format_nmea_data',
    
    # Helper Functions
    'dataclass_to_dict',
    
    # Logging
    'setup_logging'
]

# Package metadata
__version__ = '0.2.0'