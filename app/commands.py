import click
from app import app
# import requests
# import psycopg2

@app.cli.command('pull-data-from-')
def fetch_and_store_data():
    click.echo("Fetching data from API...")
    # data = get_data_from_api()
    # if data:
    #     click.echo("Storing data to database...")
    #     insert_into_data(data)
    #     click.echo("Data fetched and stored successfully.")
    # else:
    #     click.echo("Failed to fetch data")


@app.cli.command('add-papers-from-json')
def add_papers_from_json():
    click.echo("Importing paper resoure json data in database")



def load_json(filePath):
    with open(filePath, 'r') as file:
        return json.load(file)