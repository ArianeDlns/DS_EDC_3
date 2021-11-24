"""Module de chiffrage carbone"""
import pandas as pd

def bilan_carbone_route_fixe(route,factors):
    "calcul du bilan carbone pour une route"
    return factors.loc['CO2_fab'].value/(8*180)

def bilan_carbone(truck,factors):
    "calcul du bilan carbone pour un camion avec un amortissement de 6 mois sur 4 ans"
    return factors.loc['CO2_fab'].value/8 + factors.loc['CO2_t.km'].value*25*truck.total_distance*2 

def bilan_carbone_route_variable(route,factors):
    "calcul du bilan carbone pour une route"
    return factors.loc['CO2_t.km'].value*25*route.total_distance*2 

def bilan_carbone_journalier_route(route,factors):
    "calcul du bilan carbone journalier pour une route"
    carbon_amortissement = len(route['truck_id'].unique())*factors.loc['CO2_fab'].value/(8*180)
    carbon_route = factors.loc['CO2_t.km'].value*25*route.total_distance.sum()*2 
    return (carbon_route,carbon_amortissement)

def bilan_carbone_journee(route,factors,trucks): 
    "calcul du bilan carbone journalier pour une route"
    carbon_route,carbon_amortissement = bilan_carbone_journalier_route(route,factors)
    carbon_stockage = (len(trucks) - len(route['truck_id'].unique()))*factors.loc['CO2_fab'].value/(8*180)
    df = pd.DataFrame([carbon_route,carbon_stockage,carbon_amortissement], index=[['Utilisation des camions','Production des camions stockés','Production des camions utilisés']], columns=['valeur'])
    df = df.reset_index()
    return df
