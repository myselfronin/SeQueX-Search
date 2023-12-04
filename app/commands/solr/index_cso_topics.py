import click
import json
import requests
import os
from app.services.cso_query import get_topics_from_cso

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')

SOLR_TOPICS_URL = f"{SOLR_BASE_URL}/topics/update"

@click.command("solr:index_cso_topics")
def solr_index_topics():
    click.echo("Indexing CSO topics to solr...")

    topics = get_topics_from_cso()

    documents = [{'id': f"CSO_TOPIC_{i}", 'topic': topic} for i, topic in enumerate(topics)]

    # POST Request to store the topic index
    response = requests.post(SOLR_TOPICS_URL, data=json.dumps(documents), headers={'Content-Type': 'application/json'}, params={"commitWithin": 1000})

    if response.status_code != 200:
        print("Failed to index.")
    else:
        print("Indexing completed.")

    