
import click
from datetime import datetime

from app import db
from app.models import Papers
from . import construct_sparql_query, execute_query
from sqlalchemy import update

BATCH_SIZE = 1000

@click.command("makg:pull_paper_descriptions", help = "This command performs SPARQL query to MAKG to pull the abstract and title of papers pulled from AIDA")
def pull_paper_decriptions():
    click.echo("--- Started paper description import ---")
    iteration = 1
    while True:
        unprocessed_papers = get_papers_with_no_description_processed(BATCH_SIZE)
        
        makg_uris = [paper.makg_uri for paper in unprocessed_papers]
        if not makg_uris:
            print("No paper uri to pull description")
            break
            
        else: 
            query = make_query(makg_uris)
            response = execute_query(query)
            if response and response["results"]["bindings"]:
                papers_dict = {} # As same paper might have multiple title we want to prioritize the title based on length and insert that one into table
                for result in response["results"]["bindings"]:
                    paper_uri = result["paper"]["value"]
                    title = result["title"]["value"]
                    abstract = result["abstract"]["value"]
                    pub_date = result["pub_date"]["value"]
                    # check if the paper already exits in the dictionary
                    if paper_uri not in papers_dict or len(title) > len(papers_dict[paper_uri]["title"]):
                        papers_dict[paper_uri] = {
                                'title': title,
                                'abstract': abstract,
                                'pub_date': pub_date
                        }
                
                for paper in unprocessed_papers:
                    # First the makg_uri stored in table should be converted to https
                    # This way only we could get the description from MAKG
                    paper_update_data = papers_dict.get(convert_http_to_https(paper.makg_uri))
                    if paper_update_data: 
                        paper.title = paper_update_data.get('title')
                        paper.abstract = paper_update_data.get('abstract')
                        paper.publication_date = paper_update_data.get('pub_date')
                    else:
                        print('no descriptino')
                    paper.is_desc_pulled = True

                db.session.commit() 
                print(f"Done updating paper of batch{BATCH_SIZE * iteration}")
            else:
                print("No more results !!")
                break
        iteration += 1

def make_query(makg_uris):
    # Constructing the FILTER clause with the resource URLs
    # filter_query = " || ".join(f"?paper = <{url}>" for url in makg_uris)
    # filter_query = f"FILTER ({filter_query})"  # Wrap the conditions with 
    filter_query = f"FILTER (?paper IN ({', '.join(['<' + convert_http_to_https(url) + '>' for url in makg_uris])}))"


    return construct_sparql_query(f"""
        SELECT DISTINCT ?paper ?title ?abstract ?pub_date
        WHERE {{
            ?paper rdf:type magc:Paper .
            ?paper dcterms:title ?title .
            ?paper dcterms:abstract ?abstract .
            ?paper prism:publicationDate ?pub_date .
            {filter_query}
        }} 
    """)

def convert_http_to_https(url):
    if url.startswith("http://"):
        return "https://" + url[7:]
    else:
        return url    

def get_papers_with_no_description_processed(batch_size):
    return Papers.query.filter(
            Papers.is_desc_pulled == False, 
            Papers.makg_uri != None
        ).limit(batch_size).all()


def write_no_desc_paper_to_file(list):
    file_name = "no_desc_papers_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    # Write the list to a file
    with open(file_name, 'w') as file:
        for item in list:
            file.write(item + "\n")

    print(f"List saved in file: {file_name}")
