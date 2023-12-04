from app import app
from flask import request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired
from app.services.ner import NamedEntityRecognition
import spacy
import os
class SearchForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired()])
    search_option = RadioField('Search Option', choices=[('sqe', 'Semantic Query Expansion'), ('keyword', 'Keyword based')], default='sqe', validators=[DataRequired()])


@app.route("/", methods=["GET"])
def index():
    form = SearchForm()
    return render_template("home.html", form=form)

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", form=form)

@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search_option.data)
        query = form.query.data
        ner = NamedEntityRecognition()

        entities = ner.get_entities(query)
        for ent in entities:
            print(ent)
        
        return render_template("search.html", form=form)
    else:
        return render_template("home.html", form=form)
