import pytz
import logging
import mysql.connector

def is_valid_latitude(lat):
    """Validate if a given value is a valid latitude."""
    return -90 <= lat <= 90

def is_valid_longitude(lon):
    """Validate if a given value is a valid longitude."""
    return -180 <= lon <= 180

def knots_to_kmh(knots):
    """Convert speed from knots to kilometers per hour."""
    return knots * 1.852

def decimal_degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, and seconds (DMS)."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return d, m, s

def utc_to_timezone(utc_time, timezone='Asia/Dubai'):
    """Convert UTC datetime to a specified timezone."""
    local_tz = pytz.timezone(timezone)
    return utc_time.astimezone(local_tz)

def format_gps_datetime(gps_date, gps_time):
    """Format GPS date and time into ISO 8601."""
    return f"{gps_date}T{gps_time}"

def create_database_connection(host, user, password, database):
    """Establish and return a database connection."""
    try:
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(cursor, query, params):
    """Execute a database query and handle errors"""
    try:
        cursor.execute(query, params)
    except mysql.connector.Error as err:
        logging.error(f"Error executing query: {err}")

# Logging Utilities
def setup_logging(log_file='app.log'):
    """Configure logging for the application."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# NMEA Parsing Helpers
def split_nmea_sentence(sentence):
    """Split NMEA sentence into parts, ignoring checksum."""
    return sentence.split(',')[:-1]

# Error Handlers
def handle_serial_exception(e):
    """Handle serial connection exceptions."""
    print(f"Serial error: {e}")

def handle_database_exception(e):
    """Handle database-related exceptions."""
    logging.error(f"Databse operation error: {e}")