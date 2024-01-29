from app.services.cso_query import CSOQueryService
from app import logger
from app.models import Topics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from threading import Thread
import traceback

EXPANSION_SIMILARITY_THRESHOLD=0.55
class QueryExpansion:
    def __init__(self, linked_entities, user_query):
        self.linked_entities = linked_entities
        self.user_query = user_query
    
    def get_expanded_entities(self):
        """
        Fetches expanded entities for each linked entity.

        :return: A dictionary where each key is an entity label and the value is a dictionary of expansion terms.
        """
        expanded_entities = {}

        #Link is formed only when corresponding URI is available hence filtering 
        filtered_linked_entities = {k: v for k, v in self.linked_entities.items() if v is not None}
    
        recognized_topic_uris = filtered_linked_entities.values()

        related_equivalent_topics_dict = CSOQueryService().get_related_equivalent_topics(recognized_topic_uris)

        sub_topics_dict = CSOQueryService().get_sub_topics(recognized_topic_uris)
       
        for linked_entity_label, linked_entity_uri in filtered_linked_entities.items():
            candidate_topic_uris = set()

            if(linked_entity_uri in related_equivalent_topics_dict):
                candidate_topic_uris.update(related_equivalent_topics_dict[linked_entity_uri].split(","))

            if(linked_entity_uri in sub_topics_dict):
                candidate_topic_uris.update(sub_topics_dict[linked_entity_uri].split(","))

            expanded_entities[linked_entity_label] = self.get_ranked_expansion_term(list(candidate_topic_uris))


        return expanded_entities
    
    def get_ranked_expansion_term(self, candidate_uris):
        """
        Ranks candidate expansion terms.

        :param candidate_uris: List of URIs that are possibly candidates
        :return: A dictionary of ranked expansion terms.
        """
        
        term_with_description = (Topics.query.with_entities(Topics.cso_uri, Topics.label, Topics.description)
            .filter(Topics.cso_uri.in_(candidate_uris)).all())
        
    
        # Weighing each expansion terms
        score_card = {}
        max_score = 0

        # Similairty score of each possible expansion terms
        for uri, label, description in term_with_description:
            # If the description is empty then just assign label and caculate similarity based on that
            description_text = description if description is not None else label

            # Context Similarity Calculation
            context_similarity_score = self.cosine_similarity(self.user_query, description_text)

            score_card[uri] = { 'label': label, 'score': context_similarity_score }
        
        # If the score of the expansion term is greate or equal to the threshold then its is selected
        filtered_score_card = {uri: data for uri, data in score_card.items() if data['score'] >= EXPANSION_SIMILARITY_THRESHOLD}

        for uri, data in score_card.items():
            max_score = data['score'] if data['score'] > max_score  else max_score
        
        # Extract the label from the filtered score card
        expansion_term_labels = [details['label'] for details in filtered_score_card.values()]

        return expansion_term_labels
    

    def jaccard_similarity(self, text1, text2):
        """
        Calculate the Jaccard Similarity between two texts.

        :param text1: The first text
        :param text2: The second text
        :return: The Jaccard Similarity score
        """
        # Initialize the CountVectorizer
        vectorizer = CountVectorizer()

        # Convert the texts into count vectors
        count_matrix = vectorizer.fit_transform([text1, text2])

        # Convert the count vectors to boolean (presence/absence) vectors
        bool_matrix = count_matrix.astype(bool).astype(int)

        # Calculate the intersection and union
        intersection = bool_matrix[0].dot(bool_matrix[1].T).A[0][0]
        union = bool_matrix[0].sum() + bool_matrix[1].sum() - intersection

        # Compute and return the Jaccard Similarity
        return intersection / union if union != 0 else 0
    
    def cosine_similarity(self, text1, text2):
        """
        Calculate the cosine similarity between two texts.
        
        :param text1: The first text
        :param text2: The second text
        :return: The cosine similarity score
        """
        # Convert the texts into TF-IDF vectors
        tfidf_matrix = TfidfVectorizer().fit_transform([text1, text2])

        # Compute and return the cosine similarity
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    def log_terms_based_on_relation(self, expansion_terms):
        for entity_label, relations in expansion_terms.items():
            logger.info(f"Entity: {entity_label}")
            for relation_type, uris in relations.items():
                if uris:
                    uris_str = ', '.join(str(uri) for uri in uris)
                else:
                    uris_str = "None or Empty"
                self.logger.info(f"{relation_type}: {uris_str}")
