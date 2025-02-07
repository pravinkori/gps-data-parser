import pytz
import logging
import datetime
import mysql.connector

# Custom Exception
class GPSConnectionError(Exception):
    """Exception raised for errors in establishing GPS connection."""
    pass

class DatabaseConnectionError(Exception):
    """Exception raised for errors in establishing database connection."""
    pass

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

# Parse the GNGGA sentence for GPS data
def parse_gngga_sentence(sentence):
    try:
        parts = sentence.split(',')

        # Check if the sentence is a valid GNGGA message
        if parts[0] != "$GNGGA":
            return None
        
        # Parse the GPS fix quality; ignore invalid or non-standard fixes
        fix_quality = int(parts[6])
        if fix_quality in [0, 6, 7, 8]:
            logging.warning("Invalid or non-standard GPS fix.")
            return None

        # Extract and parse UTC time from the sentence
        utc_time = parts[1]
        hours = int(utc_time[0:2])
        minutes = int(utc_time[2:4])
        seconds = float(utc_time[4:])
        gps_time = datetime.time(hours, minutes, int(seconds), int((seconds - int(seconds)) * 1e6))

        # Convert latitude from degrees and minutes to decimal degrees
        raw_latitude = parts[2]
        lat_degrees = int(raw_latitude[:2])
        lat_minutes = float(raw_latitude[2:])
        latitude = lat_degrees + lat_minutes / 60
        if parts[3] == 'S':
            latitude = -latitude

        # Convert longitude from degrees and minutes to decimal degrees
        raw_longitude = parts[4]
        lon_degrees = int(raw_longitude[:3])
        lon_minutes = float(raw_longitude[3:])
        longitude = lon_degrees + lon_minutes / 60
        if parts[5] == 'W':
            longitude = -longitude

        # Parse the number of satellites and timestamp
        num_satellites = int(parts[7])
        gps_date = datetime.datetime.utcnow().date()
        gps_datetime_utc = datetime.datetime.combine(gps_date, gps_time)
        gps_datetime_utc = pytz.utc.localize(gps_datetime_utc)

        # Convert the UTC time to Dubai timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        gps_datetime_ist = gps_datetime_utc.astimezone(ist_timezone)

        # Extract date and time in Dubai timezone
        gps_date_ist = gps_datetime_ist.date()
        gps_time_ist = gps_datetime_ist.time()

        # Determine if the fix is high-accuracy (RTK fix)
        high_accuracy = fix_quality in [4, 5]

        # Prepare the parsed GPS data
        return {
            "latitude": latitude,
            "longitude": longitude,
            "date": gps_date_ist.isoformat(),
            "time": gps_time_ist.isoformat(),
            "num_satellites": num_satellites,
            "high_accuracy": high_accuracy,
            "fix_quality": fix_quality
        }

    except (IndexError, ValueError) as e:
        logging.error(f"Error parsing GNGGA sentence: {e}")
        return None

# Parse the GNVTG sentence for GPS data
def parse_gnvtg_sentence(sentence):
    # Parse the GNVTG sentence for velocity and direction data
    try:
        parts = sentence.split(',')

        # Check if the sentence is a valid GNVTF message
        if parts[0] != "$GNVTG":
            return None

        # Extract bearing and speed in km/h
        bearing = float(parts[1]) if parts[1] else None
        speed_kmh = float(parts[7]) if parts[7] else None

        # Prepare the parsed velocity and bearing data
        return {
            "bearing": bearing,
            "speed_kmh": speed_kmh
        }

    except (IndexError, ValueError) as e:
        logging.error(f"Error parsing GNVTG sentence: {e}")
        return None
