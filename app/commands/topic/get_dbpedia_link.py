from SPARQLWrapper import SPARQLWrapper, JSON, POST
import click
import os
from app.models import Topics
from app import db
from app.services.cso_query import CSOQueryService
import ssl

# Disable SSL verification (use with caution)
ssl._create_default_https_context = ssl._create_unverified_context
MAKG_ENDPOINT = os.environ.get('MAKG_ENDPOINT')

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')

SOLR_TOPICS_URL = f"{SOLR_BASE_URL}/topics/update"
"""
The CSO Ontology have #sameAs relation to DBpedia from where the description are to be pulled. 
However many of the topics such relations. Some of those have the #relatedLink to MAG from which 
the DBpedia can be retrieved. Also some has the wikipedia link from which dbpedia can be generated
"""
@click.command("topic:get_dbpedia_link")
def get_dbpedia_link():
    click.echo("Pulling DBpedia Link...")

    # Query to find all topics without a DBpedia URI
    unprocessed_topics = Topics.query.filter(Topics.dbpedia_uri.is_(None)).all()
    uris = [topic.cso_uri for topic in unprocessed_topics]

    cso_topics_with_dbpedia_link = get_makg_link_from_related_link_relation(uris)

    topic_models = Topics.query.filter(Topics.cso_uri.in_(cso_topics_with_dbpedia_link.keys())).all()

    for topic in topic_models:
        topic.dbpedia_uri = cso_topics_with_dbpedia_link[topic.cso_uri] 
        db.session.add(topic)
    db.session.commit()
    
    click.echo("Action completed")


def get_makg_link_from_related_link_relation(topic_uris):
    filter_string = " ".join(f"<{uri}>" for uri in topic_uris)
        
    query_string = f"""
    SELECT ?topic ?makgLink
    WHERE {{
        VALUES ?topic {{{filter_string}}}
        ?topic <http://schema.org/relatedLink> ?makgLink .
        FILTER(STRSTARTS(STR(?makgLink), 'https://academic.microsoft.com'))
    }}
    """
    results = CSOQueryService().execute_query_in_fuseki_server(query_string)
    makg_link_of_topic_dict = {}

    # The related link provided by the CSO ontology is for academic.microsoft.com which is not working or its broken
    # Hence the domain is changed to https://makg.org/entity with the same idenrifier from academic.microsoft.com
    if results and "results" in results and "bindings" in results["results"]:
        for row in results["results"]["bindings"]:
            if "makgLink" in row and "value" in row["makgLink"]:
                makg_link_of_topic_dict[row["topic"]["value"]] = convert_microsoft_to_makg(row["makgLink"]["value"]) if row["makgLink"]["value"] else None

    return get_dbpedia_link_from_makg_link(makg_link_of_topic_dict)


def get_dbpedia_link_from_makg_link(makg_uris_topic_dict):
    dbpedia_uris_topic_dict = {}
    makg_dpedia_dict = {}
    # Filter out empty strings and join
    filter_string = ", ".join(makg_uri for makg_uri in makg_uris_topic_dict.values() if makg_uri is not None)

    query_string = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?makgLink ?dbpediaLink
    WHERE{{
        ?makgLink owl:sameAs ?dbpediaLink .
        FILTER (?makgLink IN ({filter_string}))
    }}
    """
    sparql = SPARQLWrapper(MAKG_ENDPOINT)

    sparql.setQuery(query_string)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if results and "results" in results and "bindings" in results["results"]:
        for row in results["results"]["bindings"]:
            if "dbpediaLink" in row and "value" in row["dbpediaLink"]:
                makg_dpedia_dict[row["makgLink"]["value"]] = row["dbpediaLink"]["value"]
    

    for cso_uri, makg_uri in makg_uris_topic_dict.items():
        makg_uri = makg_uri[1:-1] # Removing <> from the makg_uri
        dbpedia_uris_topic_dict[cso_uri] = makg_dpedia_dict[makg_uri] if makg_uri in makg_dpedia_dict else None
    
    return dbpedia_uris_topic_dict



def get_description_from_dbpedia(dbpedia_uri):
    """Pulls the description for a given DBpedia URI."""
    sparql_query =  f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?description
    WHERE {{
        <{dbpedia_uri}> dbo:abstract ?description .
        FILTER (lang(?description) = 'en')
    }}
    """

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if results["results"]["bindings"]:
        return results["results"]["bindings"][0]["description"]["value"]
    return None

def process_topic(topic):
    """Processes a single topic, updating its description and processed status."""
    if topic.dbpedia_uri:
        description = get_description_from_dbpedia(topic.dbpedia_uri)
        if description:
            topic.description = description
    topic.description_pulled = True
    db.session.add(topic)
    db.session.commit()

def convert_microsoft_to_makg(url):
    try:
        # Extract the numeric identifier from the URL
        identifier = url.split('/detail/')[-1]

        # Check if the identifier is numeric
        if not identifier.isdigit():
            return ""

        # Construct the new URL
        new_url = f'<https://makg.org/entity/{identifier}>'
        return new_url
    except Exception:
        return ""
