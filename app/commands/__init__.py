from .aida.pull_cs_papers import pull_cs_papers
from .makg.pull_paper_descriptions import pull_paper_decriptions
from .aida.pull_paper_syntactic_topics import pull_paper_syntactic_topics
from .make_annotated_dataset import make_annotated_dataset
from .spacy.prepare_dataset import prepare_dataset
from .solr.index_cso_topics import solr_index_topics

def register_commands(app):
    app.cli.add_command(pull_cs_papers)
    app.cli.add_command(pull_paper_decriptions)
    app.cli.add_command(pull_paper_syntactic_topics)
    app.cli.add_command(make_annotated_dataset)
    app.cli.add_command(prepare_dataset)
    app.cli.add_command(solr_index_topics)
