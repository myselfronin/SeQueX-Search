import ssl
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import os

MAKG_ENDPOINT = os.environ.get('MAKG_ENDPOINT')
sparql = SPARQLWrapper(MAKG_ENDPOINT)

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context

def construct_sparql_query(query_string):
    return f"""
        PREFIX magc: <https://makg.org/class/>
        PREFIX mag: <https://makg.org/property/>
        PREFIX datacite: <http://purl.org/spar/datacite/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX fabio: <http://purl.org/spar/fabio/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

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
