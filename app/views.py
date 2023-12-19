from app import app
from flask import request, render_template
from app.components.ner import NamedEntityRecognition
from app.services.solr import SolrService
from app.components.query_preprocessor import QueryPreprocessor
from app.components.canditate_entity_generator import CandidateEntityGenerator
from app.components.candidate_entity_disambiguation import CandidateDisambiguator
from app.components.query_expansion import QueryExpansion
from app import logger

PAGE_SIZE=10

@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    search_option = request.args.get('search_option', 'sqe') 
    start = (page - 1) * PAGE_SIZE 

    # SQE based search
    if search_option == 'sqe':
        #--------
        logger.info('\n\n\n\nSQE SEARCH')
        logger.info('Query Text: '+ query)
        #--------

        ### Preprocess Query ###
        processed_query = QueryPreprocessor().preprocess(query)

        #--------
        logger.info('Processed Query: ' + processed_query)
        #--------

        ### Named Entity Recognition ###
        ner = NamedEntityRecognition()
        entities, corrected_dict = ner.get_entities(processed_query)
       
        ### Corrected query spelling if any found ###
        corrected_query = replace_corrected_entities(query, corrected_dict)
        ner_highlighted_text = highlight_entities(corrected_query, entities)

        #--------
        logger.info('Recognized Entities: ' + ', '.join(entities))
        logger.info('Corrected query: ' + corrected_query)
        #--------

        ### Candidate Generation ###
        reg_mentions_candidate_set = CandidateEntityGenerator(entities).get_candidates()

        #--------
        log_candidates_set(reg_mentions_candidate_set)
        #--------

        ### Entity Diambiguation ###
        disambiguator = CandidateDisambiguator(corrected_query, reg_mentions_candidate_set)
        linked_entities = { mention: disambiguator.disambiguate(mention) for mention in reg_mentions_candidate_set}

        #--------
        formatted_pairs = [f"Entity Linking: '{key}': {value}" for key, value in linked_entities.items()]
        logger.info('\n' + '\n'.join(formatted_pairs))
        #--------

        ### Query Expansion ###
        expanded_keywords = QueryExpansion(linked_entities).get_expanded_entities()
        #--------
        log_expanded_keywords(expanded_keywords)
        #--------

        return 'hi'
        #Search in Solr
        results = semantic_search(candidate_entities, start=start)


        return render_template("search.html", documents=results['documents'], total_results=results['total_results'], time_taken=results['time_taken'], page=1, query=query, search_option=search_option, ner_highlighted_text=ner_highlighted_text, recognized_entities=entities, candidate_entities=candidate_entities)
    
    else: 
        # Keyword based search
        results = keyword_search(query, start=start)

        return render_template("search.html", documents=results['documents'], total_results=results['total_results'], time_taken=results['time_taken'], page=page, query=query, search_option=search_option)
        

def keyword_search(query, start=0, rows=PAGE_SIZE):
    processed_query = QueryPreprocessor().preprocess(query)
    keywords = processed_query.split()

    solr_service = SolrService()

    # Construct solr query to search in abstract and title
    solr_query = solr_service.make_keyword_based_query(keywords)

    # Execute the query in the solr engine
    results = solr_service.get_paper_matches(solr_query, start=start, rows=rows)

    return results

def semantic_search(entities, start=0, rows=PAGE_SIZE):
    # Construct solr query to search in abstract and title
    solr_service = SolrService()

    solr_query = solr_service.make_keyword_based_query(entities)

    # Execute the query in the solr engine
    results = solr_service.get_paper_matches(solr_query, start=start, rows=rows)

    return results

def highlight_entities(text, entities):
    """
    Generates HTML with recognized entities highlighted.

    :param text: Original text
    :param entities: List of entities to highlight
    :return: HTML with highlighted entities
    """
    for entity in entities:
        highlighted = f"<span style='background-color: #3a9c8b; color: white;'>{entity}</span>"
        text = text.replace(entity, highlighted)

    return text

def replace_corrected_entities(query, corrected_dict):
    """
    Replace incorrect spellings in the query with their corrected forms.

    :param query: The original query string.
    :param corrected_dict: Dictionary of incorrect spellings and their corrections.
    :return: Updated query with corrected spellings.
    """
    for incorrect, corrected in corrected_dict.items():
        query = query.replace(incorrect, corrected)
    return query


def log_candidates_set(candidate_set):
    # Create a list of formatted strings
    formatted_entries = [f"Recognized Entity: '{entity}', Candidate Entities: {', '.join(candidates)}" 
                        for entity, candidates in candidate_set.items()]
    # Join the formatted strings and log them
    logger.info('\n'.join(formatted_entries))

def log_expanded_keywords(expanded_keywords):
    for entity_label, relations in expanded_keywords.items():
        logger.info(f"Entity: {entity_label}")
        for relation_type, uris in relations.items():
            uris_str = ', '.join(uris)
            logger.info(f"\t{relation_type}: {uris_str}")
    