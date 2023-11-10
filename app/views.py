from app import app
from flask import request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

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
        print(f"User query: {query}")
        return f'Searching for: {query}'
    else:
        return render_template("home.html", form=form)
