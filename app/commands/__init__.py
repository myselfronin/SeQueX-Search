from .aida.pull_cs_papers import pull_cs_papers
from .makg.pull_paper_descriptions import pull_paper_decriptions
from .aida.pull_paper_topics import pull_paper_topics
from .make_annotated_dataset import make_annotated_dataset
from .solr.index_cso_topics import solr_index_topics
from .solr.solr_index_publications import solr_index_papers
from .solr.index_evaluation_papers import solr_index_evaluation_paper_from_gold_dataset
from .topic.add_topics_from_cso import add_topics_from_cso
from .topic.get_dbpedia_link import get_dbpedia_link
from .topic.pull_topic_description_from_dbpedia import pull_topic_description_from_dbpedia
from .make_bio_tagged_dataset import make_bio_tagged_dataset
from .evaluation.expansion_term_evaluation import evaluate_expansion_terms
from .evaluation.ner_evaluation import evaluate_named_entity_recognition
from .evaluation.ned_evaluation import evaluate_named_entity_disambiguation
from .evaluation.update_gold_standard_dataset import update_gold_standard_dataset
from .evaluation.linking_precision_evaluation import evaluate_linking_precision
from .evaluation.retrieval_evaluation import evaluate_retrieval
from .download_cso_ner_model import download_cso_ner_model

def register_commands(app):
    app.cli.add_command(pull_cs_papers)
    app.cli.add_command(pull_paper_decriptions)
    app.cli.add_command(pull_paper_topics)
    app.cli.add_command(make_annotated_dataset)
    app.cli.add_command(solr_index_topics)
    app.cli.add_command(solr_index_papers)
    app.cli.add_command(add_topics_from_cso)
    app.cli.add_command(get_dbpedia_link)
    app.cli.add_command(pull_topic_description_from_dbpedia)
    app.cli.add_command(make_bio_tagged_dataset)
    app.cli.add_command(solr_index_evaluation_paper_from_gold_dataset)
    app.cli.add_command(evaluate_expansion_terms)
    app.cli.add_command(evaluate_named_entity_recognition)
    app.cli.add_command(evaluate_named_entity_disambiguation)
    app.cli.add_command(update_gold_standard_dataset)
    app.cli.add_command(evaluate_linking_precision)
    app.cli.add_command(evaluate_retrieval)
    app.cli.add_command(download_cso_ner_model)
