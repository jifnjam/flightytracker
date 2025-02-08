from flask import Flask, render_template, request, redirect 
import requests
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.embed import file_html, server_document
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
import numpy as np
from bokeh.io import curdoc
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from tornado.ioloop import IOLoop
import threading
from waitress import serve
import os


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
     #print(mercator.head())
     return mercator

def flight_map(doc):
     """Make a map"""

     #def update():
     loc_df = get_flights()

     flight_source = ColumnDataSource(data=loc_df)
     p = figure(x_range=(-15187814, -6458032), y_range=(2505715, 6567666),
               x_axis_type="mercator", y_axis_type="mercator", sizing_mode="scale_both", height=500)

     p.add_tile("CartoDB Positron", retina=True)

     p.scatter(x='x', y='y', size=8, color="indigo", source=flight_source)

     my_hover=HoverTool()
     my_hover.tooltips=[('Call Sign','@callsign'),('Origin Country','@ctry'),('Velocity(m/s)','@velocity')]
     p.add_tools(my_hover)
     
     def update():
          new_data = get_flights()
          flight_source.data = new_data.to_dict(orient="list")

     doc.add_root(p)       
     doc.add_periodic_callback(update, 5000)


     #return p, flight_source 
     #return file_html(p, CDN, "Flight Map")

bokeh_app = Application(FunctionHandler(flight_map))

# Run Bokeh server in background
def bk_worker():
    dport = int(os.environ.get("PORT", 5006))

    ioloop = IOLoop.current()
    #server = Server({'/bkapp': bokeh_app}, io_loop=ioloop, allow_websocket_origin=["flightytracker.onrender.com"], port=dport, address="0.0.0.0", proxy_address="https://flightytracker.onrender.com")
    #server = Server({'/bkapp': bokeh_app}, io_loop=ioloop, allow_websocket_origin=["*"], port=5006) 
    server = Server({'/bkapp': bokeh_app}, io_loop=ioloop, allow_websocket_origin=["flightytracker.onrender.com"], port=dport, address="0.0.0.0")
    server.start()
    ioloop.start()

# Ensure the Bokeh server starts before Flask
thread = threading.Thread(target=bk_worker, daemon=True)
thread.start()

@app.route("/")
def index():
     return render_template("index.html") # flight map file

@app.route("/bkapp")
def update_map():
    """Return only the updated Bokeh map for HTMX to fetch."""
    #script = server_document('http://localhost:5006/bkapp')  # Embed the Bokeh app
    #script = server_document('https://flightytracker.onrender.com/bkapp')
    script = server_document(f'https://{os.environ.get("RENDER_EXTERNAL_URL")}/bkapp')
    return render_template("bokeh-map.html", script=script)


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000, debug=True)
    #app.run()
    #pass
    serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    #serve(app, host='0.0.0.0', port=5000)