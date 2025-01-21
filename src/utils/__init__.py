# src/utils/__init__.py

# Expose commonly used functions for easy access
from .helpers import (
    setup_logging,
    execute_query,
    is_valid_latitude,
    is_valid_longitude,
    parse_gnvtg_sentence,
    parse_gngga_sentence,
    handle_serial_exception,
    handle_database_exception,
    create_database_connection
)

# What to expose when someone does 'from src.utils import *'
__all__ = [
    'setup_logging',
    'execute_query',
    'is_valid_latitude',
    'is_valid_longitude',
    'parse_gnvtg_sentence',
    'parse_gngga_sentence',
    'handle_serial_exception',
    'handle_database_exception',
    'create_database_connection'
]
