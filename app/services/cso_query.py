from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

CSO_FILE_PATH='storage/CSO.3.3.ttl'

def get_topics_from_cso():
    g = Graph()
    g.parse(CSO_FILE_PATH, format="turtle")

    # Define Namespaces
    CSO = Namespace("http://cso.kmi.open.ac.uk/schema/cso#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    # Prepare SPARQL Query
    q = prepareQuery("""
    SELECT ?topic ?topicLabel
    WHERE {
        ?topic rdf:type cso:Topic .
        ?topic rdfs:label ?topicLabel
    }
    """, initNs={"cso": CSO, "rdf": RDF, "rdfs": RDFS})

    # Execute SPARQL Query
    results = g.query(q)

    topics = {str(row.topic): str(row.topicLabel) for row in results}
    
    return topics


