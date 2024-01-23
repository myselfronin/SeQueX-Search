import nltk
import re

class LexicalNER:
    def __init__(self, text):
        self.text = text

    def get_entities(self):
        # Extract entities within quotes
        quoted_entities = self.extract_quoted_entities()

        #Extract entities with capitalized case
        capitalized_entities = self.extract_capitalized_entities()

        # All unique recognized entities
        unique_entities = set(quoted_entities + capitalized_entities)

        return list(unique_entities)

    def extract_quoted_entities(self):
        quoted_entities = re.findall(r'"(.*?)"', self.text)

        return quoted_entities

    def extract_capitalized_entities(self):
        # Tokenize the text
        tokens = nltk.word_tokenize(self.text)

        # Extract other entities based on capitalization
        return [token for token in tokens if token[0].isupper()]