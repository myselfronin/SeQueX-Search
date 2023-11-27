import click

from app import db
from app.models import Papers
from . import construct_sparql_query, execute_query

MAX_PAPERS = 200000 # How many papers should be pulled in total
BATCH_SIZE = 10000

@click.command("aida:pull_cs_papers", help = "This command performs SPARQL query to AIDA KG to pull CS papers and store in DB. The limit is 10000 papers and the offset will start from count in the table so as to pull new paper every time command runs")
def pull_cs_papers():
    click.echo("--- Started paper resources import ---")
    print("Counting total papers in database...")

    # Count resources in the databse
    total_papers = Papers.query.count()
    print(f"Total papers: {total_papers}. Hence now pulling from offset {total_papers} and limit {BATCH_SIZE}")

    offset = total_papers
    limit = BATCH_SIZE

    while True:
        if offset >= MAX_PAPERS:
            print("Reached maximum paper. Pulling Stopped !!")
            break

        print(f"Querying AIDA with limit {limit} and offset {offset}")

        query = make_query(limit, offset)
        response = execute_query(query)

        if response and response["results"]["bindings"]:
            new_papers = [
                Papers(
                    aida_uri=result['aida_uri']['value'], 
                    makg_uri=result['makg_uri']['value'] if 'makg_uri' in result else None
                )
                for result in response["results"]["bindings"]
            ]

            # Add all new papers to the session
            db.session.add_all(new_papers)
            db.session.commit()

            print("Inserted to db")   

        else:
            print("No more results !!")
            break

        offset += limit
        

def make_query(limit, offset):
    return construct_sparql_query(f"""
        SELECT ?aida_uri ?makg_uri 
        FROM <http://aida.kmi.open.ac.uk/resource> 
        WHERE {{ 
            ?aida_uri rdf:type aida:paper .
            ?aida_uri owl:sameAs ?makg_uri .
        }} LIMIT {str(limit)} OFFSET { str(offset)}
    """)


def create_paper(aida_uri, makg_uri):
    Papers(aida_uri = aida_uri, makg_uri = makg_uri)