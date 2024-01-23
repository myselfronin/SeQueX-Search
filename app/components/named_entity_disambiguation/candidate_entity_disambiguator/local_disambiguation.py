from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein

class LocalDisambiguation:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def context_similarity(self, text1, text2):
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
    
    def entity_name_similarity(self, mention, candidate_label):
        """
        Calculate the normalized Levenshtein distance between two names.

        :param mention: The entity mention name.
        :param candidate_label: The candidate label name.

        :return: Normalized name distance score.
        """
        lev_distance = Levenshtein.distance(mention, candidate_label)
        max_length = max(len(mention), len(candidate_label))
        normalized_score = lev_distance / max_length if max_length != 0 else 0
        
        return 1 - normalized_score 
