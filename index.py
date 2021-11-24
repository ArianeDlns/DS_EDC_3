import streamlit as st
import datetime
import pandas as pd
from preprocessing import clean_packages, clean_routes, adding_factors
from plotly_chart import route_chart, routes_per_day, chart_carbon
from helpers import add_days, pourcent
from cout_carbone import bilan_carbone_journee


@st.cache
def load_data(path):
    data = pd.read_csv(path)
    return data


cities = load_data("data/cities.csv")
factors = load_data("data/factors.csv")
orders = load_data("data/orders.csv")
packages = load_data("data/packages.csv")
pricing = load_data("data/pricing.csv")
routes = load_data("data/routes_v2.csv")
trucks = load_data("data/trucks.csv")
warehouses = load_data("data/warehouses.csv")

packages_cleaned = clean_packages(packages, pricing)
routes_cleaned = clean_routes(routes)
factors = adding_factors(factors)

# st.image("https://www.transformative-mobility.org/assets/site/events/COP26.PNG")
# st.sidebar.image("https://images.caradisiac.com/logos/3/9/2/9/263929/S7-camions-la-fin-du-diesel-des-2040-187102.jpg")
st.sidebar.image("http://lespopines.l.e.pic.centerblog.net/b6e74644.gif")

# ----------------------------------------------------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------------------------------------------------


#st.sidebar.image("./img/logo_cop2.png",width = 150)
st.sidebar.write("""
# LPD Dashboard
""")

date = st.sidebar.selectbox(
    "Choisissez votre jour:", routes_cleaned['route_date'].unique()[::-1])
warehouse = st.sidebar.multiselect("Choisissez vos entrepôts:", routes_cleaned['from_warehouse'].unique(
), default=routes_cleaned['from_warehouse'].unique())

col1sb, col2sb, col3sb = st.sidebar.columns(3)
lever1 = col1sb.select_slider(
    "🚦", ['Off', 'On'], key=1, format_func=lambda x: 'On' if x == 'On' else '')
lever2 = col2sb.select_slider(
    "🚚", ['Off', 'On'], key=2, format_func=lambda x: 'On' if x == 'On' else '')
lever3 = col3sb.select_slider(
    "🔋", ['Off', 'On'], key=3, format_func=lambda x: 'On' if x == 'On' else '')

#lever1 = st.sidebar.select_slider("Levier 1",['On','Off'])
#lever2 = st.sidebar.select_slider("Levier 1",['On','Off'])
#lever3 = st.sidebar.select_slider("Levier 3",['On','Off'])


# Updating database
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


# ----------------------------------------------------------------------------------------------------------------------
# USAGE
# ----------------------------------------------------------------------------------------------------------------------
st.write("## KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Bilan Carbone", f"{int(bilan_carbone_filtered.valeur.sum()/1000)} tCO2e",
            f"{pourcent(bilan_carbone_filtered.valeur.sum(),bilan_carbone_filtered_d1.valeur.sum())} % day-to-day", delta_color="inverse")

col2.metric("# de camions", f"{len(trucks_filtered)}")
col3.metric("# de routes", len(routes_cleaned_filtered),
            f"{len(routes_cleaned_filtered) - len(routes_cleaned_filtered_d1)} day-to-day", delta_color="inverse")

"""
---
"""

col21, col22 = st.columns(2)
col21.write("## Bilan carbone")
col21.plotly_chart(chart_carbon(bilan_carbone_filtered),
                   use_container_width=True)

col22.write("## Routes")
col22.plotly_chart(routes_per_day(routes_cleaned[routes_cleaned['from_warehouse'].isin(
    warehouse)], date, cities), use_container_width=True)

#st.write("*For now analyses are done live every day, a summarization of all analyses will be done at the end of the conference*")

# st.write("## Highlights")
