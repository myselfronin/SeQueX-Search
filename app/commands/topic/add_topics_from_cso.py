import click

from app import db
from app.services.cso import CSOQueryService
from app.models import Topics

@click.command("topic:add_from_cso")
def add_topics_from_cso():

    # Check if the topics table already has data or not
    if Topics.query.first():
        print("Topic table already have data hence halting process")
        return
    
    click.echo("Adding CSO topics to solr...")

    topics = CSOQueryService().get_topics_from_cso_with_dbpedia_uri()

    for uri, topic_info in topics.items():
        # Extract label and DBpedia URI from the topic_info dictionary
        label = topic_info['label']
        dbpedia_uri = topic_info['dbpedia_uri']

        # Create a new Topic instance for each topic
        new_topic = Topics(cso_uri=uri, label=label, dbpedia_uri=dbpedia_uri)

        # Add the new topic to the session
        db.session.add(new_topic)

    # Commit the session to save all new topics to the database
    try:
        db.session.commit()
        click.echo("Topics successfully added to the database.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"An error occurred: {e}")

    