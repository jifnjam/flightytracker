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
import logging
import os


app = Flask(__name__) #constructor for flask webapp

@app.route("/")
def index():
     return render_template("index.html") # flight map file

if __name__ == "__main__":
    app.run(debug=True)
