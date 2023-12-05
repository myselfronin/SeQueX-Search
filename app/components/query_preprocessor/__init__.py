import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class QueryPreprocessor:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

    def preprocess(self, query):
        # Remove quote if exists any
        new_query = query.replace('"', '').replace("'", '')
        tokens = word_tokenize(new_query)
        filtered_tokens = [token.lower() for token in tokens if token.lower() not in self.stop_words]
        processed_query = ' '.join(filtered_tokens)
        return processed_query