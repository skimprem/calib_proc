import numpy as np
import pandas as pd
import logging
from functions.globals import REL_HEADER
from functions.processing import shift_to_value, shift_to_ste

logger = logging.getLogger('calib_proc.loading')

def load_relative(files):
    '''
    Load files
    '''
    logger.debug('Loading %d CG-6 data files', len(files))
    readings = pd.DataFrame()
    for _file in files:
        logger.debug('Processing file: %s', _file.name)
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

        for key, value in header.items():
            data[key] = value

        readings = pd.concat(
            [
                readings,
                data
            ]
        )

    readings.rename(columns={'/Station': 'Station'}, inplace=True)
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
    absolute['gravity_reduce'] = absolute.apply(
        lambda x: x['gravity_eff'] + shift_to_value(x['a'], x['b'], x['h_eff'], reduce_height), axis=1)
    absolute['ste_reduce'] = absolute.apply(lambda x: shift_to_ste(x['ua'], x['ub'], x['covab'], x['h_eff'], reduce_height), axis=1)
    absolute['diff'] = absolute['gravity_reduce'] - absolute['gravity_reduce'].iloc[0]
    absolute['ste_diff'] = np.sqrt(absolute['ste_reduce']**2 + absolute['ste_reduce'].iloc[0]**2)

    return absolute