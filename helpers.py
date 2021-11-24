"""Utils."""

import pandas as pd
import random
from dateutil.relativedelta import relativedelta
from datetime import datetime
from math import radians, sin, cos, asin, acos, sqrt
import numpy as np


def process_remove_outliers_quartile(df: pd.DataFrame) -> pd.DataFrame:
    """Remove outliers outside 1.5 IQR"""
    filtered = df.copy()
    for column in df.columns:
        # Computing IQR
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        # Filtering Values between Q1-1.5IQR and Q3+1.5IQR
        filtered = filtered.query(
            f'(@Q1 - 1.5 * @IQR) <= {column} <= (@Q3 + 1.5 * @IQR) or ({column} != {column})')
    return filtered


def tri_2_arg(list):
    """Prend une liste de couple (a,b) et la trie selon les valeurs de b dans l'ordre croissant"""
    random.shuffle(list)
    return sorted(list, key=lambda x: x[1])


def color_per_reseau(warehouse):
    colors = {"Cergy": "rgb(42,56,86)", "Clermont-Ferrand": "rgb(199,59,71)",
              "Montauban": "rgb(89,112,115)", "Reims": "rgb(182,217,219)",
              "Avignon": "rgb(199,59,71)"}
    return colors[warehouse]


def add_days(date, days, dtype='datetime'):
    try:
        if dtype == 'str':
            return datetime.strftime(datetime.strptime(date, "%Y-%m-%d") + relativedelta(days=days), "%Y-%m-%d")
        else:
            return datetime.strptime(date, "%Y-%m-%d") + relativedelta(days=days)
    except TypeError:
        if dtype == 'str':
            return datetime.strftime(date + relativedelta(days=days), "%Y-%m-%d")
        else:
            return date + relativedelta(days=days)


def pourcent(x1, x2):
    return int((x1-x2)/x2 * 100)


def distance_Haversine(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return(c * r)

# function for calculating distance between two pins


def _distance_calculator(_df):

    _distance_result = np.zeros((len(_df), len(_df)))
    _df['latitude-longitude'] = '0'
    for i in range(len(_df)):
        _df['latitude-longitude'].iloc[i] = str(
            _df.latitude[i]) + ',' + str(_df.longitude[i])

    for i in range(len(_df)):
        for j in range(len(_df)):

            _res = distance_Haversine(
                _df['latitude'].iloc[i], _df['latitude'].iloc[j], _df['longitude'].iloc[i], _df['longitude'].iloc[j])

            # append distance to result list
            _distance_result[i][j] = _res

    return _distance_result
