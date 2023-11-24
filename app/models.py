from . import db
from datetime import datetime

# Paper Resources from Knowledge Graph to store the URL of the 
# paper and status indicating the processed to import data into 
# publications table or not
class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    processed = db.Column(db.Boolean, default=False)


# Publication data with title, abstract and publishedDate
class Publications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    published_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)