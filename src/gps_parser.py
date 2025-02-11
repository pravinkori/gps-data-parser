import serial
import logging
import threading
import configparser
import mysql.connector
from queue import Queue
from pathlib import Path
from threading import Event
import serial.tools.list_ports
from dataclasses import dataclass
from typing import Dict, Any, Optional

from src.utils import (
    setup_logging,
    DatabaseManager,
    NMEAParser,
    GPSData,
    GPSCoordinate,
    GPSConnectionError,
    DatabaseConnectionError
)

@dataclass
class GPSConfig:
    """Configuration data structure for GPS Parser."""
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    baudrate: int
    timeout: int

class GPSParser:
    """
    GPSParser connects to a GPS device via serial port, parses incoming NMEA sentences,
    and stores processed data into a MySQL database.
    """
    def __init__(self, config_file: str = 'config/config.example.ini'):
        self.logger = logging.getLogger(__name__)
        self._stop_event = Event()
        self._data_queue = Queue(maxsize=1000)
        
        # Load configuration
        self.config = self._load_configuration(config_file)
        
        # Initialize connections
        self.db_manager: Optional[DatabaseManager] = None
        self.serial_port: Optional[serial.Serial] = None
        self.nmea_parser = NMEAParser()

    def _load_configuration(self, config_file: str) -> GPSConfig:
        """Load and validate configuration from file."""
        config = configparser.ConfigParser()
        
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        config.read(config_file)
        
        try:
            return GPSConfig(
                db_host=config.get('database', 'host', fallback='localhost'),
                db_user=config.get('database', 'user', fallback='root'),
                db_password=config.get('database', 'password', fallback=''),
                db_name=config.get('database', 'name', fallback='gps_data'),
                baudrate=config.getint('serial', 'baudrate', fallback=9600),
                timeout=config.getint('serial', 'timeout', fallback=1)
            )
        except configparser.Error as e:
            self.logger.error(f"Configuration error: {e}")
            raise

    def auto_select_serial_port(self) -> str:
        """Auto-detect the correct serial port based on known device descriptions."""
        KNOWN_DEVICES = [
            "CP2102N USB to UART Bridge Controller",
            "Silicon Labs CP210x USB to UART Bridge"
        ]
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if any(device in port.description for device in KNOWN_DEVICES):
                return port.device
                
        raise GPSConnectionError("GPS serial port not found")

    def connect_to_serial(self) -> None:
        """Establish a connection to the serial port."""
        try:
            port = self.auto_select_serial_port()
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout
            )
            self.logger.info(f"Connected to serial port: {port}")
        except Exception as e:
            self.logger.error(f"Serial connection error: {e}")
            raise GPSConnectionError(f"Failed to connect to serial port: {e}")

    def connect_to_database(self) -> None:
        """Establish connection to the MySQL database."""
        try:
            self.db_manager = DatabaseManager(
                host=self.config.db_host,
                user=self.config.db_user,
                password=self.config.db_password,
                database=self.config.db_name
            )
            self.logger.info("Connected to database successfully")
        except mysql.connector.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

    def insert_into_database(self, gps_data: GPSData) -> None:
        """Insert parsed GPS data into the database."""
        query = """
            INSERT INTO tbl_gps_data 
            (latd, lond, gps_date, gps_time, speed, bearing, interval_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            gps_data.coordinate.latitude,
            gps_data.coordinate.longitude,
            gps_data.date,
            gps_data.time,
            gps_data.speed_kmh,
            gps_data.bearing,
            gps_data.fix_quality
        )
        
        try:
            self.db_manager.execute_query(query, params)
            self.logger.debug("Data inserted successfully")
        except DatabaseConnectionError as e:
            self.logger.error(f"Failed to insert data: {e}")

    def process_nmea_data(self, line: str) -> None:
        """Process NMEA sentences and queue the data."""
        try:
            if line.startswith('$GNGGA'):
                data = self.nmea_parser.parse_gngga_sentence(line)
                if data:
                    self._data_queue.put(data)
            elif line.startswith('$GNVTG'):
                data = self.nmea_parser.parse_gnvtg_sentence(line)
                if data:
                    self._data_queue.put(data)
        except Exception as e:
            self.logger.error(f"Error processing NMEA data: {e}")

    def gps_data_handler(self) -> None:
        """Continuously read from the serial port and process data."""
        combined_data: Dict[str, Any] = {}
        
        while not self._stop_event.is_set():
            try:
                if not self.serial_port.is_open:
                    raise GPSConnectionError("Serial port closed unexpectedly")
                    
                line = self.serial_port.readline().decode('ascii', errors='replace').strip()
                if not line:
                    continue
                    
                self.process_nmea_data(line)
                
                # Process queued data
                while not self._data_queue.empty():
                    data = self._data_queue.get()
                    combined_data.update(data)
                    
                    if self._is_data_complete(combined_data):
                        gps_data = GPSData(
                            coordinate=GPSCoordinate(
                                combined_data['latitude'],
                                combined_data['longitude']
                            ),
                            date=combined_data['date'],
                            time=combined_data['time'],
                            num_satellites=combined_data.get('num_satellites', 0),
                            high_accuracy=combined_data.get('high_accuracy', False),
                            fix_quality=combined_data.get('fix_quality', 0),
                            speed_kmh=combined_data.get('speed_kmh'),
                            bearing=combined_data.get('bearing')
                        )
                        
                        self.insert_into_database(gps_data)
                        combined_data.clear()
                        
            except Exception as e:
                self.logger.error(f"Error in GPS data handler: {e}")
                if not self._stop_event.is_set():
                    self.logger.info("Attempting to reconnect...")
                    self.reconnect()

    @staticmethod
    def _is_data_complete(data: Dict[str, Any]) -> bool:
        """Check if we have all required GPS data fields."""
        required_fields = {'latitude', 'longitude', 'date', 'time', 'speed_kmh'}
        return all(field in data for field in required_fields)

    def reconnect(self) -> None:
        """Attempt to reconnect to serial port and database."""
        try:
            self.close()
            self.connect_to_serial()
            self.connect_to_database()
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")

    def start(self) -> None:
        """Start the GPS parser in a separate thread."""
        self.connect_to_serial()
        self.connect_to_database()
        
        self._stop_event.clear()
        self.gps_thread = threading.Thread(target=self.gps_data_handler)
        self.gps_thread.daemon = True
        self.gps_thread.start()

    def stop(self) -> None:
        """Stop the GPS parser gracefully."""
        self._stop_event.set()
        if hasattr(self, 'gps_thread'):
            self.gps_thread.join(timeout=5.0)
        self.close()

    def close(self) -> None:
        """Cleanup method to properly close connections and release resources."""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            if self.db_manager:
                self.db_manager = None
            self.logger.info("Cleaned up resources successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def main() -> None:
    """Initialize and run the GPS parser."""
    parser = GPSParser()
    
    try:
        parser.start()
        # Keep the main thread alive
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        parser.logger.info("Shutting down GPS parser...")
    except Exception as e:
        parser.logger.critical(f"Fatal error: {e}")
    finally:
        parser.stop()

if __name__ == "__main__":
    main()