import ssl
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import os

AIDA_ENDPOINT = os.environ.get('AIDA_ENDPOINT')

sparql = SPARQLWrapper(AIDA_ENDPOINT)

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

def construct_sparql_query(query_string):
    return f"""
        PREFIX aida: <http://aida.kmi.open.ac.uk/ontology#> 
        PREFIX cito: <https://purl.org/spar/cito>
        PREFIX cso: <http://cso.kmi.open.ac.uk/schema/cso#> 
        PREFIX datacite: <http://purl.org/spar/datacite/>
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX mag: <https://makg.org/entity/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <http://schema.org/>

        {query_string}
    """

def execute_query(query):
    sparql.setQuery(query)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)

    try:
        return sparql.query().convert()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
