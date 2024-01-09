from flask import current_app
import spacy
import os

class ModelNER:
    def __init__(self, text):
        self.text = text
        self.model_path = current_app.root_path + '/../storage/model-best'


    def get_entities(self):
        if(os.path.exists(self.model_path)):
            nlp = spacy.load('storage/model-best')
            doc = nlp(self.text)

            return doc.ents
        else:
            return []        