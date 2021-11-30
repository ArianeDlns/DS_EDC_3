from numpy import int32
import streamlit as st
import datetime
import pandas as pd
from utils.plotly_chart import route_chart, routes_per_day, chart_carbon, waterfall_CO2
from utils.preprocessing import clean_packages, clean_routes, adding_factors
from utils.cout_carbone import bilan_carbone_journee, levers_computing
from utils.helpers import add_days, pourcent


# ----------------------------------------------------------------------------------------------------------------------
# To run locally run: 'streamlit run index.py'
# ----------------------------------------------------------------------------------------------------------------------

@st.cache
def load_data(path):
    data = pd.read_csv(path)
    return data


@st.cache
def cleaning(packages, pricing, routes, factors):
    packages_cleaned = clean_packages(packages, pricing)
    routes_cleaned = clean_routes(routes)
    factors = adding_factors(factors)
    return packages_cleaned, routes_cleaned, factors


cities = load_data("data/cities.csv")
factors = load_data("data/factors.csv")
orders = load_data("data/orders.csv")
packages = load_data("data/packages.csv")
pricing = load_data("data/pricing.csv")
routes = load_data("data/routes_v2.csv")
trucks = load_data("data/trucks.csv")
warehouses = load_data("data/warehouses.csv")

packages_cleaned, routes_cleaned, factors = cleaning(
    packages, pricing, routes, factors)


# ----------------------------------------------------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------------------------------------------------

st.sidebar.image("http://lespopines.l.e.pic.centerblog.net/b6e74644.gif")
st.sidebar.write("""
# LPD Dashboard
""")

date = st.sidebar.selectbox(
    "Choisissez votre jour:", routes_cleaned['route_date'].unique()[::-1])
warehouse = st.sidebar.multiselect("Choisissez vos entrepôts:", routes_cleaned['from_warehouse'].unique(
), default=routes_cleaned['from_warehouse'].unique())

st.sidebar.write("""
## Leviers stratégiques
""")
col1sb, col2sb, col3sb = st.sidebar.columns(3)
lever1 = col1sb.select_slider(
    "🚦", ['Off', 'On'], key=1, format_func=lambda x: 'On' if x == 'On' else '')
lever2 = col2sb.select_slider(
    "🚚", ['Off', 'On'], key=2, format_func=lambda x: 'On' if x == 'On' else '')
lever3 = col3sb.select_slider(
    "🔋", ['Off', 'On'], key=3, format_func=lambda x: 'On' if x == 'On' else '')

levers = [lever1, lever2, lever3]

# ----------------------------------------------------------------------------------------------------------------------
# UPDATING DATA
# ----------------------------------------------------------------------------------------------------------------------

routes_cleaned_filtered = routes_cleaned[(routes_cleaned['route_date'] == date) & (
    routes_cleaned['from_warehouse'].isin(warehouse))]
trucks_filtered = trucks[trucks['truck_warehouse'].isin(warehouse)]
bilan_carbone_filtered = bilan_carbone_journee(
    routes_cleaned_filtered, factors, trucks_filtered)

date_d1 = add_days(date, -1, dtype='str')
routes_cleaned_filtered_d1 = routes_cleaned[(routes_cleaned['route_date'] == date_d1) & (
    routes_cleaned['from_warehouse'].isin(warehouse))]
bilan_carbone_filtered_d1 = bilan_carbone_journee(
    routes_cleaned_filtered_d1, factors, trucks_filtered)

routes_levers = routes_cleaned_filtered
trucks_levers = trucks_filtered
bilan_carbone_levers = bilan_carbone_filtered

# ----------------------------------------------------------------------------------------------------------------------
# USAGE
# ----------------------------------------------------------------------------------------------------------------------

if 'On' in levers:
    bilan_carbon_full = bilan_carbone_filtered.valeur.sum()/1000
    values = [bilan_carbon_full, -bilan_carbon_full*0.19,0,-bilan_carbon_full*0.06,0,-bilan_carbon_full*0.24,0]
    impact_lever1 = values[1] if lever1=='On' else 0
    impact_lever2 = values[3] if lever2=='On' else 0
    impact_lever3 = values[5] if lever3=='On' else 0
    full_values = [bilan_carbon_full, impact_lever1 ,0, impact_lever2 ,0, impact_lever3, 0]

    st.write("## Impact des leviers")
    st.metric('Gain Carbon sur la journée',
              f'{-int(impact_lever1+impact_lever2+impact_lever3)} tCO2e', f'{int32((impact_lever1+impact_lever2+impact_lever3)/bilan_carbon_full*100)} %', delta_color="inverse")
 
    col1l, col2l, col3l = st.columns(3)
    col1l.metric("🚦 Optimisation des routes", f"{-int(impact_lever1)} tCO2e",
                  delta_color="inverse")

    col2l.metric("🚚 Dimensionnement des camions",
                 f"{-int(impact_lever2)} tCO2e")
    col3l.metric("🔋 Flotte électrique", f"{-int(impact_lever3)} tCO2e",
                 delta_color="inverse")

    st.plotly_chart(waterfall_CO2(full_values))

"""
---
"""

st.write("## KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Bilan carbone", f"{int(bilan_carbone_filtered.valeur.sum()/1000)} tCO2e",
            f"{pourcent(bilan_carbone_filtered.valeur.sum(),bilan_carbone_filtered_d1.valeur.sum())} % day-to-day", delta_color="inverse")

col2.metric("# de camions", f"{len(trucks_filtered)}")
col3.metric("# de routes", len(routes_cleaned_filtered),
            f"{len(routes_cleaned_filtered) - len(routes_cleaned_filtered_d1)} day-to-day", delta_color="inverse")

"""
---
"""

if 'On' not in levers:
    col21, col22 = st.columns(2)
    col21.write("## Bilan carbone")
    col21.plotly_chart(chart_carbon(bilan_carbone_filtered),
                    use_container_width=True)

    col22.write("## Routes")
    col22.plotly_chart(routes_per_day(routes_cleaned[routes_cleaned['from_warehouse'].isin(
        warehouse)], date, cities), use_container_width=True)
