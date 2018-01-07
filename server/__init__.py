"""
  Grow-Hub Sensor Server

"""
__author__ = "Jeremy Nelson, Timothy Semple"


import datetime
import os
from flask import Flask, render_template

app = Flask(__name__)
PROJECT_ROOT = os.path.split(os.path.abspath(__file__))[0]

@app.route("/")
def hub():
    return render_template('hub.html', 
	now=datetime.datetime.utcnow())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=13691, debug=True)
