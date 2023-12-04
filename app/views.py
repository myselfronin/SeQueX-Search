from app import app
from flask import request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from app.services.ner import NamedEntityRecognition
import spacy
import os
class SearchForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired()])


@app.route("/", methods=["GET"])
def index():
    form = SearchForm()
    return render_template("home.html", form=form)

@app.route("/", methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        ner = NamedEntityRecognition()
        
        entities = ner.get_entities(query)
        for ent in entities:
            print(ent)
        # print(os.path.exists('storage/model-best'))
        # nlp = spacy.load('storage/model-best')
        # doc = nlp(query)
        # for ent in doc.ents:
        #     print(f"- {ent.text} ({ent.label_})")
        # print(f"User query: {query}")
        return f'Searching for: {query}'
    else:
        return render_template("home.html", form=form)
