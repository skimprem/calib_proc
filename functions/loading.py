import numpy as np
import pandas as pd
from functions.globals import REL_HEADER
from functions.processing import shift_to_value, shift_to_ste

def load_relative(files):
    '''
    Load files
    '''
    readings = pd.DataFrame()
    for _file in files:
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
    Load absolute readings from Excel file
    '''

    absolute = pd.read_excel(_file, engine='openpyxl')
    absolute['redu'] = absolute.apply(
        lambda x: shift_to_value(x['a'], x['b'], x['h_eff'], reduce_height), axis=1)
    absolute['gravity_cg6'] = absolute.apply(
        lambda x: x['gravity_eff'] + shift_to_value(x['a'], x['b'], x['h_eff'], reduce_height), axis=1)
    absolute['ste_cg6'] = absolute.apply(lambda x: shift_to_ste(x['ua'], x['ub'], x['covab'], x['h_eff'], reduce_height), axis=1)
    absolute['diff'] = absolute['gravity_cg6'] - absolute['gravity_cg6'].iloc[0]
    absolute['ste_diff'] = np.sqrt(absolute['ste_cg6']**2 + absolute['ste_cg6'].iloc[0]**2)

    absolute.to_excel('absolute_cg6.xlsx', index=False)

    return absolute