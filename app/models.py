from . import db
from datetime import datetime
from sqlalchemy import ARRAY

class Papers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aida_uri = db.Column(db.String, nullable=False, unique=True)
    makg_uri = db.Column(db.String, nullable=True)
    is_desc_pulled = db.Column(
        db.Boolean, default=False, 
        info={'description': 'Flag to denote whether the description of the paper from MAKG has been pulled or not'}) 
    title = db.Column(db.String, nullable=True)
    abstract = db.Column(db.Text, nullable=True)
    doi = db.Column(db.String, nullable=True)
    publication_date = db.Column(db.String, nullable=True)
    syntactic_topic_pulled = db.Column(
        db.Boolean, default=False,
        info={'description': 'Flag to denote whether the Syntactic Topic labels from AIDA KG has been pulled or not '}
    )
    syntactic_topics = db.Column(
        ARRAY(db.String), nullable=True,
        info={'description': 'Syntactic Topic (a CSO Topic) labels of the paper from the AIDA KG'}
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Topics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cso_uri = db.Column(db.String, nullable=False, unique=True)
    label = db.Column(db.String)
    dbpedia_uri = db.Column(db.String)
    description_pulled = db.Column(db.Boolean, default=False, info={'description': 'Flag to denote whether the description from DBpedia has been pulled or not'})
    description = db.Column(db.Text, nullable=True)
