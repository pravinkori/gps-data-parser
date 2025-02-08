import pytest
import serial
import configparser
from src.gps_parser import GPSParser
from unittest.mock import patch, MagicMock
from src.utils.helpers import GPSConnectionError, DatabaseConnectionError

@patch('serial.tools.list_ports.comports')
def test_auto_select_serial_port(mock_comports):
    fake_port = MagicMock()
    fake_port.description = "CP2102N USB to UART Bridge Controller"
    fake_port.device = "/dev/ttyUSB0"
    mock_comports.return_value = [fake_port]
    
    parser = GPSParser(config_file='config/config.example.ini')
    port = parser.auto_select_serial_port()
    assert port == "/dev/ttyUSB0"

@patch('serial.tools.list_ports.comports')
def test_auto_select_serial_port_not_found(mock_comports):
    mock_comports.return_value = []
    parser = GPSParser(config_file='config/config.example.ini')
    with pytest.raises(Exception):
        parser.auto_select_serial_port()

@patch('serial.Serial')
@patch('serial.tools.list_ports.comports')
def test_connect_to_serial(mock_comports, mock_serial):
    fake_port = MagicMock()
    fake_port.description = "CP2102N USB to UART Bridge Controller"
    fake_port.device = "/dev/ttyUSB0"
    mock_comports.return_value = [fake_port]
    
    parser = GPSParser(config_file='config/config.example.ini')
    parser.connect_to_serial()
    mock_serial.assert_called_once_with(port="/dev/ttyUSB0", baudrate=parser.baudrate, timeout=parser.timeout)

@patch('src.gps_parser.create_database_connection')
def test_connect_to_database_success(mock_create_db):
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    mock_create_db.return_value = fake_conn
    
    parser = GPSParser(config_file='config/config.example.ini')
    parser.connect_to_database()
    assert parser.db_connection == fake_conn
    assert parser.cursor == fake_cursor

def test_insert_into_database_invalid_coordinates():
    parser = GPSParser(config_file='config/config.example.ini')
    parser.db_connection = MagicMock()
    parser.cursor = MagicMock()
    # Use invalid coordinates so that the insert should not occur.
    parser.insert_into_database(1000, 2000, "2024-01-01", "12:00:00", 50, 90, 1)
    parser.cursor.execute.assert_not_called()

def test_insert_into_database_valid_coordinates():
    parser = GPSParser(config_file='config/config.example.ini')
    parser.db_connection = MagicMock()
    parser.cursor = MagicMock()
    # Use valid coordinates
    parser.insert_into_database(45.0, 90.0, "2024-01-01", "12:00:00", 50, 90, 1)
    parser.cursor.execute.assert_called_once()

def test_close_resources():
    parser = GPSParser(config_file='config/config.example.ini')
    fake_cursor = MagicMock()
    fake_db_conn = MagicMock()
    fake_serial = MagicMock()
    fake_serial.is_open = True
    parser.cursor = fake_cursor
    parser.db_connection = fake_db_conn
    parser.serial_port = fake_serial
    parser.close()
    fake_cursor.close.assert_called_once()
    fake_db_conn.close.assert_called_once()
    fake_serial.close.assert_called_once()
