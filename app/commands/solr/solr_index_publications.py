import click
import json
import requests
import os
from app.models import Papers

SOLR_PAPERS_URL = os.environ.get('SOLR_BASE_URL')
SOLR_PAPERS_URL = f"{SOLR_PAPERS_URL}/papers/update"

BATCH_SIZE = 1000

@click.command("solr:index_papers")
def solr_index_papers():
    click.echo("Indexing papers to solr...")

    total_papers = Papers.query.count()
    iteration = 1

    for offset in range(0, total_papers, BATCH_SIZE):
        batch = Papers.query.order_by(Papers.id).offset(offset).limit(BATCH_SIZE).all()
        solr_docs = [{"title": pub.title, "abstract": pub.abstract if pub.abstract else ""} for pub in batch]

        solr_json = json.dumps(solr_docs)
        response = requests.post(SOLR_PAPERS_URL, data=solr_json, headers={'Content-Type': 'application/json'}, params={"commitWithin": 1000})

        if response.status_code != 200:
            print(f"Failed to index batch starting at offset {offset}: {response.text}")
            break
        else:
            print(f"Completed indexing of batch: {iteration * BATCH_SIZE}")
        iteration += 1
    
    click.echo("Solr indexing completed")

    