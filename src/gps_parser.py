import pytz
import serial
import logging
import datetime
import threading
import configparser
import mysql.connector
import serial.tools.list_ports

from utils.helpers import (
    knots_to_kmh,
    setup_logging, 
    execute_query,
    is_valid_latitude,
    is_valid_longitude,
    parse_gnvtg_sentence, 
    parse_gngga_sentence, 
    decimal_degrees_to_dms,
    handle_serial_exception, 
    handle_database_exception,
    create_database_connection,
    )

class GPSParser:
    def __init__(self, config_file='config.ini'):
        # Setup logging for debugging and operational tracking
        setup_logging('gps_parser.log')

        # Initialize the config parser and read the configuration file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        try:
            # Fetch database configuration from the INI file, using fallbacks for robustness
            self.db_host = self.config.get('database', 'host', fallback='localhost')
            self.db_user = self.config.get('database', 'user', fallback='root')
            self.db_password = self.config.get('database', 'password', fallback='')
            self.db_name = self.config.get('database', 'name', fallback='gps_data')

            # Fetch serial port configuration, with default values if not specified
            self.baudrate = self.config.getint('serial', 'baudrate', fallback=9600)
            self.timeout = self.config.getint('serial', 'timeout', fallback=1)
        except configparser.Error as e:
            logging.error(f"Configuration error: {e}")
            raise

        # Initialize database and serial connections as None for later setup
        self.db_connection = None
        self.cursor = None
        self.serial_port = None

    def auto_select_serial_port(self):
        # Auto-detect the correct serial port based on known device descriptions
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "CP2102N USB to UART Bridge Controller" in port.description or \
               "Silicon Labs CP210x USB to UART Bridge" in port.description:
                return port.device
        logging.error("GPS serial port not found.")
        raise IOError("GPS serial port not found.")

    def connect_to_serial(self):
        # Establish a connection to the serial port
        try:
            port = self.auto_select_serial_port()
            self.serial_port = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
            logging.info(f"Connected to serial port: {port}")
        except Exception as e:
            logging.error(f"Serial connection error: {e}")
            raise

    def connect_to_database(self):
        try:
            # Establish a connection to the MySQL database
            self.db_connection = create_database_connection(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            if self.db_connection:
                self.cursor = self.db_connection.cursor()
                logging.info("Connected to database successfully.")
            else:
                logging.error("Failed to connect to the database.")
                raise ConnectionError("Database connection failed.")
        except mysql.connector.Error as err:
            handle_database_exception(err)
            raise

    def insert_into_database(self, latitude, longitude, gps_date, gps_time, speed, bearing, interval_type):
        # Validate latitude and longitude values
        if not (is_valid_latitude(latitude) and is_valid_longitude(longitude)):
            logging.error(f"Invalid coordinates: lat={latitude}, lon={longitude}")
            return
        
        # SQL query to insert data into table
        query = """
                INSERT INTO tbl_gps_data (latd, lond, gps_date, gps_time, speed, bearing, interval_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        
        params = (latitude, longitude, gps_date, gps_time, speed, bearing, interval_type)
        
        # Insert GPS data into the database
        try:
            execute_query(self.cursor, query, params)
            self.db_connection.commit()
            logging.info("Data inserted into database successfully.")
        except mysql.connector.Error as db_err:
            handle_database_exception(db_err)

    def gps_data_handler(self):
        # Handle incoming GPS data from the serial port
        combined_data = {}
        try:
            while True:
                # Read a line from the serial port
                current_line = self.serial_port.readline().decode('ascii', errors='replace').strip()

                # Parse GNGGA sentences for location and fix data
                if current_line.startswith('$GNGGA'):
                    parsed_gga_data = parse_gngga_sentence(current_line)
                    if parsed_gga_data:
                        combined_data.update(parsed_gga_data)

                # Parse GNVTG sentences for speed and direction data
                elif current_line.startswith('$GNVTG'):
                    parsed_vtg_data = parse_gnvtg_sentence(current_line)
                    if parsed_vtg_data:
                        combined_data.update(parsed_vtg_data)

                # Process and store the combined data when complete
                if 'latitude' in combined_data and 'speed_kmh' in combined_data:
                    logging.info(f"Combined GPS Data: {combined_data}")

                    interval_type = combined_data.get('fix_quality')

                    self.insert_into_database(
                        latitude=combined_data['latitude'],
                        longitude=combined_data['longitude'],
                        gps_date=combined_data['date'],
                        gps_time=combined_data['time'],
                        speed=combined_data['speed_kmh'],
                        bearing=combined_data.get('bearing', None),
                        interval_type=interval_type
                    )

                    # Reset combined data for the next GPS data set
                    combined_data = {}
        except Exception as e:
            logging.error(f"GPS data handling error: {e}")
    
    # Cleanup method to properly close connection
    def __def__(self):
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

if __name__ == "__main__":
    # Initialize and run the GPS parser
    gps_parser = GPSParser()
    try:
        gps_parser.connect_to_serial()
        gps_parser.connect_to_database()

        # Start the GPS data handler in a separate thread
        gps_thread = threading.Thread(target=gps_parser.gps_data_handler, daemon=True)
        gps_thread.start()
        gps_thread.join()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
