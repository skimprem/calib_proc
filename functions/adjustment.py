import numpy as np
import pandas as pd
import statsmodels.api as sm



def to_minutes_since_start(series):
    t0 = series.min()
    return (series - t0).dt.total_seconds() / 60

def drift_fitting(stations, date_time, gravity, error, degree=2, model_type='WLS'):

    times = to_minutes_since_start(pd.to_datetime(date_time))

    time_design = pd.DataFrame()
    for degree in range(1, degree + 1):
        time_design[f'd_{degree}'] = times ** degree

    endog = gravity
    weights = error**-2

    stations = pd.get_dummies(stations, dtype=float)
    tie_names = stations.columns[1:]

    exog = pd.concat(
        [
            stations.drop(stations.columns[0], axis=1),
            time_design,
            pd.DataFrame(np.ones_like(endog), index=endog.index, columns=['c']),
        ],
        axis=1
    )

    match model_type:
        case 'WLS':
            model = sm.WLS(endog=endog, exog=exog, weights=weights)
        case 'OLS':
            model = sm.OLS(endog=endog, exog=exog)
        case 'RLM':
            model = sm.RLM(endog=endog, exog=exog)
        case _:
            raise ValueError(f"Unknown model type: {model_type}")

    fit = model.fit()

    fitted = fit.fittedvalues
    residuals = fit.resid
    params = fit.params
    bse = fit.bse

    return params[tie_names], bse[tie_names], fitted, residuals

def calibration_fitting(ties, ties_ste, refs, refs_ste, degree=None, model_type='WLS'):

    n_points = len(ties)

    if degree is None:
        degree = n_points - 1

    endog = refs
    design = pd.DataFrame()
    for deg in reversed(range(1, degree + 1)):
        design[f'deg_{deg}'] = ties ** deg

    match model_type:
        case 'WLS':
            weights = refs_ste**-2
            model = sm.WLS(endog=endog, exog=design, weights=weights)
        case 'OLS':
            model = sm.OLS(endog=endog, exog=design)
        case 'RLM':
            model = sm.RLM(endog=endog, exog=design)
        case _:
            raise ValueError(f"Unknown model type: {model_type}")

    fit = model.fit()
    params = fit.params
    bse = fit.bse

    return params, bse

def weighted_mean(values, ste):
    """
    Расчёт средневзвешенного значения и его стандартной ошибки.

    Параметры:
    - values: массив значений
    - ste: массив стандартных ошибок (той же длины)

    Возвращает:
    - mean: средневзвешенное значение
    - std_err: стандартная ошибка среднего
    """

    endog=np.array(values)

    weights = 1 / np.array(ste)**2

    model = sm.WLS(endog=endog, exog=np.ones_like(endog), weights=weights)

    fit = model.fit()

    mean = fit.params[0]
    std_err = fit.bse[0]

    return mean, std_err
