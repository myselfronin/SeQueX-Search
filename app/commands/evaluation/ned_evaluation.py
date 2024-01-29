import json
import click
from app import logger
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator

GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandardUpdated.json'

@click.command("evaluate:named_entity_disambiguation", help = "Evaluates the NED wrt GoldStandardUpdated Dataset")
def evaluate_named_entity_disambiguation():
    # Initialize counts for evaluation metrics
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    metrics_per_paper = []
    # Load dataset
    gold_dataset = load_dataset()
    count = 1
    for paper_id, paper_data in gold_dataset.items():
        print(count)
        # Initialize counts for the current paper
        tp_paper = 0
        fp_paper = 0
        fn_paper = 0

        logger.info(f"Evaluating paper id: {paper_id}")

        # Gold standard topics with URI
        gold_standard_topics_with_uri = paper_data["topics"]

        # Preprocess text (title + abstract)
        text = paper_data["title"] + " " + paper_data["abstract"]
        processed_text = TextProcessor().preprocess(text)

        # Get linked entities from NED
        linked_entities = NamedEntityDisambiguator(processed_text).get_linked_entities()

        # Evaluate the results
        for entity, uri in linked_entities.items():
            if entity in gold_standard_topics_with_uri:
                if uri == gold_standard_topics_with_uri[entity]:
                    true_positives += 1  # Correctly identified and linked
                    tp_paper += 1
                    logger.info(f"Correct Link: {entity} -> {uri}")
                else:
                    false_positives += 1  # Correctly identified but incorrectly linked
                    fp_paper += 1
                    logger.info(f"Incorrect Link: {entity} -> {uri}, Expected: {gold_standard_topics_with_uri[entity]}")
            else:
                false_positives += 1  # Incorrectly identified
                fp_paper += 1
                logger.info(f"False Entity Detected: {entity}")

        for entity, uri in gold_standard_topics_with_uri.items():
            if entity not in linked_entities:
                false_negatives += 1  # Missed entity
                fn_paper += 1
                logger.info(f"Missed Entity: {entity}")

        # Add metrics for this paper to the list
        metrics_per_paper.append((tp_paper, fp_paper, fn_paper))

        count += 1

    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if true_positives + false_negatives > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

    # Log final results
    logger.info(f"Final Evaluation - Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1_score:.4f}")

def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)

    

