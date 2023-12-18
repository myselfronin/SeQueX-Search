from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSimilarity:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def cosine_similarity(self, text1, text2):
        """
        Calculate the cosine similarity between two texts.
        
        :param text1: The first text
        :param text2: The second text
        :return: The cosine similarity score
        """
        # Convert the texts into TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform([text1, text2])

        # Compute and return the cosine similarity
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
