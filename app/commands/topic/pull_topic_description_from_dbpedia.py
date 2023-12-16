from SPARQLWrapper import SPARQLWrapper, JSON
import click
import os
from app.services.cso_query import get_topics_from_cso
from app.models import Topics
from app import db

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')

SOLR_TOPICS_URL = f"{SOLR_BASE_URL}/topics/update"

@click.command("topic:get_description_from_dbpedia")
def pull_topic_description_from_dbpedia():
    click.echo("Pulling description of topic from DBPedia...")

    # Query to find all unprocessed topics with a DBpedia URI
    unprocessed_topics = Topics.query.filter_by(description_pulled=False).all()

    for topic in unprocessed_topics:
        try:
            process_topic(topic)
        except Exception as e:
            click.echo(f"An error occurred when pulling topic:{topic.dbpedia_uri}: {e}")
    
    click.echo("Action completed")




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