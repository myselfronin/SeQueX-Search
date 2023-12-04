from app import app
from flask import request, render_template
from app.services.ner import NamedEntityRecognition
from app.services.solr import SolrService
from app.components.query_preprocessor import QueryPreprocessor
import spacy
import os

PAGE_SIZE=10

@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")

@app.route("/search", methods=["GET"])
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    search_option = request.args.get('search_option', 'sqe') 

    if search_option == 'sqe':
        # SQE based search
        ner = NamedEntityRecognition()

        entities = ner.get_entities(query)

        ner_highlighted_text = highlight_entities(query, entities)

        return render_template("search.html", documents=[], total_results=0, time_taken=0, page=1, query=query, search_option=search_option, ner_highlighted_text=ner_highlighted_text)
    
    else: 
        # Keyword based search
        start = (page - 1) * PAGE_SIZE  # Assuming 10 results per page
        results = keyword_search(query, start=start)
        total_results = results['total_results']
        time_taken = results['time_taken']
        documents = results['documents']

        return render_template("search.html", documents=documents, total_results=total_results, time_taken=time_taken, page=page, query=query, search_option=search_option)
        

def keyword_search(query, start=0, rows=PAGE_SIZE):
    processed_query = QueryPreprocessor().preprocess(query)
    keywords = processed_query.split()

    solr_service = SolrService()

    # Construct solr query to search in abstract and title
    solr_query = solr_service.make_keyword_based_query(keywords)
    print(solr_query)

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