from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

CSO_FILE_PATH='storage/CSO.3.3.ttl'

# Define Namespaces
CSO = Namespace("http://cso.kmi.open.ac.uk/schema/cso#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
DBPEDIA = Namespace("http://dbpedia.org/resource/")


def execute_query(query_string):
    g = Graph()
    g.parse(CSO_FILE_PATH, format="turtle")

    # Prepare SPARQL Query
    q = prepareQuery(query_string, initNs={"cso": CSO, "rdf": RDF, "rdfs": RDFS, "dbr": DBPEDIA})

    # Execute SPARQL Query
    results = g.query(q)

    return results


def get_topics_from_cso():
   
   query_string = """
    SELECT ?topic ?topicLabel
    WHERE {
        ?topic rdf:type cso:Topic .
        ?topic rdfs:label ?topicLabel
    }
    """
   results = execute_query(query_string)
   
   topics = {str(row.topic): str(row.topicLabel) for row in results}
   
   return topics

def get_topics_from_cso_with_dbpedia_uri():
   
   query_string = """
   SELECT ?topic ?topicLabel ?dbpediaResource
    WHERE {
        ?topic rdf:type cso:Topic .
        ?topic rdfs:label ?topicLabel .
        OPTIONAL {
            ?topic owl:sameAs ?dbpediaResource .
            FILTER(STRSTARTS(STR(?dbpediaResource), STR(dbr:)))
        }
    }
    """
   results = execute_query(query_string)

   topics = {
       str(row.topic): {
           'label': str(row.topicLabel),
           'dbpedia_uri': str(row.dbpediaResource) if row.dbpediaResource else None
       }
       for row in results
   }
   return topics

