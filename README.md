# README.md

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

---

# CONTRIBUTING.md

# Contributing to GPS Data Parser

Thank you for considering contributing to **GPS Data Parser**! We appreciate your time and effort. By participating in this project, you help make it better for everyone.

## How to Contribute

### Reporting Issues
If you encounter bugs or have feature requests, please open an issue:
1. Go to the [Issues](https://github.com/yourusername/gps-data-parser/issues) tab.
2. Click on `New Issue` and provide details about the problem or suggestion.

### Submitting Code Changes
1. **Fork the Repository**:
   - Click on the `Fork` button at the top of the repository.
   - Clone your fork locally:
     ```bash
     git clone https://github.com/yourusername/gps-data-parser.git
     cd gps-data-parser
     ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**:
   - Follow PEP 8 style guidelines.
   - Add or update tests for your changes.

4. **Test Your Changes**:
   Run the test suite:
   ```bash
   python -m unittest discover tests
   ```

5. **Commit Your Changes**:
   ```bash
   git add .
   git commit -m "Add a descriptive commit message"
   ```

6. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**:
   - Go to the original repository.
   - Click on `Pull Requests` and then `New Pull Request`.
   - Select your fork and branch, and submit your pull request.

### Coding Standards
- Follow Python's PEP 8 for coding style.
- Write clear, concise commit messages.
- Add inline comments to explain complex code.

### Community Guidelines
- Be respectful and inclusive.
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Need Help?
If you have questions, feel free to reach out by opening an issue or starting a discussion in the [Discussions](https://github.com/yourusername/gps-data-parser/discussions) tab.
