from .lexical import LexicalNER
from .ngrams import NGramNER
from app.services.cso_ner import CSONER

class NamedEntityRecognition:
    def __init__(self):
        self.cso_ner = CSONER()

    def get_entities(self, text):
        lexical_ne = LexicalNER(text).get_entities()
        ngram_ne, corrected_dict = NGramNER(text).get_entities()
        model_ne = self.cso_ner.query(text)
        #model_ne = ModelNER(text).get_entities()
        return set(ngram_ne + lexical_ne + model_ne), corrected_dict