from app import app
from flask import request, render_template, Response
from app.services.solr import SolrService
from app.components.text_processing import TextProcessor
from app.components.named_entity_disambiguation import NamedEntityDisambiguator
from app.components.query_expansion import QueryExpansion
from app import logger
import time
import os

PAGE_SIZE = 10
PATH_TO_LOG_FILE = os.path.join(app.root_path, '../myapp.log')

@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")

@app.route("/search", methods=["GET"])
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    search_option = request.args.get('search_option', 'sqe') 
    start = (page - 1) * PAGE_SIZE 

    process_start_time = time.time()
    # SQE based search
    if search_option == 'sqe':
        #--------
        logger.info('\n\n\n\nSQE SEARCH')
        logger.info('Query Text: '+ query)
        #--------

        ### Preprocess Query ###
        processed_query = TextProcessor().preprocess(query)

        ### Named Entity Disambiguation ###
        linked_entities = NamedEntityDisambiguator(processed_query).get_linked_entities()

        ### Query Expansion ###
        expanded_entities = QueryExpansion(linked_entities, processed_query).get_expanded_entities()
    
        #Search in Solr
        results = semantic_search(expanded_entities, start=start)

        process_taken_time = time.time() - process_start_time

        return render_template("search.html", documents=results['documents'], total_results=results['total_results'], time_taken=results['time_taken'], page=1, query=query, search_option=search_option,process_time = process_taken_time)
    
    else: 
        # Keyword based search
        results = keyword_search(query, start=start)

        process_taken_time = time.time() - process_start_time
        return render_template("search.html", documents=results['documents'], total_results=results['total_results'], time_taken=results['time_taken'], page=page, query=query, search_option=search_option, process_time = process_taken_time)

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/stream-logs')
def stream_logs():
    return Response(read_log_file(), mimetype='text/event-stream')

def keyword_search(query, start=0, rows=PAGE_SIZE):
    processed_query = TextProcessor().preprocess(query)
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

    solr_query = solr_service.make_query_for_expanded_entities(entities)
    logger.info("Formulated Query: " + solr_query)
   
    # Execute the query in the solr engine
    results = solr_service.get_paper_matches(solr_query, start=start, rows=rows)

    return results


def read_log_file():
    with open(PATH_TO_LOG_FILE, "r") as log:
        log.seek(0, os.SEEK_END)  # Move to the end of the file
        while True:
            line = log.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly
                continue
            yield f"data: {line}\n\n"


    