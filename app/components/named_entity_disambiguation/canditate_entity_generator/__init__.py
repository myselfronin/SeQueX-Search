from app.services.solr import SolrService

class CandidateEntityGenerator:
    def __init__(self, recognized_entities):
        self.recognized_entities = recognized_entities
        self.solr_service = SolrService()

    def get_candidates(self):
        candidate_sets_of_mentions = self.get_candidate_from_topic_indexes()

        return candidate_sets_of_mentions
    
    def get_candidate_from_topic_indexes(self):
        """
        Get candidate entities from the indexed topic in solr
        The candidate are fetched via exact match and Levenstein Edit Distance

        {
            "reg_ent_1" : {set of candidate entities for it}, 
            "reg_eng_2" : {set of candidate entities for it}
        }

        :return: Dictionary of recognized entities and their corresponding candidate topics
        """
        candidate_entities = {}
        for entity in self.recognized_entities:
            ngrams = set(entity.split())
            topics = {item['uri'][0] for item in self.solr_service.get_topic_matches(ngrams) if 'uri' in item and item['uri']} # set
            candidate_entities[entity] = topics

        return candidate_entities
    

