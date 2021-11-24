import streamlit as st
import datetime
import pandas as pd
from preprocessing import clean_packages,clean_routes
from plotly_chart import route_chart,routes_per_day

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

packages_cleaned = clean_packages(packages,pricing)
routes_cleaned = clean_routes(routes)

# st.image("https://www.transformative-mobility.org/assets/site/events/COP26.PNG")
st.sidebar.image("https://images.caradisiac.com/logos/3/9/2/9/263929/S7-camions-la-fin-du-diesel-des-2040-187102.jpg")

#----------------------------------------------------------------------------------------------------------------------
# SIDEBAR
#----------------------------------------------------------------------------------------------------------------------


#st.sidebar.image("./img/logo_cop2.png",width = 150)
st.sidebar.write("""
# LPD Dashboard
""")

date = st.sidebar.selectbox("Choisissez votre jour:",routes_cleaned['route_date'].unique())

col1sb, col2sb, col3sb = st.sidebar.columns(3)
lever1 = col1sb.select_slider("Levier 1",['Off','On'], key=1, format_func=lambda x: 'On' if x=='On' else '')
lever2 = col2sb.select_slider("Levier 2",['Off','On'], key=2, format_func=lambda x: 'On' if x=='On' else '')
lever3 = col3sb.select_slider("Levier 3",['Off','On'], key=3, format_func=lambda x: 'On' if x=='On' else '')

#lever1 = st.sidebar.select_slider("Levier 1",['On','Off'])
#lever2 = st.sidebar.select_slider("Levier 1",['On','Off'])
#lever3 = st.sidebar.select_slider("Levier 3",['On','Off'])

st.sidebar.write("""##### Sommaire
1. [KPIs](#kpis)
2. [Bilan Carbone](#detail-du-bilan-carbone)
3. [Routes](#routes)
""")


# st.sidebar.write("""
# ## Author
# Work done by [Théo Alves Da Costa](https://www.linkedin.com/in/th%C3%A9o-alves-da-costa-09397a82/).
# Head of AI for Sustainability at [Ekimetrics](https://ekimetrics.com/) & Co-Lead for the NGO [Data For Good](https://dataforgood.fr/).
# I am present at the COP26 from the 4th to the 12th, if you want to meet in person. 
# - Code for the platform is open sourced on [Github](https://github.com/TheoLvs/cop26radar)
# - Contact by mail [here](mailto:theo.alvesdacosta@ekimetrics.com)
# ## Methodology
# For developers - analysis are done on Twitter data using Python, Flashtext, Hugging Face pretrained Transformers models from Cardiff University, BERTopic, langdetect, VADER.
# *Work in progress - Detailed methodology article and open source code soon available* 
# ## AI Carbon Footprint
# Artificial intelligence can consume a lot of energy, so special attention was paid to reduce the carbon footprint of the analyses: no cloud platform was used - performed on a simple laptop, the computing is done asynchronously to avoid multiplying requests and live calculations.
# Moreover, the carbon footprint was measured with the [CodeCarbon](https://github.com/mlco2/codecarbon) tool developed by the MILA University.
# """)


#----------------------------------------------------------------------------------------------------------------------
# USAGE
#----------------------------------------------------------------------------------------------------------------------

st.write("## KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Bilan Carbone", "14 ktCO2e", "-8%")
col2.metric("# de packets", "4 200", "+3%")
col3.metric("# de routes", "42", "-2%")

st.write("## Detail du bilan carbone")
st.info('WIP')

st.write("## Routes")
#st.plotly_chart(route_chart(orders,cities))
st.plotly_chart(routes_per_day(routes_cleaned,date,cities), use_container_width=True)

#st.write("*For now analyses are done live every day, a summarization of all analyses will be done at the end of the conference*")

#st.write("## Highlights")

