from flask import Flask, render_template, request, redirect 
import requests
import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
from pyproj import Transformer
import numpy as np


app = Flask(__name__) #constructor for flask webapp

url = "https://opensky-network.org/api/states/all?lamin=30.038&lomin=-125.974&lamax=52.214&lomax=-68.748"

#DATA FRAME CONVERSION
def wgs84_to_web_mercator(df, lon="longitude", lat="latitude"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df


def get_flights():
     """Use opensky network api to get flight data"""
     r = requests.get(url)
     data = r.json()
     df = pd.DataFrame(data['states']) #states is data I need # number after corresponds to state vector
     fdf = pd.DataFrame( {"icao24": df[0],
                         "callsign": df[1],
                         "ctry": df[2],
                         "longitude": df[5],
                         "latitude": df[6],
                         "velocity": df[9]
                         })
     location = pd.DataFrame({"longitude": df[5],
                         "latitude": df[6]})
     
     
     mercator = wgs84_to_web_mercator(fdf)
     print(mercator.head())
     return fdf, mercator

def flight_map():
     """Make a map"""

     df, loc_df = get_flights()

     flight_source = ColumnDataSource(data=loc_df)
     p = figure(x_range=(-15187814, -6458032), y_range=(2505715, 6567666),
               x_axis_type="mercator", y_axis_type="mercator", sizing_mode="scale_both", height=500)
     
     p.add_tile("CartoDB Positron", retina=True)

     p.scatter(x='x', y='y', size=8, color="indigo", source=flight_source)

     my_hover=HoverTool()
     my_hover.tooltips=[('Call Sign','@callsign'),('Origin Country','@ctry'),('Velocity(m/s)','@velocity')]
     p.add_tools(my_hover)


     return show(p)

flight_map()









@app.route("/")
def index():
     return render_template("index.html") # flight map file

#if __name__ == "__main__":
#     app.run(debug=True)