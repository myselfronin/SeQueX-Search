from .aida.pull_cs_papers import pull_cs_papers
from .makg.pull_paper_descriptions import pull_paper_decriptions
from .aida.pull_paper_syntactic_topics import pull_paper_syntactic_topics


def register_commands(app):
    app.cli.add_command(pull_cs_papers)
    app.cli.add_command(pull_paper_decriptions)
    app.cli.add_command(pull_paper_syntactic_topics)
