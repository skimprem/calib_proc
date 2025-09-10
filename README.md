# Calibration Processing

## Description

This package is designed for processing Scintrex CG-6 gravimeter data, calculating calibration parameters, and generating reports. It supports both relative and absolute measurements, automatic drift and calibration fitting.

## Features

- Load and process CG-6 data files
- Merge relative and absolute measurements
- Automatic drift and calibration fitting
- Calculation of parameters and their uncertainties
- Generation of summary tables and Excel reports

## Installation

```bash
pip install .
```

## Usage

### Command Line

```bash
calibration.py --relative data/relative/*.dat --absolute data/absolute.xlsx
```

### GUI Mode

If no arguments are provided, a dialog window will open for file selection.

## Requirements

- Python 3.8+
- pandas
- openpyxl
- tabulate
- statsmodels

## Project Structure

- `scripts/calibration.py` — main script for data processing
- `functions/` — module with loading, processing, and calculation functions
- `data/` — example data structure for processing

## Author

Roman Sermiagin  
roman.sermiagin@gmail.com

## License

MIT License
