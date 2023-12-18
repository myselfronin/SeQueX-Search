from .aida.pull_cs_papers import pull_cs_papers
from .makg.pull_paper_descriptions import pull_paper_decriptions
from .aida.pull_paper_syntactic_topics import pull_paper_syntactic_topics
from .make_annotated_dataset import make_annotated_dataset
from .spacy.prepare_dataset import prepare_dataset
from .solr.index_cso_topics import solr_index_topics
from .solr.solr_index_publications import solr_index_papers
from .topic.add_topics_from_cso import add_topics_from_cso
from .topic.pull_topic_description_from_dbpedia import pull_topic_description_from_dbpedia
from .make_bio_tagged_dataset import make_bio_tagged_dataset

def register_commands(app):
    app.cli.add_command(pull_cs_papers)
    app.cli.add_command(pull_paper_decriptions)
    app.cli.add_command(pull_paper_syntactic_topics)
    app.cli.add_command(make_annotated_dataset)
    app.cli.add_command(prepare_dataset)
    app.cli.add_command(solr_index_topics)
    app.cli.add_command(solr_index_papers)
    app.cli.add_command(add_topics_from_cso)
    app.cli.add_command(pull_topic_description_from_dbpedia)
    app.cli.add_command(make_bio_tagged_dataset)
