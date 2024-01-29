import json
import click
from app import logger
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator
from app.components.query_expansion import QueryExpansion

GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandard.json'

@click.command("evaluate:expansion_terms", help = "Evaluates the expansion term wrt GoldStandard Dataset")
def evaluate_expansion_terms():
    try:
        logger.info("\n\n\n#########################################################################################\nEvaluating Expansion terms with distil bert cosine similarity having threshold of 0.85 in unprocessed text.1\n#########################################################################################\n\n\n")
        true_positives = 0
        false_positives = 0
        false_negatives = 0 
        count = 1
        gold_dataset = load_dataset()
        metrics_per_paper = []
        for paper_id, paper_data in gold_dataset.items():
            print(count)
            logger.info("Evaluation paper id: " + str(paper_id))
            gold_topics = set(paper_data["gold_standard"]["majority_vote"])

            expanded_terms = get_expansion_terms(paper_data["title"]+ " " + paper_data["abstract"])
            all_expansion_terms = set() # Collection of recognized entities with its expansion terms

            generated_expansion_term_count = 0

            for key, values in expanded_terms.items():
                all_expansion_terms.add(key)
                all_expansion_terms.update(values)
                generated_expansion_term_count += len(values)

            logger.info("Gold Standard Topics: " + ", ".join(gold_topics))
            logger.info("QES Topics: " + ", ".join(all_expansion_terms))

            logger.info("Number of expansion terms: " + str(generated_expansion_term_count))

            true_positives_of_paper = len(gold_topics.intersection(all_expansion_terms))
            false_positives_of_paper = len(all_expansion_terms - gold_topics)
            false_negatives_of_paper = len(gold_topics - all_expansion_terms)
            
            logger.info("TP: " + str(true_positives_of_paper) + ", FP: " + str(false_positives_of_paper) + ", FN: " + str(false_negatives_of_paper))
            

            # Add metrics for this paper to the list
            metrics_per_paper.append((true_positives_of_paper, false_positives_of_paper, false_negatives_of_paper, generated_expansion_term_count))

            true_positives += true_positives_of_paper
            false_positives += false_positives_of_paper
            false_negatives += false_negatives_of_paper

            count+=1

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics =  {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

        logger.info(json.dumps(metrics, indent=4))
        
        # Log metrics for each paper
        logger.info("Metrics per paper: " + str(metrics_per_paper))

    except Exception as e:
        print(e)

def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)
    
def get_expansion_terms(text):
     ### Preprocess Query ###
    processed_query = TextProcessor().preprocess(text)
    
    ### Named Entity Disambiguation ###
    linked_entities = NamedEntityDisambiguator(processed_query).get_linked_entities()
    ### Query Expansion ###
    expanded_entities = QueryExpansion(linked_entities, text).get_expanded_entities()

    return expanded_entities
    
