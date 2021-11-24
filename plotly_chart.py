import pandas as pd
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import geopandas as gpd
from preprocessing import clean_packages,clean_routes
import ssl
from helpers import *

ssl._create_default_https_context = ssl._create_unverified_context

def route_chart(orders,cities):
    with urlopen('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson') as response:
        french_counties = json.load(response)
        geo_data = pd.DataFrame(gpd.GeoDataFrame(french_counties['features'])['properties'].tolist())
        geo_data['value']= 1

    pck_volume_per_city = orders.groupby('delivery_location').aggregate({'package_volume':'sum'}).sort_values('package_volume',ascending=False)
    pck_volume_per_city = pd.merge(cities,pck_volume_per_city, left_on='city', right_index=True)

    pck_volume_per_city['text'] = pck_volume_per_city['city'] + ', ' + 'Package_Volume: ' + round(pck_volume_per_city['package_volume']).astype(str)

    trace0 = go.Choropleth(
        locations=geo_data['code'],
        geojson=french_counties,
        autocolorscale=False,
        z=geo_data['value'],
        featureidkey='properties.code', 
        showscale=False,
        marker_line_color='black',
        colorscale=[[0, "rgb(255,255,255)"],
                    [1, "rgb(240,240,240)"]])

    trace1 = data=go.Scattergeo(
            lon = pck_volume_per_city['lng'],
            lat = pck_volume_per_city['lat'],
            mode = 'markers',
            geojson= french_counties,
            text = pck_volume_per_city['text'],
            marker_color = pck_volume_per_city['package_volume'],
            marker = dict(
                size = 8,
                opacity = 0.8,
                reversescale = False,
                autocolorscale = False,
                symbol = 'square',
                line = dict(width=1,
                            color='rgba(102, 102, 102)'),
                colorscale = 'Reds',
                cmin = 150,
                color = pck_volume_per_city['package_volume'],
                cmax = pck_volume_per_city['package_volume'].max(),
                colorbar_title="Package Volume delivered<br>"),)

    fig = go.Figure(data=[trace0,
                        trace1,
                        ])

    fig.update_geos(fitbounds="locations", 
                    visible=False,
                    showlakes=True,
                    oceancolor='rgba(0,0,0,0)',
                    landcolor = 'rgba(0,0,0,0)',
                    bgcolor= 'rgba(0,0,0,0)')

    fig.update_layout(
            title = 'Most delivered city in France by LPD',
            geo_scope='europe',
            margin=dict(l=10, r=10, t=45, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

    return fig

def routes_per_day(routes_cleaned,random_date,cities):
    with urlopen('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson') as response:
        french_counties = json.load(response)
        geo_data = pd.DataFrame(gpd.GeoDataFrame(french_counties['features'])['properties'].tolist())
        geo_data['value']= 1

    used_tracks = []
    for i in range(len(routes_cleaned)):
        for j in range(len(routes_cleaned.stops[i])-1):
            used_tracks += [[routes_cleaned.stops[i][j] + ' - ' + routes_cleaned.stops[i][j+1],
                            routes_cleaned.stops[i][j],
                            routes_cleaned.stops[i][j+1],
                            routes_cleaned.route_date[i],
                            routes_cleaned.from_warehouse[i]]]
    used_tracks = (pd.DataFrame(used_tracks,columns=['routes','start','stop','date','from_warehouse']))

    routes_used_per_day = (used_tracks
                       .groupby(['routes','date','start','stop','from_warehouse'])
                       .agg({'routes':'count'})
                       .rename(columns={'routes':'nb_routes'})
                       .sort_values("nb_routes"))

    routes_used_per_day = pd.merge(routes_used_per_day.reset_index(), cities[['city','lat','lng']], 
                        left_on='start',right_on='city')

    routes_used_per_day = (routes_used_per_day
                .rename(columns={'lat':'lat_start','lng':'lng_start'})
                .drop(columns=['city']))

    routes_used_per_day = pd.merge(routes_used_per_day, cities[['city','lat','lng']], 
                        left_on='stop',right_on='city')

    routes_used_per_day = (routes_used_per_day
                .rename(columns={'lat':'lat_stop','lng':'lng_stop'})
                .drop(columns=['city']))

    routes_used_per_day_1 = routes_used_per_day[routes_used_per_day['date']==random_date].reset_index()

    trace0 = go.Choropleth(
        locations=geo_data['code'],
        geojson=french_counties,
        autocolorscale=False,
        z=geo_data['value'],
        featureidkey='properties.code', 
        showscale=False,
        showlegend=False,
        marker_line_color='grey',
        colorscale=[[0, "rgb(255,255,255)"],
                    [1, "rgb(240,240,240)"]])

    fig = go.Figure(data=[trace0])

    for i in range(len(routes_used_per_day_1)):
        fig.add_trace(go.Scattergeo(
                            lat = [routes_used_per_day_1.lat_start[i],routes_used_per_day_1.lat_stop[i]],
                            lon = [routes_used_per_day_1.lng_start[i],routes_used_per_day_1.lng_stop[i]],
                            mode = 'lines',
                            line = dict(color=color_per_reseau(routes_used_per_day_1.from_warehouse[i])), 
                            showlegend=False
                            ))

    fig.update_geos(fitbounds="locations", 
                    visible=False,
                    landcolor = "rgb(240, 240, 240)",
                    bgcolor= 'rgba(0,0,0,0)')

    fig.update_layout(
            title = f'Routes on the {random_date}',
            geo_scope='europe',
            margin=dict(l=10, r=10, t=45, b=20),
        )
    return fig
