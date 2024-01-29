import click
import json
import requests
import os
from . import update_solr_schema

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')
SOLR_EVAL_PAPER_CORE_NAME="evaluationpapers"
SOLR_EVAL_PAPERS_URL = f"{SOLR_BASE_URL}/{SOLR_EVAL_PAPER_CORE_NAME}/update"
GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandard.json'

@click.command("solr:index_evaluation_paper")
def solr_index_evaluation_paper_from_gold_dataset():
    """
    For evaluation of the retrieval the 70 papers from Gold Standard
    dataset is indexed in solr 
    """
    click.echo("Updating the scheme of the core....")
    # Define the fields to be added or updated
    fields_to_update = [
        {"name": "title", "type": "text_general", "indexed": True, "stored": True, "multiValued": False},
        {"name": "abstract", "type": "text_general", "indexed": True, "stored": True, "multiValued": False},
        {"name": "semantic_topics", "type": "text_general", "indexed": True, "stored": True, "multiValued": True},
        {"name": "doi", "type": "string", "indexed": False, "stored": True, "multiValued": False},
    ]

    update_solr_schema(SOLR_EVAL_PAPER_CORE_NAME,fields_to_update )
    
    click.echo("Indexing evaluation papers to solr from file...")

    # Read papers from the provided JSON file
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        papers = json.load(file)

    # Assuming the JSON structure is a list of objects with 'title' and 'abstract' keys
    solr_docs = [{
        "title": paper['title'], 
        "abstract": paper['abstract'] if paper['abstract'] else "",
        "doi": paper['doi'] if paper['doi'] else "",
        "semantic_topics": paper['gold_standard']['majority_vote']
        } for paper_id, paper in papers.items()]

    # Convert to JSON for Solr
    solr_json = json.dumps(solr_docs)
    response = requests.post(SOLR_EVAL_PAPERS_URL, data=solr_json, headers={'Content-Type': 'application/json'}, params={"commitWithin": 1000})

    # Check the response status
    if response.status_code != 200:
        print(f"Failed to index papers: {response.text}")
    else:
        print(f"Completed indexing of {len(papers)} papers")

    click.echo("Solr indexing completed from file")

