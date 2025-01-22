"""
GPS Data Parser Utilities
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides utility functions for GPS data processing and validation.

Available functions:
    - Coordinate validation
    - Time zone conversion
    - NMEA sentence parsing
    - Database operations
    - Serial communication helpers
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple

# Setup module logger
logger = logging.getLogger(__name__)

# Import all utility functions
from .helpers import (
    # Validation functions
    is_valid_latitude,
    is_valid_longitude,
    
    # Conversion functions
    knots_to_kmh,
    decimal_degrees_to_dms,
    utc_to_timezone,
    format_gps_datetime,
    
    # Parsing functions
    parse_gngga_sentence,
    parse_gnvtg_sentence,
    split_nmea_sentence,
    
    # Database functions
    create_database_connection,
    execute_query,
    
    # Error handlers
    handle_serial_exception,
    handle_database_exception,
    
    # Logging setup
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
        Tuple of (is_valid, error_message)
        error_message is None if coordinates are valid
    """
    if not is_valid_latitude(latitude):
        return False, f"Invalid latitude: {latitude}"
    if not is_valid_longitude(longitude):
        return False, f"Invalid longitude: {longitude}"
    return True, None

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
        Dictionary containing degrees, minutes, and seconds
    """
    # Validate input
    if coordinate_type not in ['latitude', 'longitude']:
        raise ValueError("coordinate_type must be 'latitude' or 'longitude'")
    
    # Convert using helper function
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
        Formatted data dictionary
    """
    formatted = {}
    
    # Copy basic fields
    basic_fields = ['latitude', 'longitude', 'speed_kmh', 'bearing']
    for field in basic_fields:
        if field in data:
            formatted[field] = data[field]
    
    # Format date/time if present
    if 'date' in data and 'time' in data:
        formatted['timestamp'] = format_gps_datetime(data['date'], data['time'])
    
    # Add raw data if requested
    if include_raw:
        formatted['raw'] = data.get('raw', {})
    
    return formatted

__all__ = [
    # Main utility functions
    'is_valid_latitude',
    'is_valid_longitude',
    'knots_to_kmh',
    'decimal_degrees_to_dms',
    'utc_to_timezone',
    'format_gps_datetime',
    
    # Parsing functions
    'parse_gngga_sentence',
    'parse_gnvtg_sentence',
    'split_nmea_sentence',
    
    # Database functions
    'create_database_connection',
    'execute_query',
    
    # Error handlers
    'handle_serial_exception',
    'handle_database_exception',
    
    # Additional utility functions
    'validate_coordinates',
    'convert_coordinates',
    'get_supported_sentences',
    'format_nmea_data',
    
    # Logging
    'setup_logging'
]

# Version of the utils package
__version__ = '0.1.0'
