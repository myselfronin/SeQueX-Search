from app.services.cso import CSOQueryService

class QueryExpansion:
    def __init__(self, linked_entities):
        self.cso_query_service = CSOQueryService() 
        self.linked_entities = linked_entities
    
    def get_expanded_entities(self):
        """
        Fetches expanded entities for each linked entity.

        :return: A dictionary where each key is an entity label and the value is a dictionary of expansion terms.
        """
        expanded_entities = {}
        for entity_label, entity_uri in self.linked_entities.items():
            expansion_terms = self.get_ranked_expansion_term(entity_uri)
            expanded_entities[entity_label] = expansion_terms

        return expanded_entities
    
    def get_ranked_expansion_term(self, topic_uri):
        """
        Fetches and ranks expansion terms for a given topic URI.

        :param topic_uri: URI of the topic for which to find expansion terms.
        :return: A dictionary of ranked expansion terms.
        """
        expansion_terms = self.get_expansion_terms(topic_uri)
        # TODO: Implement scoring logic for expansion terms
        # For now, return all expansion terms
        return expansion_terms
    
    def get_expansion_terms(self, topic_uri):
        """
        Fetches expansion terms for a given topic URI based on CSO ontology relations.

        :param topic_uri: URI of the topic for which to find expansion terms.
        :return: A dictionary of expansion terms categorized by relation type.
        """
        # Fetch related equivalent topics
        related_equivalents = self.cso_query_service.get_related_equivalent_topics(topic_uri)

        # Fetch super topics
        super_topics = self.cso_query_service.get_super_topics(topic_uri)

        # Organize the expansion terms in a dictionary
        expansion_terms = {
            'relatedEquivalent': related_equivalents,
            'superTopicOf': super_topics
        }

        return expansion_terms

