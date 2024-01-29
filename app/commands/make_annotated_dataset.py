import click
import json
import re

from app.models import Papers

BATCH_SIZE = 1000

@click.command("make:annotated_dataset")
def make_annotated_dataset():
    """
    This command string matches the topic in the abstract and title of the paper and annote the position where the TOPIC instance of CSO is situated.
    This was create as a starting point of training spacy model. But as we are
    using bert model a different annotation scheme is used called BIO tagging scheme.
    """
    click.echo("Creating annotated dataset...")

    limit = BATCH_SIZE
    offset = 0
    total_paper_count = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).count()

    doc_id = 1
    with open('storage/dataset/annotations.jsonl', 'a') as file:
        while True:
            papers = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).limit(limit).offset(offset).all()

            for paper in papers:
                annnoted_dict = annotate_paper(paper, doc_id)
                # Check if 'label' key has a non-empty array
                if len(annnoted_dict["label"]) > 0:
                    annotated_string = json.dumps(annnoted_dict)

                    file.write(annotated_string + '\n')

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

    # Sort annotations by their start position, and in case of a tie, by the end position (longer first)
    annotations = sorted(annotations, key=lambda x: (x['start'], -x['end']))

    # Initialize a variable to keep track of the end position of the last annotation
    last_end = -1

    for annotation in annotations:
        start = annotation['start']
        end = annotation['end']

        # Check if there is an overlap with the previous annotation
        if start < last_end:
            # If there's an overlap, only add the current annotation if it ends after the last one
            if end > last_end:
                # Update the last annotation with the current one if it's longer
                doc_data['label'][-1] = [start, end, "TOPIC"]
                last_end = end
        else:
            # If no overlap, add the annotation normally
            doc_data['label'].append([start, end, "TOPIC"])
            last_end = end

    return doc_data
