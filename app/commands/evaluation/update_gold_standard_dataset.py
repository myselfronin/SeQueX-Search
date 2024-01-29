import json
import click
from app.services.cso_query import CSOQueryService


GOLD_STANDARD_DATASET_PATH = 'storage/GoldStandard.json'
def load_dataset():
    with open(GOLD_STANDARD_DATASET_PATH, 'r') as file:
        return json.load(file)
    
gold_dataset = load_dataset()

@click.command("evaluate:update_gold_standard_dataset", help = "Extract relevant data and also appends the topic URI that will be used in evaluating entity linking")

def update_gold_standard_dataset():
    processed_papers = {}
    count = 1
    for paper_id, paper_data in gold_dataset.items():
        print(count)
        extracted_data = extract_data(paper_data)
        processed_papers[paper_id] = extracted_data
        count += 1

    with open('storage/GoldStandardUpdated.json', 'w') as file:
        json.dump(processed_papers, file, indent=4)

    print("finished")

def extract_data(paper_data):
    topic_list = paper_data.get("topics", [])
    topic_uris = get_topic_uri_from_cso(topic_list)
    #Some of the topics might not have the URI in the CSO ontology. For those we just add empty string ""
    # Check if any label in the list is not in the dictionary keys
    missing_labels = any(label not in topic_uris for label in topic_list)

    # If there are missing labels, create a new dictionary
    if missing_labels:
        updated_dict = {label: topic_uris.get(label, "") for label in topic_list}
    else:
        updated_dict = topic_uris
    
    majority_voted_topics = paper_data.get("gold_standard", {}).get("majority_vote", [])

    return {
        "doi": paper_data.get("doi", ""),
        "title": paper_data.get("title", ""),
        "abstract": paper_data.get("abstract", ""),
        "topics": updated_dict,
        "majority_vote": majority_voted_topics, 
        "relevant_papers": get_relevant_papers_with_score(majority_voted_topics)
    }


    

def get_topic_uri_from_cso(topics):
    return CSOQueryService().get_uris_by_topic_labels(topics)

def get_relevant_papers_with_score(majority_voted_topics_in_query_paper):
    relevant_papers_with_score = {}
    for paper_id, paper_data in gold_dataset.items():
        majority_voted_topics_of_current_paper = paper_data.get("gold_standard", {}).get("majority_vote", [])
        relevancy_score = get_relevancy_score(majority_voted_topics_in_query_paper, majority_voted_topics_of_current_paper)

        if relevancy_score > 0:
            relevant_papers_with_score[paper_data.get("doi")] = relevancy_score

    return relevant_papers_with_score

def get_relevancy_score(majority_voted_topics_in_query_paper, majority_voted_topics_of_current_paper):
    # Normalize the topics of both papers
    normalized_topic_of_query_paper = set([topic.lower() for topic in majority_voted_topics_in_query_paper])
    normalized_topic_of_current_paper = set([topic.lower() for topic in majority_voted_topics_of_current_paper])

    # Calculate the relevancy score
    relevancy_score = len(normalized_topic_of_current_paper & normalized_topic_of_query_paper)

    return relevancy_score
