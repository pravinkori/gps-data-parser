import os
import pytz
import logging
import datetime
import mysql.connector
import logging.handlers
from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, Union

# Custom Exceptions
class GPSConnectionError(Exception):
    """Exception raised for errors in establishing GPS connection."""
    pass

class DatabaseConnectionError(Exception):
    """Exception raised for errors in establishing database connection."""
    pass

class NMEAParseError(Exception):
    """Exception raised for errors in parsing NMEA sentences."""
    pass

# Data Classes for better type safety and cleaner code
@dataclass
class GPSCoordinate:
    """Represents a GPS coordinate with validation."""
    latitude: float
    longitude: float

    def __post_init__(self):
        if not is_valid_latitude(self.latitude):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not is_valid_longitude(self.longitude):
            raise ValueError(f"Invalid longitude: {self.longitude}")

@dataclass
class GPSData:
    """Represents parsed GPS data."""
    coordinate: GPSCoordinate
    date: datetime.date
    time: datetime.time
    num_satellites: int
    high_accuracy: bool
    fix_quality: int
    speed_kmh: Optional[float] = None
    bearing: Optional[float] = None

# Validation functions
def is_valid_latitude(lat: float) -> bool:
    """Validate if a given value is a valid latitude."""
    return isinstance(lat, (int, float, Decimal)) and -90 <= float(lat) <= 90

def is_valid_longitude(lon: float) -> bool:
    """Validate if a given value is a valid longitude."""
    return isinstance(lon, (int, float, Decimal)) and -180 <= float(lon) <= 180

# Conversion functions with better type hints
def knots_to_kmh(knots: float) -> float:
    """Convert speed from knots to kilometers per hour."""
    return float(knots) * 1.852

def decimal_degrees_to_dms(degrees: float) -> Tuple[int, int, float]:
    """
    Convert decimal degrees to degrees, minutes, and seconds (DMS).
    
    Returns:
        Tuple of (degrees, minutes, seconds)
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = round((degrees - d - m / 60) * 3600, 6)  # Round to 6 decimal places
    return d, m, s

def utc_to_timezone(utc_time: datetime.datetime, timezone: str = 'Asia/Kolkata') -> datetime.datetime:
    """
    Convert UTC datetime to a specified timezone.
    
    Args:
        utc_time: UTC datetime object
        timezone: Target timezone string
    
    Returns:
        Localized datetime object
    """
    if not utc_time.tzinfo:
        utc_time = pytz.utc.localize(utc_time)
    return utc_time.astimezone(pytz.timezone(timezone))

def format_gps_datetime(gps_date: Union[datetime.date, str], 
                       gps_time: Union[datetime.time, str]) -> str:
    """Format GPS date and time into ISO 8601."""
    if isinstance(gps_date, str) and isinstance(gps_time, str):
        return f"{gps_date}T{gps_time}"
    return f"{gps_date.isoformat()}T{gps_time.isoformat()}"

# Database functions with connection pooling
class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="gps_pool",
            pool_size=5,
            host=host,
            user=user,
            password=password,
            database=database
        )
    
    def execute_query(self, query: str, params: tuple = None) -> None:
        """Execute a database query with proper connection handling."""
        with self.pool.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                connection.commit()
            except mysql.connector.Error as err:
                connection.rollback()
                logging.error(f"Database error: {err}")
                raise DatabaseConnectionError(f"Query execution failed: {err}")
            finally:
                connection.close()

# Improved NMEA parsing with better error handling
class NMEAParser:
    """Handles parsing of NMEA sentences."""
    
    @staticmethod
    def parse_gngga_sentence(sentence: str) -> Optional[Dict[str, Any]]:
        """Parse GNGGA sentence with improved error handling and validation."""
        try:
            parts = sentence.strip().split(',')
            
            if not sentence.startswith("$GNGGA") or len(parts) < 15:
                raise NMEAParseError("Invalid GNGGA sentence format")
            
            fix_quality = int(parts[6]) if parts[6] else 0
            if fix_quality in [0, 6, 7, 8]:
                logging.warning(f"Invalid GPS fix quality: {fix_quality}")
                return None
            
            # Parse time
            utc_time = parts[1]
            if len(utc_time) < 6:
                raise NMEAParseError("Invalid time format")
                
            hours = int(utc_time[0:2])
            minutes = int(utc_time[2:4])
            seconds = float(utc_time[4:])
            
            gps_time = datetime.time(
                hours, 
                minutes, 
                int(seconds), 
                int((seconds - int(seconds)) * 1e6)
            )
            
            # Parse coordinates with better validation
            try:
                latitude = NMEAParser._parse_latitude(parts[2], parts[3])
                longitude = NMEAParser._parse_longitude(parts[4], parts[5])
            except ValueError as e:
                raise NMEAParseError(f"Coordinate parsing error: {e}")
            
            # Create GPS data object
            gps_data = GPSData(
                coordinate=GPSCoordinate(latitude, longitude),
                date=datetime.datetime.utcnow().date(),
                time=gps_time,
                num_satellites=int(parts[7]) if parts[7] else 0,
                high_accuracy=fix_quality in [4, 5],
                fix_quality=fix_quality
            )
            
            return dataclass_to_dict(gps_data)
            
        except (IndexError, ValueError, NMEAParseError) as e:
            logging.error(f"Error parsing GNGGA sentence: {e}")
            return None
    
    @staticmethod
    def _parse_latitude(raw_lat: str, direction: str) -> float:
        """Parse latitude from NMEA format."""
        if not raw_lat or not direction:
            raise ValueError("Missing latitude data")
            
        degrees = int(raw_lat[:2])
        minutes = float(raw_lat[2:])
        latitude = degrees + minutes / 60
        
        return -latitude if direction == 'S' else latitude
    
    @staticmethod
    def _parse_longitude(raw_lon: str, direction: str) -> float:
        """Parse longitude from NMEA format."""
        if not raw_lon or not direction:
            raise ValueError("Missing longitude data")
            
        degrees = int(raw_lon[:3])
        minutes = float(raw_lon[3:])
        longitude = degrees + minutes / 60
        
        return -longitude if direction == 'W' else longitude

# Helper function to convert dataclass to dict
def dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert a dataclass instance to a dictionary."""
    if hasattr(obj, '__dataclass_fields__'):
        return {
            field: dataclass_to_dict(getattr(obj, field))
            if hasattr(getattr(obj, field), '__dataclass_fields__')
            else getattr(obj, field)
            for field in obj.__dataclass_fields__
        }
    return obj

# Setup logging with rotation
def setup_logging(
    log_file: str = 'app.log',
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> None:
    """Configure logging with rotation and proper formatting."""
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # Prevent adding duplicate handlers
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)
    else:
        # Optionally replace existing handlers or update them
        root_logger.handlers = [handler]
