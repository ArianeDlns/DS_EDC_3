"""Utils."""

import pandas as pd
import random

def process_remove_outliers_quartile(df: pd.DataFrame) -> pd.DataFrame:
    """Remove outliers outside 1.5 IQR"""
    filtered = df.copy()
    for column in df.columns:
        # Computing IQR
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        # Filtering Values between Q1-1.5IQR and Q3+1.5IQR
        filtered = filtered.query(f'(@Q1 - 1.5 * @IQR) <= {column} <= (@Q3 + 1.5 * @IQR) or ({column} != {column})')
    return filtered

def tri_2_arg(list):
    """Prend une liste de couple (a,b) et la trie selon les valeurs de b dans l'ordre croissant"""
    random.shuffle(list)
    return sorted(list, key = lambda x: x[1])

