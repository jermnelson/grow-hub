"""
  Grow-Hub Sensor Server

"""
__author__ = "Jeremy Nelson, Timothy Semple"


import datetime
import os
import rdflib
from flask import Flask, render_template

app = Flask(__name__)
PROJECT_ROOT = os.path.split(os.path.dirname(os.path.abspath((__file__))))[0]
KNOWLEGE_GRAPH = rdflib.Graph()
KNOWLEGE_GRAPH.parse(os.path.join(PROJECT_ROOT, "data/current.ttl"),
                     format='turtle')
SCHEMA = rdflib.Namespace("http://schema.org/")

@app.template_filter('get_label')
def label_(entity_iri, lang_code):
    for label in KNOWLEGE_GRAPH.subjects(subject=entity_iri,
        predicate=rdflib.RDFS.label):
        if label.lang == lang_code:
            return label
    return ''
                                    

@app.route("/plant/<path:uuid>")
def plant(uuid):
    plant_iri = rdflib.URIRef("http://garden.local/plant/{}".format(uuid))
    class_ = KNOWLEGE_GRAPH.value(subject=plant_iri,
                                  predicate=rdflib.RDF.type)
    if class_ is None:
        abort(404)
    elif class_ != SCHEMA.HousePlant:
        abort(401)
    return render_template("plant.html",
        plant=plant_iri)

@app.route("/")
def hub():
    return render_template('hub.html', 
	now=datetime.datetime.utcnow())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=13691, debug=True)
