"""
  Grow-Hub Sensor Server

"""
__author__ = "Jeremy Nelson, Timothy Semple"


import datetime
import os
import sqlite3

import rdflib

from collections import OrderedDict
from flask import Flask, flash, render_template, request, redirect
from flask import url_for

app = Flask(__name__)
app.secret_key = 'GROWHUB'

PROJECT_ROOT = os.path.split(os.path.dirname(os.path.abspath((__file__))))[0]
KNOWLEGE_GRAPH = rdflib.Graph()
KNOWLEGE_GRAPH.parse(os.path.join(PROJECT_ROOT, "data/current.ttl"),
                     format='turtle')
LOG_PATH = os.path.join(PROJECT_ROOT, "data/logs.db")
SCHEMA = rdflib.Namespace("http://schema.org/")

# Helper Functions
def __plant_crud__(form, plant_iri=None):
    msg = None
    action = form.get('action')
    description = form.get('description')
    conn = sqlite3.connect(LOG_PATH)
    cur = conn.cursor()
    plant_id_result = cur.execute("SELECT id FROM Plant WHERE iri=?",
        (plant_iri,)).fetchone()
    if len(plant_id_result) < 1:
        raise ValueError('Plant {} not found in log database'.format(
            plant_iri))
    plant_id = plant_id_result[0]
    # Specific types of Updates
    if action.endswith('water'):
        cur.execute("""INSERT INTO ActivityLog (activity, plant, description) 
VALUES (?,?,?);""",
            (1, plant_id, description))
        msg = "Watered {}".format(KNOWLEGE_GRAPH.value(
            subject=plant_iri,
            predicate=SCHEMA.name))
    cur.close()
    con.close()
    return msg

# Template Filter Functions
@app.template_filter('get_label')
def label_(entity_iri, lang_code):
    for label in KNOWLEGE_GRAPH.objects(subject=entity_iri,
        predicate=rdflib.RDFS.label):
        if label.language == lang_code:
            return label
    return ''
                  
# View Functions                  
@app.route("/plant/")
@app.route("/plant/<path:uuid>", methods=["GET", "POST"])
def plant(uuid=None):
    if uuid is None:
        plants = [plant_iri for plant_iri in KNOWLEGE_GRAPH.subjects(
                                                predicate=rdflib.RDF.type,
                                                object=SCHEMA.HousePlant)]
        return render_template("plants.html", plants=plants)
    plant_iri = rdflib.URIRef("http://garden.local/plant/{}".format(uuid))
    class_ = KNOWLEGE_GRAPH.value(subject=plant_iri,
                                  predicate=rdflib.RDF.type)
    if class_ is None:
        abort(404)
    elif class_ != SCHEMA.HousePlant:
        abort(401)
    if request.method.startswith("POST"):
        msg = __plant_crud__(request.form, plant_iri)
        flash("You {} plant {}".format(request.form.get('action'), uuid))
        return redirect(url_for('plant', uuid=uuid))
    return render_template("plant.html",
        plant=plant_iri)


@app.route("/")
def hub():
    return render_template('hub.html', 
        stats={"triples": len(KNOWLEGE_GRAPH)},
	now=datetime.datetime.utcnow())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=13691, debug=True)
