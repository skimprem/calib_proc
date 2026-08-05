import io
import re
import numpy as np
import pandas as pd
import logging
from functions.globals import REL_HEADER, CG5_SECTION_TITLES, CG5_COLUMNS, CG5_HEADER_KEY_MAP
from functions.processing import shift_to_value, shift_to_ste

logger = logging.getLogger('calib_proc.loading')

def _normalize_station(value):
    '''
    Normalize a station label so that CG-6 (e.g. "P05"), CG-5 (e.g.
    "1089.0000000") and Excel-derived (e.g. 1089, 1089.0, "1089") station
    identifiers all collapse to the same string when they refer to the same
    station, letting the drift/calibration merges match reliably regardless
    of instrument or file format.
    '''
    if pd.isna(value):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value).strip()
    if number.is_integer():
        return str(int(number))
    return str(value).strip()

def _detect_relative_format(_file):
    '''
    Peek at the leading lines of a relative-measurement file to determine
    whether it was produced by a Scintrex CG-6 or a Scintrex CG-5
    gravimeter, then rewind the file so callers can parse it from the top.
    '''
    _file.seek(0)
    fmt = None
    for _ in range(15):
        line = _file.readline()
        if not line:
            break
        content = line.strip().lstrip('/').strip().upper()
        if content.startswith('CG-6'):
            fmt = 'CG-6'
            break
        if content.startswith('CG-5'):
            fmt = 'CG-5'
            break
    _file.seek(0)

    if fmt is None:
        raise ValueError(f'Unable to detect Scintrex file format (CG-5/CG-6) for file: {_file.name}')

    return fmt

def _load_relative_cg6(_file):
    '''
    Parse a single Scintrex CG-6 relative-measurement file
    '''
    header = {}
    count = 0
    line = _file.readline()
    first_symbol = line[0]
    line = line[1:].strip()
    while first_symbol == '/':
        count += 1
        if not line in [
            'CG-6 Survey',
            'CG-6 Calibration',
            '',
            REL_HEADER
        ]:
            items = line.split(':')
            key = items[0]
            value = ':'.join(items[1:])
            header[key] = value.strip()

        line = _file.readline()
        first_symbol = line[0]
        line = line[1:].strip()

    data = pd.read_csv(
        _file.name,
        sep='\t',
        skiprows=count-1,
    )
    data.rename(columns={'/Station': 'Station'}, inplace=True)
    data['Station'] = data['Station'].apply(_normalize_station)

    for key, value in header.items():
        data[key] = value

    return data

def _is_cg5_column_header(content):
    '''
    The CG-5 column header row looks like:
    /------LINE-----STATION-----ALT.------GRAV.---SD.--TILTX...
    '''
    return bool(content) and content[0] == '-' and 'LINE' in content and 'STATION' in content

def _load_relative_cg5(_file):
    '''
    Parse a single Scintrex CG-5 relative-measurement file.

    CG-5 files interleave three kinds of lines: '/'-prefixed metadata
    (section titles, key/value pairs, and the dashed column header),
    'Line'-prefixed station markers inserted by the instrument, and the
    whitespace-delimited data rows themselves.
    '''
    header = {}
    columns = None

    for raw_line in _file:
        stripped = raw_line.strip()

        if not stripped:
            continue

        if stripped[0] == '/':
            content = stripped[1:].strip()
            if _is_cg5_column_header(content):
                columns = [
                    CG5_COLUMNS.get(token, token)
                    for token in re.split(r'-+', content) if token
                ]
                break
            if content not in CG5_SECTION_TITLES:
                key, _, value = content.partition(':')
                header[key.strip()] = value.strip()
            continue

        if stripped.startswith('Line'):
            continue

        raise ValueError(f'Unexpected content before CG-5 column header in file {_file.name}: {stripped!r}')

    if columns is None:
        raise ValueError(f'CG-5 column header not found in file: {_file.name}')

    data_lines = [
        stripped for raw_line in _file
        if (stripped := raw_line.strip()) and not stripped.startswith('Line')
    ]

    data = pd.read_csv(
        io.StringIO('\n'.join(data_lines)),
        sep=r'\s+',
        names=columns,
        engine='python',
        dtype={'Station': str, 'Line': str, 'Date': str, 'Time': str},
    )
    data['Station'] = data['Station'].apply(_normalize_station)

    for key, value in header.items():
        column = CG5_HEADER_KEY_MAP.get(key, key)
        if column not in data.columns:
            data[column] = value

    return data

def load_relative(files):
    '''
    Load relative-measurement files produced by either a Scintrex CG-6 or
    a Scintrex CG-5 gravimeter, auto-detecting the format of each file.
    '''
    logger.debug('Loading %d relative data files', len(files))
    readings = pd.DataFrame()
    for _file in files:
        logger.debug('Processing file: %s', _file.name)

        fmt = _detect_relative_format(_file)
        logger.debug('Detected %s format for file: %s', fmt, _file.name)

        if fmt == 'CG-6':
            data = _load_relative_cg6(_file)
        else:
            data = _load_relative_cg5(_file)

        readings = pd.concat(
            [
                readings,
                data
            ]
        )

    readings['Group'] = (readings['Station'] != readings['Station'].shift()).cumsum()
    readings['Date Time'] = readings.apply(lambda row: f"{row['Date']} {row['Time']}", axis=1)

    return readings.reset_index(drop=True)

def load_absolute(_file, reduce_height=0):

    '''
    Load absolute reference gravity and vertical gravity gradient from Excel file
    '''
    logger.debug('Loading reference data from: %s', _file)
    logger.debug('Reduce height parameter: %f', reduce_height)

    absolute = pd.read_excel(_file, engine='openpyxl')

    # Some source tables store effective height in centimeters.
    # Convert to meters when values are obviously not in meters.
    h_eff = absolute['h_eff'].astype(float)
    if h_eff.abs().median() > 10:
        logger.warning('Detected h_eff values likely in centimeters, converting to meters')
        absolute['h_eff'] = h_eff / 100.0

    absolute['gravity_reduce'] = absolute.apply(
        lambda x: x['gravity_eff'] + shift_to_value(x['a'], x['b'], x['h_eff'], reduce_height), axis=1)
    absolute['ste_reduce'] = absolute.apply(lambda x: shift_to_ste(x['ua'], x['ub'], x['covab'], x['h_eff'], reduce_height), axis=1)
    absolute['diff'] = absolute['gravity_reduce'] - absolute['gravity_reduce'].iloc[0]
    absolute['ste_diff'] = np.sqrt(absolute['ste_reduce']**2 + absolute['ste_reduce'].iloc[0]**2)

    return absolute