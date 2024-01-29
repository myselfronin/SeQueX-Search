from Levenshtein import distance as levenshtein_distance
from app.services.solr import SolrService

LEVENSTEIN_DISTANCE_THRESHOLD = 1
class NGramNER():
    def __init__(self, text):
        self.text = text
        self.solr_service = SolrService()

    def get_entities(self):
        unigrams = self.generate_ngrams(1)
        bigrams = self.generate_ngrams(2)
        trigrams = self.generate_ngrams(3)

        # Union of all the ngram sets 
        ngrams = list(unigrams | bigrams | trigrams)

        # Get all possible topic from solr index
        possible_topics = [item['topic'][0] for item in self.solr_service.get_topic_matches(ngrams) if 'topic' in item and item['topic']]

        # Match the ngrams with possibel topic to recognize possible topic entities
        # Exact match and Levenshtein distance
        matched_entities = []
        for ngram in ngrams:
            for topic in possible_topics:
                if self.is_close_match(ngram, topic, threshold=LEVENSTEIN_DISTANCE_THRESHOLD):
                    matched_entities.append(topic)

                    break  # Stop checking other topics if a match is found


        return matched_entities
    

    def generate_ngrams(self, n):
        words = self.text.split()
        ngrams = zip(*[words[i:] for i in range(n)])
        return set([" ".join(ngram) for ngram in ngrams])
    

    def is_close_match(self, str1, str2, threshold):
        """
        Determine if two strings are a close match based on Levenshtein distance.

        :param str1: First string.
        :param str2: Second string.
        :param threshold: Maximum Levenshtein distance to be considered a close match.
        :return: True if close match, False otherwise.
        """
        return levenshtein_distance(str1, str2) <= threshold
    

    