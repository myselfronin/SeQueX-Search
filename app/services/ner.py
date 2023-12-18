from app.components.ner  import LexicalNER, NGramNER, ModelNER

class NamedEntityRecognition:
    def __init__(self):
        pass

    def get_entities(self, text):
        lexical_ne = LexicalNER(text).get_entities()
        ngram_ne, corrected_dict = NGramNER(text).get_entities()
        #model_ne = ModelNER(text).get_entities()
        return set(ngram_ne + lexical_ne), corrected_dict