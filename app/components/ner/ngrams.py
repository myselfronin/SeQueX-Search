from app.services.solr import SolrService

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
        matched_entities = list(filter(lambda item: item in possible_topics, ngrams))

        return matched_entities
    

    def generate_ngrams(self, n):
        words = self.text.split()
        ngrams = zip(*[words[i:] for i in range(n)])
        return set([" ".join(ngram) for ngram in ngrams])
    

    