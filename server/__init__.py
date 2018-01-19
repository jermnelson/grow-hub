"""
  Grow-Hub Sensor Server

"""
__author__ = "Jeremy Nelson, Timothy Semple"


import datetime
import os
import sqlite3
import uuid

import rdflib

from collections import OrderedDict
from flask import Flask, flash, render_template, request, redirect
from flask import url_for

app = Flask(__name__)
app.secret_key = 'GROWHUB'

PROJECT_ROOT = os.path.split(os.path.dirname(os.path.abspath((__file__))))[0]
KNOWLEGE_GRAPH = rdflib.Graph()
KNOWLEGE_GRAPH.parse(os.path.join(PROJECT_ROOT, "instance/current.ttl"),
                     format='turtle')
LOG_PATH = os.path.join(PROJECT_ROOT, "instance/logs.db")
SCHEMA = rdflib.Namespace("http://schema.org/")

# Helper Functions
def __add_plant__(name, latin_name, purchased_date, type_of=SCHEMA.HousePlant):
    new_plant_iri = rdflib.URIRef(
        "http://garden.local/plant/{}".format(uuid.uuid1()))
    KNOWLEGE_GRAPH.add(
        (new_plant_iri, 
         rdflib.RDF.type, 
         type_of))
    KNOWLEGE_GRAPH.add(
        (new_plant_iri, 
         rdflib.RDFS.label, 
         rdflib.Literal(name, lang="en")))
    KNOWLEGE_GRAPH.add(
        (new_plant_iri, 
         rdflib.RDFS.label, 
         rdflib.Literal(latin_name, lang="la")))
    KNOWLEGE_GRAPH.add(
        (new_plant_iri, 
         SCHEMA.name, 
         rdflib.Literal(name, lang="en")))
    KNOWLEGE_GRAPH.add(
        (new_plant_iri, 
         SCHEMA.purchasedDate, 
         rdflib.Literal(purchased_date)))
    with open(os.path.join(PROJECT_ROOT, "instance/current.ttl"), "wb+") as fo:
        fo.write(KNOWLEGE_GRAPH.serialize(format='turtle'))
    return new_plant_iri
    

def __plant_crud__(form, plant_iri=None):
    msg = None
    conn = sqlite3.connect(LOG_PATH)
    cur = conn.cursor()
    action = form.get('action')
    # Creates a new Plant and save to file
    if action.startswith("create"):
        name = form.get("name")
        latin_name = form.get("latin")
        purchased_date = form.get("purchasedDate")
        plant_iri = __add_plant__(name, latin_name, purchased_date)
        cur.execute("INSERT INTO Plant (iri) VALUES (?,)",
            (plant_iri,))
        conn.commit()
        msg = "Added plant {} ({})".format(name, latin_name)
    description = form.get('description')
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
        msg = "Watered {} on {}".format(KNOWLEGE_GRAPH.value(
            subject=plant_iri,
            predicate=SCHEMA.name),
            datetime.datetime.utcnow().isoformat())
        conn.commit()
    cur.close()
    conn.close()
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
        # Add a new plant
        if request.method.startswith("POST"):
            print("Shourld route to {}".format(request.form.keys()))
            msg = __plant_curd__(request.form)    
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
        flash(msg)
        return redirect(url_for('plant', uuid=uuid))
    plant_activity = []
    con = sqlite3.connect(LOG_PATH)
    cur = con.cursor()
    cur.execute("""SELECT ActivityLog.taken, ActivityLog.description, Activity.name
FROM ActivityLog, Activity, Plant
WHERE ActivityLog.activity = Activity.id AND 
ActivityLog.plant = Plant.id AND
Plant.iri=?""", (plant_iri,))
    for row in cur.fetchall():
        plant_activity.append({"date": row[0],
                               "description": row[1],
                               "activity": row[2]})
    cur.close()
    con.close()
    return render_template("plant.html",
        plant=plant_iri,
        activity=plant_activity)


@app.route("/")
def hub():
    return render_template('hub.html', 
        stats={"triples": len(KNOWLEGE_GRAPH)},
	now=datetime.datetime.utcnow())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=13691, debug=True)
