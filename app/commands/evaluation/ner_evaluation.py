import json
import click
from app import logger
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator
from app.components.query_expansion import QueryExpansion

GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandardUpdated.json'

@click.command("evaluate:named_entity_recognition", help = "Evaluates the NER  wrt GoldStandard Dataset")
def evaluate_named_entity_recognition():
    logger.info("\n\n\n#########################################################################################\nEvaluating CSO NER \n#########################################################################################\n\n\n")

    true_positives = 0
    false_positives = 0
    false_negatives = 0
    metrics_per_paper = []
    gold_dataset = load_dataset()
    for paper_id, paper_data in gold_dataset.items():
        print(paper_id)
        logger.info("Evaluation paper id: " + str(paper_id))
        topic_present_in_paper = set(paper_data["topics"])

        ### Preprocess Query ###
        text = paper_data["title"] + " " + paper_data["abstract"]
        processed_text = TextProcessor().preprocess(text)

        ## NER ###
        recognized_entities = NamedEntityDisambiguator(processed_text).named_entity_recognition()

        predictions = set(recognized_entities)
        logger.info("Gold Standard Topics: " + ", ".join(topic_present_in_paper))
        logger.info("NER Model Predictions: " + ", ".join(recognized_entities))

        true_positives_of_paper = len(topic_present_in_paper.intersection(predictions))
        false_positives_of_paper = len(predictions - topic_present_in_paper)
        false_negatives_of_paper = len(topic_present_in_paper - predictions)

        logger.info("TP: " + str(true_positives_of_paper) + ", FP: " + str(false_positives_of_paper) + ", FN: " + str(false_negatives_of_paper) + "\n")
        
        # Add metrics for this paper to the list
        metrics_per_paper.append((true_positives_of_paper, false_positives_of_paper, false_negatives_of_paper))

        true_positives += true_positives_of_paper
        false_positives += false_positives_of_paper
        false_negatives += false_negatives_of_paper

    # Calculating precision, recall, and F1 score
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Modified accuracy calculation
    accuracy = true_positives / (true_positives + false_positives + false_negatives) if (true_positives + false_positives + false_negatives) > 0 else 0

    metrics = {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy 
    }

    logger.info(json.dumps(metrics, indent=4))
    logger.info("Metrics per paper: " + str(metrics_per_paper))


def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)

    

