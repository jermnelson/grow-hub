"""
  Grow-Hub Sensor Server

"""
__author__ = "Jeremy Nelson"
__author__ = "Timothy Semple"


import datetime
import os
from bottle import request, route, run, static_file
from bottle import jinja2_view as view
from bottle import jinja2_template as template

PROJECT_ROOT = os.path.split(os.path.abspath(__file__))[0]

@route('/assets/<type_of:path>/<filename:path>')
def send_asset(type_of,filename):
    local_path = os.path.join(PROJECT_ROOT,
                              "assets",
                              type_of,
                              filename)
    if os.path.exists(local_path):
        return static_file(filename,
                           root=os.path.join(PROJECT_ROOT,
                                             "assets",
                                              type_of))

@route("/")
def hub():
    return template('hub', now=datetime.datetime.utcnow())

run(host='0.0.0.0', port=8000)
