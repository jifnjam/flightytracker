import requests
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, ImageURL
import numpy as np
from bokeh.io import curdoc



url = "https://otmmint:CFuMr9M84mXigLz@opensky-network.org/api/states/all?lamin=30.038&lomin=-125.974&lamax=52.214&lomax=-68.748"


#DATA FRAME CONVERSION
def wgs84_to_web_mercator(df, lon="longitude", lat="latitude"):
    """Converts latitude and longitude coordinates into mercator"""
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df


def get_flights():
     """Use opensky network api to get flight data"""
     r = requests.get(url)
     data = r.json()
     df = pd.DataFrame(data['states']) #states is the data needed | number after corresponds to state vector
     fdf = pd.DataFrame( {"icao24": df[0],
                         "callsign": df[1],
                         "ctry": df[2],
                         "longitude": df[5],
                         "latitude": df[6],
                         "velocity": df[9]
                         })
     location = pd.DataFrame({"longitude": df[5],
                         "latitude": df[6]})
     
     
     mercator = wgs84_to_web_mercator(fdf) #turn flight dataframe into one with mercator coordinates
     return mercator

def flight_map(doc):
     """Make a map from OpenSky Network REST API"""

     loc_df = get_flights() # get data

     flight_source = ColumnDataSource(data=loc_df)
     p = figure(x_range=(-15187814, -6458032), y_range=(2505715, 6567666),
               x_axis_type="mercator", y_axis_type="mercator", sizing_mode="scale_both", 
               tools="wheel_zoom, reset, pan, zoom_in, zoom_out")

     # map tile
     p.add_tile("Esri World Imagery", retina=True)

     # map style
     p.scatter(x='x', y='y', size=8, color="aquamarine", source=flight_source, marker="asterisk")
     p.xaxis.visible=False
     p.xgrid.visible = False
     p.yaxis.visible = False
     p.ygrid.visible = False
     # interactivity
     my_hover=HoverTool()
     my_hover.tooltips=[('Call Sign','@callsign'),('ICAO 24', '@icao24'),('Origin Country','@ctry'),('Velocity(m/s)','@velocity')]
     p.add_tools(my_hover)
     p.toolbar.autohide = True

     def update():
          """Update flight data to ensure realtime status"""
          new_data = get_flights()
          flight_source.data = new_data.to_dict(orient="list")

     doc.add_root(p) # add map to doc      
     doc.add_periodic_callback(update, 5000) #update every 5 seconds
     doc.title = "Flight Tracker App"


bokeh_doc = curdoc()
flight_map(bokeh_doc) #initiate map of active flights