import click
import json
import requests
import os
from app.models import Papers
from . import update_solr_schema

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')
SOLR_PAPER_CORE_NAME = 'papers'
SOLR_PAPERS_URL = f"{SOLR_BASE_URL}/{SOLR_PAPER_CORE_NAME}/update"

BATCH_SIZE = 1000

@click.command("solr:index_papers")
def solr_index_papers():
    click.echo("Updating the scheme of the core....")
    # Define the fields to be added or updated
    fields_to_update = [
        {"name": "title", "type": "text_general", "indexed": True, "stored": True, "multiValued": False},
        {"name": "abstract", "type": "text_general", "indexed": True, "stored": True, "multiValued": False},
        {"name": "semantic_topics", "type": "text_general", "indexed": True, "stored": True, "multiValued": True},
        {"name": "doi", "type": "string", "indexed": False, "stored": True, "multiValued": False},
    ]
    update_solr_schema(SOLR_PAPER_CORE_NAME,fields_to_update )
    
    click.echo("Indexing papers to solr...")

    total_papers = Papers.query.count()
    iteration = 1

    for offset in range(0, total_papers, BATCH_SIZE):
        batch = Papers.query.order_by(Papers.id).offset(offset).limit(BATCH_SIZE).all()

        solr_docs = [{
            "title": pub.title, 
            "abstract": pub.abstract if pub.abstract else "", 
            "doi": pub.doi if pub.doi else "",
            "semantic_topics": pub.semantic_topics if pub.semantic_topics else []
            } for pub in batch]

        solr_json = json.dumps(solr_docs)
        response = requests.post(SOLR_PAPERS_URL, data=solr_json, headers={'Content-Type': 'application/json'}, params={"commitWithin": 1000})

        if response.status_code != 200:
            print(f"Failed to index batch starting at offset {offset}: {response.text}")
            break
        else:
            print(f"Completed indexing of batch: {iteration * BATCH_SIZE}")
        iteration += 1
    
    click.echo("Solr indexing completed")

    