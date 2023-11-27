from .aida.pull_cs_papers import pull_cs_papers
from .makg.pull_paper_descriptions import pull_paper_decriptions

def register_commands(app):
    app.cli.add_command(pull_cs_papers)
    app.cli.add_command(pull_paper_decriptions)
