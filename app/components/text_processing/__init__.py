import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from app import logger

class TextProcessor:
    def __init__(self):
        # Ensure NLTK resources are available
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')

        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def preprocess(self, text):
        """Performs tokenization, stop word removal, and lemmatization on the input text."""
        tokens = self.tokenize(text)
        tokens_no_stop = self.remove_stop_words(tokens)
        lemmatized_tokens = self.lemmatize(tokens_no_stop)

        processed_query = " ".join(lemmatized_tokens)
        
        #--------
        logger.info('Processed Query: ' + processed_query)
        #--------

        return processed_query

    def tokenize(self, text):
        """Tokenizes the input text into words."""
        return word_tokenize(text)

    def remove_stop_words(self, tokens):
        """Removes stop words from the list of tokens."""
        return [word for word in tokens if word not in self.stop_words]

    def stem(self, tokens):
        """Applies stemming to the list of tokens."""
        return [self.stemmer.stem(word) for word in tokens]

    def lemmatize(self, tokens):
        """Applies lemmatization to the list of tokens."""
        return [self.lemmatizer.lemmatize(word) for word in tokens]