import json
import click
from app import logger
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator

GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandardUpdated.json'

@click.command("evaluate:linking_precision", help="Evaluates the disambiguation of entities provided in the GoldStandardUpdated Dataset")
def evaluate_linking_precision():
    logger.info("\n\n\n#########################################################################################\nEvaluating Linking Precision \n#########################################################################################\n\n\n")
    # Initialize a list to store precision for each paper
    precision_per_paper = []

    # Load dataset
    gold_dataset = load_dataset()
    count = 1
    for paper_id, paper_data in gold_dataset.items():
        print(count)
        logger.info(f"Evaluating paper id: {paper_id}")

        # Gold standard topics
        gold_standard_topics_with_uri = paper_data["topics"]
        gold_standard_topics = list(gold_standard_topics_with_uri.keys())

        # Disambiguate entities from gold standard topics
        disambiguator = NamedEntityDisambiguator("x") # x is just a dependency string need (No use for evaluating linking precision)

        # The recognized entities are directly from the gold standard as only linking is to be evaluated
        linked_entities = disambiguator.get_linked_entities_from_given_entities(gold_standard_topics)

        # Initialize counts for the current paper
        true_positives = 0
        false_positives = 0

        # Evaluate disambiguation accuracy
        for entity, expected_uri in gold_standard_topics_with_uri.items():
            if entity in linked_entities:
                if linked_entities[entity] == expected_uri:
                    true_positives += 1
                else:
                    false_positives += 1

        # Calculate and append precision for this paper
        paper_precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0
        precision_per_paper.append(paper_precision)

        count += 1

    # Log precision for each paper
    for idx, precision in enumerate(precision_per_paper, start=1):
        logger.info(f"Paper {idx}, Precision: {precision:.4f}")

    # Optional: Calculate and log overall precision
    overall_precision = sum(precision_per_paper) / len(precision_per_paper) if precision_per_paper else 0
    logger.info(f"Overall Evaluation - Precision: {overall_precision:.4f}")


    print("finished")

def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)
