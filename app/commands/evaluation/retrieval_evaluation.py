import json
import click
from app.services.cso_query import CSOQueryService
from app.services.solr import SolrService
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator
from app.components.query_expansion import QueryExpansion
from app import logger

GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandardUpdated.json'
SOLR_RESPONSE_SIZE = 70

@click.command("evaluate:retrieval", help="Evaluate the retrieval both keyword based and SQE based")
def evaluate_retrieval():
    gold_dataset = load_dataset()

    keyword_based_metrics = []
    sqe_based_metrics = []

    count = 0
    # Keyword Search
    logger.info("\n\nEvalution of keyword-based search")
    for paper_id, paper_data in gold_dataset.items():
        count += 1
        print(count)
        relevant_papers_with_score = paper_data["relevant_papers"]

        keyword_results = keyword_search(paper_data)
        keyword_retrieved_papers = keyword_results['documents']

        keyword_metrics = evaluate_metrics(keyword_retrieved_papers, relevant_papers_with_score)
        keyword_based_metrics.append(keyword_metrics)
    
    # Calculate average metric
    avg_keyword_metrics = calculate_average_metrics(keyword_based_metrics)

    average_keyword_metrics = {
        "precision": avg_keyword_metrics[0],
        "recall": avg_keyword_metrics[1],
        "f1score": avg_keyword_metrics[2],
    }

    logger.info(str(keyword_based_metrics))
    logger.info("Average Evaluation: \n" + json.dumps(average_keyword_metrics, indent=4))
    
    # SQE Search
    count = 0
    logger.info("\n\nEvalution of SQE-based search")
    for paper_id, paper_data in gold_dataset.items():
        count += 1
        print(count)
        relevant_papers_with_score = paper_data["relevant_papers"]
        sqe_results = sqe_search(paper_data)
        sqe_retrieved_papers = sqe_results['documents']

        sqe_metrics = evaluate_metrics(sqe_retrieved_papers, relevant_papers_with_score)
        
        sqe_based_metrics.append(sqe_metrics)


    # Calculate average metrics
    avg_sqe_metrics = calculate_average_metrics(sqe_based_metrics)

    average_sqe_metrics = {
        "precision": avg_sqe_metrics[0],
        "recall": avg_sqe_metrics[1],
        "f1score": avg_sqe_metrics[2],
    }
    logger.info(str(sqe_based_metrics))
    logger.info("Average Evaluation: \n" + json.dumps(average_sqe_metrics, indent=4))


def evaluate_metrics(retrieved_papers, relevant_papers):
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    retrieved_paper_dois = {paper["doi"] for paper in retrieved_papers}
    for doi, score in relevant_papers.items():
        if doi in retrieved_paper_dois:
            true_positives += 1
        else:
            false_negatives += 1

    false_positives = len(retrieved_paper_dois) - true_positives

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return precision, recall, f1_score

def calculate_average_metrics(metrics_list):
    sum_precision = sum_recall = sum_f1 = 0
    count = len(metrics_list)

    for precision, recall, f1_score in metrics_list:
        sum_precision += precision
        sum_recall += recall
        sum_f1 += f1_score

    avg_precision = sum_precision / count if count > 0 else 0
    avg_recall = sum_recall / count if count > 0 else 0
    avg_f1 = sum_f1 / count if count > 0 else 0

    return avg_precision, avg_recall, avg_f1

def sqe_search(paper_data):
    query = paper_data["title"] 

    ### Preprocess Query ###
    processed_query = TextProcessor().preprocess(query)

    ### Named Entity Disambiguation ###
    linked_entities = NamedEntityDisambiguator(processed_query).get_linked_entities()

    ### Query Expansion ###
    expanded_entities = QueryExpansion(linked_entities, query).get_expanded_entities()

    #Search in Solr
    solr_service = SolrService()

    solr_query = solr_service.make_query_for_expanded_entities(expanded_entities)
   
    # Execute the query in the solr engine
    results = solr_service.get_paper_matches(solr_query, start=0, rows=SOLR_RESPONSE_SIZE)

    return results

def keyword_search(paper_data):
    query = paper_data["title"]

    solr_service = SolrService()

    # Construct solr query to search from title
    solr_query = solr_service.make_keyword_based_query(query)

    # Execute the query in the solr engine
    results = solr_service.get_paper_matches(solr_query, start=0, rows=SOLR_RESPONSE_SIZE)
    
    return results

def calculate_relevancy_score(retrieved_keywords, majority_vote_keywords):
    # Normalize keywords to lowercase
    normalized_retrieved_keywords = {keyword.lower() for keyword in retrieved_keywords}
    normalized_majority_vote_keywords = {keyword.lower() for keyword in majority_vote_keywords}

    # Count the number of common keywords between retrieved and majority vote keywords
    common_keywords = normalized_retrieved_keywords & normalized_majority_vote_keywords
    return len(common_keywords)

def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)
    

    