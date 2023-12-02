import click
import json
import spacy
from spacy.tokens import DocBin
import random
from pathlib import Path


from app.models import Papers
import os

BATCH_SIZE = 30000
SPACY_DATASET_OUTPUT_PATH='storage/dataset/'
JSONL_ANNOTATION_FILE_PATH='storage/dataset/annotations.jsonl'

@click.command("spacy:prepare_dataset")
@click.option('--load', default=None, help='Load a pretrained SpaCy model.')

def prepare_dataset(load):
    click.echo("Converting .jsonl dataset into .spacy...")

    jsonl_to_spacy_chunks(JSONL_ANNOTATION_FILE_PATH, SPACY_DATASET_OUTPUT_PATH, load)

def jsonl_to_spacy_chunks(jsonl_file_path, output_dir, model_name, chunk_size=BATCH_SIZE, test_size=0.2):
    # Load the model, either pretrained or blank
    try:
        if model_name:
            nlp = spacy.load(model_name)
            output_dir += model_name
            click.echo(f"Loaded pretrained model: {model_name}")
        else:
            nlp = spacy.blank("en")
            output_dir += 'en'
            click.echo("Loaded a blank 'en' model")
    except IOError:
        click.echo(f"Error: Model '{model_name}' not found. Download it: python -m spacy download {model_name}")
        return
    

    # Load data from .jsonl file
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]

        # Split data into training and testing
        random.shuffle(data)
        split_index = int(len(data) * (1 - test_size))
        train_data = data[:split_index]
        test_data = data[split_index:]

        # Process and save data in chunks
        for dataset, dataset_type in [(train_data, 'train'), (test_data, 'test')]:
            for i in range(0, len(dataset), chunk_size):
                doc_bin = DocBin()
                for entry in dataset[i:i+chunk_size]:
                    text = entry['text']
                    annotations = entry['label']
                    doc = nlp.make_doc(text)
                    ents = []
                    for start, end, label in annotations:
                        span = doc.char_span(start, end, label=label)
                        if span is not None:
                            ents.append(span)
                    doc.ents = ents
                    doc_bin.add(doc)
                
                # Create output dir path if not exists
                output_dir_path = Path(output_dir)
                output_dir_path.mkdir(parents=True, exist_ok=True)
                
                # Save the DocBin object
                output_file = f"{output_dir}/{dataset_type}_{i//chunk_size}.spacy"
                doc_bin.to_disk(output_file)

