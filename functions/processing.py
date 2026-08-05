import numpy as np
import pandas as pd
import statsmodels.api as sm
import logging
from functions.globals import TOTAL_UNCERT as total_uncert
from functions.adjustment import drift_fitting, calibration_fitting, weighted_mean

logger = logging.getLogger('calib_proc.processing')


def shift_to_value(a, b, h1, h2):
    return a * (h2 - h1) + b * (h2**2 - h1**2)

def shift_to_ste(ua, ub, covab, h1, h2):
    return abs(h2 - h1) * np.sqrt(ua**2 + (h2 + h1)**2 * ub**2 + (h2 + h1) * covab)

def proc(relative, absolute, model_type='WLS', drift_degree=2, calib_degree=1, anchor_station=None):
    logger.info('Starting processing with model_type=%s, drift_degree=%d, calib_degree=%d',
               model_type, drift_degree, calib_degree)
    
    '''
    Process relative and absolute readings to get calibration parameters
    '''

    relative = relative.merge(absolute[['Station']], how='inner', on='Station')

    if relative.empty:
        raise ValueError('No common stations between relative and absolute data.')

    if anchor_station is None:
        anchor_station = relative['Station'].iloc[0]
    else:
        try:
            anchor_station = relative['Station'].dtype.type(anchor_station)
        except (TypeError, ValueError):
            pass

    relative_stations = set(relative['Station'])
    absolute_stations = set(absolute['Station'])

    if anchor_station not in relative_stations:
        raise ValueError(
            f'Anchor station "{anchor_station}" is missing in relative measurements.'
        )

    if anchor_station not in absolute_stations:
        raise ValueError(
            f'Anchor station "{anchor_station}" is missing in absolute reference file.'
        )

    logger.info('Using anchor station: %s', anchor_station)

    reference = absolute.copy()
    reference.set_index('Station', inplace=True)

    anchor_gravity = reference.at[anchor_station, 'gravity_reduce']
    anchor_ste = reference.at[anchor_station, 'ste_reduce']
    reference['diff_anchor'] = reference['gravity_reduce'] - anchor_gravity
    reference['ste_diff_anchor'] = np.sqrt(reference['ste_reduce']**2 + anchor_ste**2)
    reference.drop(index=anchor_station, inplace=True, errors='ignore')

    # total_ties = pd.DataFrame()
    total_ties = []

    # meters_calib_params = pd.DataFrame()
    meters_calib_params = []

    for meter, meter_grouped in relative.groupby('Instrument Serial Number'):

        meter_number = int(meter)
        calib_params = pd.DataFrame()

        idx = meter_grouped.index

        fitted_ties_value, fitted_ties_err, fitted, _ = drift_fitting(
            stations=meter_grouped['Station'],
            date_time=meter_grouped['Date Time'],
            gravity=meter_grouped['CorrGrav'],
            error=meter_grouped['StdErr'],
            degree=drift_degree,
            anchor_station=anchor_station,
        )

        tie_names = fitted_ties_value.index
    
        ties = pd.DataFrame()
        
        ties['tie'] = fitted_ties_value[tie_names]
        ties['tie_ste'] = np.sqrt(fitted_ties_err[tie_names]**2 + total_uncert**2)
        ties['meter'] = meter_number

        ties['ref'] = reference['diff_anchor'].reindex(tie_names) * 1e-3
        ties['ref_ste'] = reference['ste_diff_anchor'].reindex(tie_names) * 1e-3

        if ties[['tie', 'tie_ste', 'ref', 'ref_ste']].isna().any().any():
            missing_refs = ties[ties['ref'].isna()].index.tolist()
            raise ValueError(
                'Reference increments contain NaN values. '
                f'Check station coverage/order. Missing reference stations: {missing_refs}'
            )

        ties['tie_coef'] = ties['ref'] / ties['tie']

        ties['tie_coef_ste'] = np.sqrt((ties['ref_ste']/ties['ref'])**2 + ((ties['ref']*ties['tie_ste'])/ties['tie']**2)**2)

        # p, s = weighted_mean(ties['tie_coef'], ties['tie_coef_ste'])
        
        params, bse = calibration_fitting(
            ties=ties['tie'],
            ties_ste=ties['tie_ste'],
            refs=ties['ref'],
            refs_ste=ties['ref_ste'],
            degree=calib_degree,
            model_type=model_type
        )

        fit_tie = 0
        for deg in range(calib_degree):
            fit_tie += params[f'deg_{deg+1}'] * ties['tie'] ** (deg+1)

            calib_params = pd.concat(
                [
                    calib_params,
                    pd.DataFrame(
                        data={
                            f'calib_deg_{deg+1}': [params[f'deg_{deg+1}']],
                            f'calib_deg_{deg+1}_ste': [bse[f'deg_{deg+1}']]
                        },
                        index=[meter_number]
                    )
                ], axis=1
            )

        ties['fit_tie'] = fit_tie
        ties['diff'] = ties['ref'] - ties['fit_tie']

        stats = ties['diff'].describe().to_frame().T

        calib_params = pd.concat(
            [
                calib_params,
                pd.DataFrame(
                    data={
                        # 'meter': meter_number,
                        'diff_count': stats.loc['diff', 'count'],
                        'diff_mean': stats.loc['diff', 'mean'],
                        'diff_ste': stats.loc['diff', 'std'] / np.sqrt(stats.loc['diff', 'count']),
                        'diff_min': stats.loc['diff', 'min'],
                        'diff_max': stats.loc['diff', 'max'],
                    },
                    index=[meter_number]
                )
            ], axis=1
        )

        total_ties.append(ties)

        meters_calib_params.append(calib_params)
    
    return pd.concat(meters_calib_params), pd.concat(total_ties)
