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

def proc(relative, absolute, model_type='WLS', drift_degree=2, calib_degree=1):
    logger.info('Starting processing with model_type=%s, drift_degree=%d, calib_degree=%d',
               model_type, drift_degree, calib_degree)
    
    '''
    Process relative and absolute readings to get calibration parameters
    '''

    relative = relative.merge(absolute[['Station']], how='inner', on='Station')

    reference = absolute.copy()
    reference.set_index('Station', inplace=True)
    reference.drop(index=reference.index[0], inplace=True)

    total_ties = pd.DataFrame()

    meters_calib_params = pd.DataFrame()

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
        )

        tie_names = fitted_ties_value.index
    
        ties = pd.DataFrame()
        
        ties['tie'] = fitted_ties_value[tie_names]
        ties['tie_ste'] = np.sqrt(fitted_ties_err[tie_names]**2 + total_uncert**2)
        ties['meter'] = meter_number

        ties['ref'] = reference['diff'] * 1e-3
        ties['ref_ste'] = reference['ste_diff'] * 1e-3

        ties['tie_coef'] = ties['ref'] / ties['tie']

        ties['tie_coef_ste'] = np.sqrt((ties['ref_ste']/ties['ref'])**2 + ((ties['ref']*ties['tie_ste'])/ties['tie']**2)**2)

        p, s = weighted_mean(ties['tie_coef'], ties['tie_coef_ste'])
        
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
                        'diff_count': stats.loc['diff', 'count'],
                        'diff_mean': stats.loc['diff', 'mean'],
                        'diff_ste': stats.loc['diff', 'std'],
                        'diff_min': stats.loc['diff', 'min'],
                        'diff_max': stats.loc['diff', 'max'],
                    },
                    index=[meter_number]
                )
            ], axis=1
        )

        total_ties = pd.concat(
            [
                total_ties,
                ties
            ],
            axis=0
        )

        meters_calib_params = pd.concat(
            [
                meters_calib_params,
                calib_params
            ],
            axis=0
        )
    
    return meters_calib_params, total_ties
