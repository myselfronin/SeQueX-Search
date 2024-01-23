from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

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

    def get_related_equivalent_topics(self, topic_uri):
        """
        Retrieves topics that are equivalent to a given topic.

        :param topic_uri: URI of the topic.
        :return: A list of URIs of related equivalent topics.
        """
        
        query_string = f"""
        SELECT ?relatedTopic
        WHERE {{
            <{topic_uri}> cso:relatedEquivalent ?relatedTopic .
        }}
        """
        results = self.execute_query(query_string)
        related_topics = [str(row.relatedTopic) for row in results]
        return related_topics

    def get_super_topics(self, topic_uri):
        """
        Retrieves super-topics (broader topics) of a given topic.

        :param topic_uri: URI of the topic.
        :return: A list of URIs of super-topics.
        """

        query_string = f"""
        SELECT ?superTopic
        WHERE {{
            <{topic_uri}> cso:superTopicOf ?superTopic .
        }}
        """
  
        results = self.execute_query(query_string)
        super_topics = [str(row.superTopic) for row in results]
        return super_topics