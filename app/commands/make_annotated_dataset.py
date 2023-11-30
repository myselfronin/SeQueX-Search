import click
import json
import re

from app.models import Papers

BATCH_SIZE = 1000

@click.command("make:annotated_dataset")
def make_annotated_dataset():
    click.echo("Creating annotated dataset...")

    limit = BATCH_SIZE
    offset = 0
    total_paper_count = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).count()

    # Calculate the split between trainig and test dataset : 80/20
    train_count = int(total_paper_count * 0.8)

    doc_id = 1
    with open('storage/annotated_train_dataset.jsonl', 'a') as train_file, open('storage/annotated_test_dataset.jsonl', 'a') as test_file:
        while True:
            papers = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).limit(limit).offset(offset).all()

            for paper in papers:
                annnoted_dict = annotate_paper(paper, doc_id)
                # Check if 'label' key has a non-empty array
                if len(annnoted_dict["label"]) > 0:
                    annotated_string = json.dumps(annnoted_dict)

                    # Check the append to train or test file
                    if doc_id <= train_count:
                        train_file.write(annotated_string + '\n')
                    else:
                        test_file.write(annotated_string + '\n')
        
                    doc_id += 1
                
            # Update the offset
            offset += limit

            #check if all records have been processed
            if offset >= total_paper_count or not papers: 
                break
    click.echo("Finish annotation")


def annotate_paper(paper, doc_id):
    # Combine title and abstract of the paper
    paper_text = paper.title + ' ' + paper.abstract

    # Normalize the text
    normalized_text = paper_text.lower()

    # Normalize the topic 
    normalized_topics = [topic.lower() for topic in paper.syntactic_topics]

    annotations = []
    for topic in normalized_topics:
        for match in re.finditer(re.escape(topic), normalized_text):
            start, end = match.span()
            annotations.append({'topic': topic, 'start': start, 'end': end})

    return prepare_annoted_doc(doc_id, paper_text, annotations)


def prepare_annoted_doc(paper_id, paper_text, annotations):
    doc_data = {
        "id": paper_id, 
        "text": paper_text,
        "label": [], 
    }

    for annotation in annotations:
        start = annotation['start']
        end = annotation['end']
        doc_data['label'].append([start, end, "TOPIC"])
    
    return doc_data