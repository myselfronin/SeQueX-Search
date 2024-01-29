from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
import ssl
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import os
from app import logger

CSO_ENDPOINT = os.environ.get('CSO_FUSEKI_HOST_ENPOINT')

sparql = SPARQLWrapper("http://fuseki:3030/cso/sparql")

# Disable SSL verification (use with caution)

class CSOQueryService:
    # Path of CSO file
    CSO_FILE_PATH = 'storage/CSO.3.3.ttl'

    # Define Namespaces
    CSO = Namespace("http://cso.kmi.open.ac.uk/schema/cso#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    DBPEDIA = Namespace("http://dbpedia.org/resource/")

    def __init__(self):
        self.graph = Graph()
        self.graph.parse(self.CSO_FILE_PATH, format="turtle")

    def construct_sparql_query(self, query_string):
        return f"""
            PREFIX cso: <http://cso.kmi.open.ac.uk/schema/cso#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX dbr: <http://dbpedia.org/resource/>
            
            {query_string}
        """
    
    # Executes the SPARQL query on the fuseki server to optimize the call better than file based rdflib graph
    def execute_query_in_fuseki_server(self, query_string):
        sparql.setQuery(self.construct_sparql_query(query_string))
        sparql.setMethod(POST)
        sparql.setReturnFormat(JSON)
        try:
            return sparql.query().convert()
        except Exception as e:
            print(f"An error occurred query fuseki cso: {e}")
            logger.error(e)
            return None
        
    # Executes the SPARQL query in CSO ontology file with rdflib graph
    def execute_query(self,query_string):
        g = Graph()
        g.parse(self.CSO_FILE_PATH, format="turtle")

        # Prepare SPARQL Query
        q = prepareQuery(query_string, initNs={"cso": self.CSO, "rdf": self.RDF, "rdfs": self.RDFS, "dbr": self.DBPEDIA})

        # Execute SPARQL Query
        results = g.query(q)

        return results
    
    def get_topics_from_cso(self):
        """
        Retrieves a list of topics from the CSO ontology.
        Returns:
            A dictionary where keys are topic URIs and values are the corresponding labels.
        """

        query_string = """
            SELECT ?topic ?topicLabel
            WHERE {
                ?topic rdf:type cso:Topic .
                ?topic rdfs:label ?topicLabel
            }
            """
        results = self.execute_query(query_string)
        
        topics = {str(row.topic): str(row.topicLabel) for row in results}
        
        return topics
    
    def get_topics_from_cso_with_dbpedia_uri(self):
        """
        Retrieves a list of topics from the CSO ontology, including their DBpedia URIs.
        Returns:
            A dictionary where each key is a topic URI, and each value is a dictionary with 'label' and 'dbpedia_uri'.
        """
        
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
        results = self.execute_query(query_string)

        topics = {
            str(row.topic): {
                'label': str(row.topicLabel),
                'dbpedia_uri': str(row.dbpediaResource) if row.dbpediaResource else None
            }
            for row in results
        }
        return topics

    # Executed in fuseki server for improving the performance
    def get_related_equivalent_topics(self, topic_uris):
        """
        Retrieves topics that are equivalent to a given list topics.

        :param topic_uris: List of URIs of the topics.
        :return: A dictionary where keys are topics URIs and values are lists of UIRs of related equivalent topics.
        """

        values_clause = " ".join(f"<{uri}>" for uri in topic_uris)
        
        query_string = f"""
        SELECT ?topic (GROUP_CONCAT(?relatedTopic; separator=",") AS ?relatedTopics)
        WHERE {{
            VALUES ?topic {{{values_clause}}}
            ?topic cso:relatedEquivalent ?relatedTopic .
        }}
        GROUP BY ?topic
        """

        results = self.execute_query_in_fuseki_server(query_string)
    
        related_topics = {}

        if results and "results" in results and "bindings" in results["results"]:
            for row in results["results"]["bindings"]:
                if "relatedTopics" in row and "value" in row["relatedTopics"]:
                    related_topics[row["topic"]["value"]] = row["relatedTopics"]["value"]

        return related_topics

    # Executed in fuseki server for improving the performance
    def get_sub_topics(self, topic_uris):
        """
        Retrieves super-topics (broader topics) of a given list of topics.

        :param topic_uris: List of URIs of the topics.
        :return:A dictionary where keys are topics URIs and values are lists of UIRs of sub topics.
        """

        values_clause = " ".join(f"<{uri}>" for uri in topic_uris)
        
        query_string = f"""
        SELECT ?topic (GROUP_CONCAT(?subTopic; separator=",") AS ?subTopics)
        WHERE {{
            VALUES ?topic {{{values_clause}}}
            ?topic cso:superTopicOf ?subTopic .
        }}
        GROUP BY ?topic
        """
        results = self.execute_query_in_fuseki_server(query_string)

        sub_topics = {}

        if results and "results" in results and "bindings" in results["results"]:
            for row in results["results"]["bindings"]:
                if "subTopics" in row and "value" in row["subTopics"]:
                    sub_topics[row["topic"]["value"]] = row["subTopics"]["value"]
        return sub_topics
    
    # Executed in fuseki server for improving the performance
    def get_uris_by_topic_labels(self, labels):
        """
        Retrieves URIs of topics based on their labels.

        :param labels: A list of labels of the topics.
        :return: A dictionary where keys are labels and values are their corresponding URIs.
        """
        uris = {}

        for label in labels:
            query_string = f"""
            SELECT ?topic
            WHERE {{
                ?topic rdf:type cso:Topic .
                ?topic rdfs:label ?label .
                FILTER(LCASE(STR(?label)) = LCASE("{label}"))
            }}
            """
            results = self.execute_query_in_fuseki_server(query_string)

            if results and "results" in results and "bindings" in results["results"]:
                for row in results["results"]["bindings"]:
                    if "topic" in row and "value" in row["topic"]:
                        uris[label] = row["topic"]["value"]
                        break  # Break after the first match

        return uris