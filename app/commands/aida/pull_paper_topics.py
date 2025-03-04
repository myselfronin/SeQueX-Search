import click

from app import db
from app.models import Papers
from . import construct_sparql_query, execute_query

BATCH_SIZE = 1000

@click.command("aida:pull_paper_topics")
def pull_paper_topics():
    try:
        click.echo("Pulling topic labels of CS papers...")
        iteration = 1
        
        while True:
            print(iteration)
            # Get paper for which labels has not been retrieved yet
            papers = get_papers_with_no_syntactic_labels_processed(BATCH_SIZE)
            # Break the loop if no any paper left to pull labels
            if not papers: 
                break

            # Extract URLs of the resource of papers
            paper_uris = [paper.aida_uri for paper in papers]

            result = query_aida_for_topic_labels_for_given_paper_uris(paper_uris)
            if result:
                uri_topics = {
                    r['paper']['value']:  { 
                        'syntactic_topics': r['syntacticLabels']['value'].split(',') if 'value' in r['syntacticLabels'] else [], 
                        'semantic_topics': r['semanticLabels']['value'].split(',') if 'value' in r['semanticLabels'] else []
                    }
                    for r in result
                }
                
                #Update each paper in the list
                for paper in papers:
                    topics = uri_topics.get(paper.aida_uri)
                    if topics: 
                        paper.syntactic_topics = topics.get('syntactic_topics')
                        paper.semantic_topics = topics.get('semantic_topics')
                    
                    paper.syntactic_topic_pulled = True
                # Commit the changes in the database
                db.session.commit()

            else:
                print("No results found from SPARQL query.")
            
            print(f"Number of paper processed: {iteration * BATCH_SIZE}")
            iteration += 1 # Increment the iteration
            
    except Exception as e:
        print(str(e))


def get_papers_with_no_syntactic_labels_processed(batch_size):
    return Papers.query.filter(Papers.syntactic_topic_pulled == False).limit(batch_size).all()


def query_aida_for_topic_labels_for_given_paper_uris(makg_uris):
    # Constructing the FILTER clause with the resource URLs
    filter_query = f"FILTER (?paper IN ({', '.join(['<' + paper + '>' for paper in makg_uris])}))"

    query = construct_sparql_query(f"""
        SELECT ?paper (GROUP_CONCAT(?syntacticTopicLabel; SEPARATOR=",") AS ?syntacticLabels) (GROUP_CONCAT(?semanticTopicLabel; SEPARATOR=",") AS ?semanticLabels)
        FROM <http://aida.kmi.open.ac.uk/resource> 
        WHERE {{ 
        ?paper rdf:type aida:paper .
        ?paper aida:hasSyntacticTopic ?syntacticTopic .
        ?paper aida:hasSemanticTopic ?semanticTopic .
        ?syntacticTopic rdfs:label ?syntacticTopicLabel .
        ?semanticTopic rdfs:label ?semanticTopicLabel .
        {filter_query}
        }}
        GROUP BY ?paper 
    """)

    response = execute_query(query)

    if response and response['results']['bindings']:
        return response['results']['bindings']
    else:
        return None

