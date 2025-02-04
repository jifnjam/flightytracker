from flask import Flask, render_template, request, redirect 
import requests
import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.embed import file_html


app = Flask(__name__) #constructor for flask webapp

url = "https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226"
r = requests.get(url)
data = r.json()
data["states"][0] #states is data I need # number after corresponds to state vector






@app.route("/")
def index():
     return render_template("index.html") # flight map file

#if __name__ == "__main__":
#     app.run(debug=True)