from app.services.solr import SolrService

class CandidateEntityGenerator:
    def __init__(self, recognized_ents):
        self.recognized_ents = recognized_ents
        self.solr_service = SolrService()

    
    def get_candidate_from_topic_indexes(self):
        """
        Get candidate entities from the indexed topic in solr
        The candidate are fetched via exact match and Levenstein Edit Distance

        :return: Set of candidate entities
        """
        ngrams = set()
        for entity in self.recognized_ents:
            ngrams.update(entity.split())
        
        candidate_entities = [item['topic'][0] for item in self.solr_service.get_topic_matches(ngrams) if 'topic' in item and item['topic']]

        return candidate_entities

    
    