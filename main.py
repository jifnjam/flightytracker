from flask import Flask, render_template


app = Flask(__name__) #constructor for flask webapp

@app.route("/")
def index():
     return render_template("index.html") # flight map file

if __name__ == "__main__":
    app.run(debug=True)
