import click
import json
import requests
import os
from app.services.cso import CSOQueryService

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')

SOLR_TOPICS_URL = f"{SOLR_BASE_URL}/topics/update"

@click.command("solr:index_cso_topics")
def solr_index_topics():
    click.echo("Indexing CSO topics to solr...")

    topics = CSOQueryService.get_topics_from_cso()

    documents = [{'uri': f"{uri}", 'topic': label} for uri, label in topics.items()]

    # POST Request to store the topic index
    response = requests.post(SOLR_TOPICS_URL, data=json.dumps(documents), headers={'Content-Type': 'application/json'}, params={"commitWithin": 1000})

    if response.status_code != 200:
        print("Failed to index.")
    else:
        print("Indexing completed.")

    