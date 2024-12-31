# GPS Data Parser

**GPS Data Parser** is a Python-based application designed to parse GPS data (NMEA sentences) from serial ports, process it, and store the data in a MySQL database. It includes robust features for handling GNGGA and GNVTG sentences, timezone conversions, and real-time data storage.

## Features
- Auto-detection of GPS serial ports.
- Parsing GNGGA and GNVTG NMEA sentences.
- Conversion of UTC time to local timezone (Asia/Dubai by default).
- Multi-threaded real-time GPS data processing.
- Storage of parsed data in MySQL database.

## Getting Started

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.8 or later
- MySQL Server
- Required Python packages (listed in `requirements.txt`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pravinkori/gps-data-parser.git
   cd gps-data-parser
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your settings:
   - Copy the example configuration file:
     ```bash
     cp config/config.example.ini config/config.ini
     ```
   - Edit `config/config.ini` to set your MySQL credentials and desired serial settings.

### Usage
Run the parser with the following command:
```bash
python src/gps_parser.py
```

### Testing
Run the test suite to ensure everything works correctly:
```bash
python -m unittest discover tests
```

## Contributing
We welcome contributions from the community! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to get started.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

