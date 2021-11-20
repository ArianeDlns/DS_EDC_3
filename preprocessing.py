import pandas as pd

def clean_packages(packages,pricing):
    """Clean the package dataframe based on the pricing df"""
    packages_cleaned = packages.copy()

    #On commence par corriger la valeur du package de volume buggé
    packages_cleaned.loc[packages_cleaned['package_id']=='aBCDNfWx5TAkxbTTmQJEE4','package_volume'] = 0.1138

    #On corrige tous les prix pour les accorder au pricing selon le volume - tient compte des missing values en price
    packages_cleaned['threshold'] = packages_cleaned.apply(lambda x: min(pricing.max_volume.values, key=lambda y:max(0,x.package_volume-y)) ,axis=1)

    packages_cleaned = pd.merge(packages_cleaned,pricing[['max_volume','pricing']], left_on='threshold', right_on='max_volume')
    packages_cleaned.loc[packages_cleaned['package_revenues']!=packages_cleaned['pricing'],'package_revenues'] = packages_cleaned['pricing']
    #On ne garde que les colonnes pertinentes
    packages_cleaned = packages_cleaned[packages.columns]
    return packages_cleaned

def clean_routes(routes):
    """Clean the routes dataframe"""
    routes_cleaned = routes.copy()
    routes_cleaned.stops = routes.apply(lambda x: x.stops.split(' > '), axis=1)
    routes_cleaned.orders = routes.apply(lambda x: x.orders.split(' > '), axis=1)
    #Filling with average speed for 0 distance
    routes_cleaned['total_distance']=routes_cleaned.apply(lambda x: x.duration*100 if x.total_distance == 0 else x.total_distance, axis=1)
    #Filling with average speed for over 120*duration distance
    routes_cleaned['total_distance'] = routes_cleaned.apply(lambda x: x.duration*100  if  x.total_distance > x.duration*120 else x.total_distance, axis=1 )
    return routes_cleaned