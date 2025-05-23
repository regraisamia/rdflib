from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Namespace personnalisé
UNIV = Namespace("http://example.org/university/")

# Charger le fichier RDF local
def load_graph():
    graph = Graph()
    try:
        graph.parse("data/university.ttl", format="turtle")
    except Exception as e:
        print(f"Erreur lors du chargement du fichier RDF : {str(e)}")
    return graph

# Sauvegarder le graphe RDF dans le fichier
def save_graph(graph):
    graph.serialize("data/university.ttl", format="turtle")

# Route pour servir la page principale
@app.route("/", methods=["GET"])
def index():
    graph = load_graph()

    # Extraire les départements, filières, étudiants, professeurs, chercheurs et cours
    departments = list(graph.subjects(RDF.type, UNIV.Department))
    fields = list(graph.subjects(RDF.type, UNIV.Field))
    students = list(graph.subjects(RDF.type, UNIV.Student))
    courses = list(graph.subjects(RDF.type, UNIV.Course))

    return render_template(
        "index.html",
        departments=departments,
        fields=fields,
        students=students,
        courses=courses
    )

# Route pour afficher le formulaire d'ajout
@app.route("/add", methods=["GET"])
def add_entity_form():
    graph = load_graph()

    # Extraire les départements, filières et cours pour les menus déroulants
    departments = list(graph.subjects(RDF.type, UNIV.Department))
    fields = list(graph.subjects(RDF.type, UNIV.Field))
    courses = list(graph.subjects(RDF.type, UNIV.Course))

    return render_template("add_entity.html", departments=departments, fields=fields, courses=courses)

# Route pour ajouter une entité
@app.route("/add", methods=["POST"])
def add_entity():
    graph = load_graph()

    entity_type = request.form.get("entity_type")
    name = request.form.get("name")
    department = request.form.get("department")
    field = request.form.get("field")
    course = request.form.get("course")

    if not name or not entity_type:
        return jsonify({"error": "Veuillez remplir tous les champs."}), 400

    # Créer une nouvelle entité
    entity_uri = URIRef(f"http://example.org/university/{name.replace(' ', '_')}")

    if entity_type == "Department":
        graph.add((entity_uri, RDF.type, UNIV.Department))
        graph.add((entity_uri, RDFS.label, Literal(name)))

    elif entity_type == "Field":
        if not department:
            return jsonify({"error": "Veuillez spécifier un département pour la filière."}), 400
        graph.add((entity_uri, RDF.type, UNIV.Field))
        graph.add((entity_uri, RDFS.label, Literal(name)))
        graph.add((entity_uri, UNIV.belongsTo, URIRef(department)))

    elif entity_type == "Student":
        if not field:
            return jsonify({"error": "Veuillez spécifier une filière pour l'étudiant."}), 400
        graph.add((entity_uri, RDF.type, UNIV.Student))
        graph.add((entity_uri, RDFS.label, Literal(name)))
        graph.add((entity_uri, UNIV.enrolledIn, URIRef(field)))

    elif entity_type == "Teacher":
        if not department:
            return jsonify({"error": "Veuillez spécifier un département pour le professeur."}), 400
        graph.add((entity_uri, RDF.type, UNIV.Teacher))
        graph.add((entity_uri, RDFS.label, Literal(name)))
        graph.add((entity_uri, UNIV.worksIn, URIRef(department)))

    elif entity_type == "Researcher":
        if not department:
            return jsonify({"error": "Veuillez spécifier un département pour le chercheur."}), 400
        graph.add((entity_uri, RDF.type, UNIV.Researcher))
        graph.add((entity_uri, RDFS.label, Literal(name)))
        graph.add((entity_uri, UNIV.worksIn, URIRef(department)))

    elif entity_type == "Course":
        if not field:
            return jsonify({"error": "Veuillez spécifier une filière pour le cours."}), 400
        graph.add((entity_uri, RDF.type, UNIV.Course))
        graph.add((entity_uri, RDFS.label, Literal(name)))
        graph.add((entity_uri, UNIV.offeredBy, URIRef(field)))

    save_graph(graph)
    return redirect(url_for("index"))



# Route pour rechercher des entités
@app.route("/search", methods=["POST"])
def search():
    graph = load_graph()

    query = request.form.get("query")
    results = []

    # Requête SPARQL pour rechercher des entités correspondantes
    sparql_query = f"""
    PREFIX univ: <http://example.org/university/>
    SELECT ?entity ?label WHERE {{
        ?entity rdfs:label ?label .
        FILTER(CONTAINS(LCASE(?label), LCASE("{query}")))
    }}
    """
    for row in graph.query(sparql_query):
        results.append({
            "uri": str(row.entity),
            "label": str(row.label)
        })

    return render_template("search_results.html", results=results)


@app.route("/advanced_search", methods=["POST"])
def advanced_search():
    graph = load_graph()
    entity_type = request.form.get("entity_type")  # Type d'entité à rechercher
    name = request.form.get("name")  # Nom (facultatif)
    department = request.form.get("department")  # Département (facultatif)
    field = request.form.get("field")  # Filière (facultatif)
    results = []

    if entity_type == "Student":
        sparql_query = """
        PREFIX univ: <http://example.org/university/>
        SELECT ?student ?label WHERE {
            ?student a univ:Student ;
                     rdfs:label ?label .
        """
        filters = []
        if name:
            filters.append(f'FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))')
        if field:
            filters.append(f'?student univ:enrolledIn <{field}> .')
        if department:
            filters.append(f'?student univ:enrolledIn ?field . ?field univ:belongsTo <{department}> .')
        if filters:
            sparql_query += " " + " ".join(filters)
        sparql_query += "}"
        for row in graph.query(sparql_query):
            results.append({
                "uri": str(row.student),
                "label": str(row.label)
            })

    elif entity_type == "Teacher":
        sparql_query = """
        PREFIX univ: <http://example.org/university/>
        SELECT ?teacher ?label WHERE {
            ?teacher a univ:Teacher ;
                     rdfs:label ?label .
        """
        filters = []
        if name:
            filters.append(f'FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))')
        if department:
            filters.append(f'?teacher univ:worksIn <{department}> .')
        if filters:
            sparql_query += " " + " ".join(filters)
        sparql_query += "}"
        for row in graph.query(sparql_query):
            results.append({
                "uri": str(row.teacher),
                "label": str(row.label)
            })

    elif entity_type == "Researcher":
        sparql_query = """
        PREFIX univ: <http://example.org/university/>
        SELECT ?researcher ?label WHERE {
            ?researcher a univ:Researcher ;
                        rdfs:label ?label .
        """
        filters = []
        if name:
            filters.append(f'FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))')
        if department:
            filters.append(f'?researcher univ:worksIn <{department}> .')
        if filters:
            sparql_query += " " + " ".join(filters)
        sparql_query += "}"
        for row in graph.query(sparql_query):
            results.append({
                "uri": str(row.researcher),
                "label": str(row.label)
            })

    return render_template("search_results.html", results=results)


# Route pour afficher toutes les entités avec leurs relations
@app.route("/all_entities", methods=["GET"])
def all_entities():
    graph = load_graph()

    # Extraire toutes les entités et leurs relations
    entities = []
    for s, p, o in graph:
        entities.append({
            "subject": str(s),
            "predicate": str(p),
            "object": str(o)
        })

    return render_template("all_entities.html", entities=entities)




if __name__ == "__main__":
    app.run(debug=True)