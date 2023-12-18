from app.services.solr import SolrService
from app.services.cso_query import get_topics_via_relations, get_topics_via_relations_test
from app import logger

class CandidateEntityGenerator:
    def __init__(self, recognized_ents):
        self.recognized_ents = recognized_ents
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
        for entity in self.recognized_ents:
            ngrams = set(entity.split())
            topics = {item['uri'][0] for item in self.solr_service.get_topic_matches(ngrams) if 'uri' in item and item['uri']} # set
            candidate_entities[entity] = topics

        return candidate_entities
    

    # def get_same_topic_from_cso(self):
    #     results = get_topics_via_relations(self.recognized_ents, ['owl#sameAs'])
    #     # results = get_topics_via_relations_test(self.recognized_ents, ["owl#sameAs", "skos#related"])

    #     return results
