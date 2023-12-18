import click
import json
import re
from nltk.tokenize import word_tokenize, sent_tokenize

from app.models import Papers

# Constants
BATCH_SIZE = 10000
ENTITY_TYPE = 'TOPIC'  # Entity type used in BIO tagging

@click.command("make:bio_tagged_dataset")
def make_bio_tagged_dataset():
    """Command to create an annotated dataset with BIO tagging."""
    click.echo("Creating bio tagged dataset...")

    # Initialize pagination variables
    limit = BATCH_SIZE
    offset = 0
    total_paper_count = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).count()

    doc_id = 1
    with open('storage/dataset/bio_tagged_dataset.jsonl', 'a') as file:
        while True:
            # Fetch batch of papers from the database
            papers = Papers.query.filter(Papers.title != None, Papers.syntactic_topics != None).limit(limit).offset(offset).all()

            for paper in papers:
                # Annotate each paper
                annotated_dict = annotate_paper(paper, doc_id)
                if annotated_dict['bio_tags']:  # Check if there are BIO tags
                    # Write the annotated data to the file
                    annotated_string = json.dumps(annotated_dict)
                    file.write(annotated_string + '\n')
                    doc_id += 1

            # Update offset for next batch
            offset += limit

            # Exit loop if all records have been processed
            if offset >= total_paper_count or not papers:
                break
    click.echo("Finish annotation")

def annotate_paper(paper, doc_id):
    """
    Annotate a paper with BIO tags.
    
    Args:
    - paper: The paper object from the database.
    - doc_id: Document ID for identification in the dataset.

    Returns:
    - A dictionary containing the paper ID, text, and BIO tags.
    """
    # Combine title and abstract of the paper
    paper_text = paper.title + ' ' + paper.abstract

    # Normalize the text for consistent matching
    normalized_text = paper_text.lower()

    # Normalize the topics
    normalized_topics = [topic.lower() for topic in paper.syntactic_topics]

    # Find matches of topics in the text
    annotations = []
    for topic in normalized_topics:
        for match in re.finditer(re.escape(topic), normalized_text):
            start, end = match.span()
            annotations.append({'topic': topic, 'start': start, 'end': end})

    return prepare_annoted_doc(doc_id, paper_text, annotations)

def tokenize_with_annotations(text, annotations):
    """
    Tokenize text and assign BIO tags to tokens.

    Args:
    - text: The full text to tokenize.
    - annotations: List of topic annotations with start and end indices.

    Returns:
    - A tuple of tokens and their corresponding BIO tags.
    """
    tokens = word_tokenize(text)
    labels = ['O'] * len(tokens)  # Initialize all labels as 'O' (Outside)

    # Assigning BIO tags to tokens based on annotations
    for annotation in annotations:
        start, end = annotation['start'], annotation['end']
        inside = False  # Flag to mark if we are inside an annotated span

        for i, token in enumerate(tokens):
            token_start = text.find(token, start if inside else 0)

            # Check if the token is within an annotated span
            if start <= token_start < end:
                labels[i] = ('B-' if not inside else 'I-') + ENTITY_TYPE
                inside = True
                start = token_start + len(token)
            else:
                inside = False

    return tokens, labels

def prepare_annoted_doc(paper_id, paper_text, annotations):
    """
    Prepare the annotated document data.

    Args:
    - paper_id: ID of the paper.
    - paper_text: Text of the paper.
    - annotations: Annotations for the text.

    Returns:
    - A dictionary with the paper ID, text, and BIO tags.
    """
    tokens, bio_tags = tokenize_with_annotations(paper_text, annotations)

    # Filter out sentences that don't contain any topic entity
    filtered_text, filtered_tags = filter_sentences(tokens, bio_tags, paper_text)

    doc_data = {
        "id": paper_id,
        "text": ' '.join(filtered_text),
        "bio_tags": filtered_tags
    }

    return doc_data

def filter_sentences(tokens, bio_tags, original_text):
    """
    Filter out sentences that don't contain any annotated topic.

    Args:
    - tokens: List of tokens from the text.
    - bio_tags: Corresponding BIO tags for each token.
    - original_text: The original text for sentence tokenization.

    Returns:
    - A tuple of filtered tokens and their corresponding BIO tags.
    """
    filtered_tokens = []
    filtered_tags = []

    # Split the original text into sentences
    sentences = sent_tokenize(original_text)
    token_index = 0

    # Process each sentence
    for sentence in sentences:
        sentence_tokens = tokens[token_index:token_index + len(word_tokenize(sentence))]
        sentence_tags = bio_tags[token_index:token_index + len(sentence_tokens)]
        token_index += len(sentence_tokens)

        # Keep sentence if it contains a topic entity
        if any(tag.startswith('B-') or tag.startswith('I-') for tag in sentence_tags):
            filtered_tokens.extend(sentence_tokens)
            filtered_tags.extend(sentence_tags)

    return filtered_tokens, filtered_tags
