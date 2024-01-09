from app.services.cso_query import CSOQueryService
from app import logger
from app.models import Topics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from threading import Thread

class QueryExpansion:
    def __init__(self, linked_entities, user_query):
        self.linked_entities = linked_entities
        self.user_query = user_query
        self.num_of_query_term = 5 #This is the number of query term to select at max for each mention

    
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
        expansion_term_uris = self.get_expansion_topic_uri_based_on_relation(topic_uri)  
        
        combined_uris = list(set(element for sublist in expansion_term_uris.values() for element in sublist))

        term_with_description = (Topics.query.with_entities(Topics.cso_uri, Topics.label, Topics.description)
            .filter(Topics.cso_uri.in_(combined_uris)).all())
        
        # Weighing each expansion terms
        score_card = {}

        # Similairty score of each possible expansion terms
        for uri, label, description in term_with_description:
            # If the description is empty then just assign label and caculate similarity based on that
            description_text = description if description is not None else label

            # Context Similarity Calculation
            context_similarity_score = self.cosine_similarity(self.user_query, description_text)

            score_card[uri] = { 'label': label, 'score': context_similarity_score }

        #order the possible expansion terms based on the weight in score_card
        sorted_score_card = sorted(score_card.items(), key=lambda x: x[1]['score'], reverse=True)
        top_candidate = sorted_score_card[: self.num_of_query_term]

        # Create a list of labels for the top_n entries
        top_labels = [details['label'] for _, details in top_candidate]

        return top_labels
    
    def get_expansion_topic_uri_based_on_relation(self, topic_uri):
        """
        Fetches expansion terms for a given topic URI based on CSO ontology relations.

        :param topic_uri: URI of the topic for which to find expansion terms.
        :return: A dictionary of expansion terms categorized by relation type.
        """
        expansion_terms = {}

        # Fetch related equivalent topics
        def fetch_related_equivalents():
            expansion_terms['relatedEquivalent'] = CSOQueryService().get_related_equivalent_topics(topic_uri)

        def fetch_super_topics():
            expansion_terms['superTopicOf'] = CSOQueryService().get_super_topics(topic_uri)

        # Create threads
        thread1 = Thread(target=fetch_related_equivalents)
        thread2 = Thread(target=fetch_super_topics)

        # Start threads
        thread1.start()
        thread2.start()

        # Wait for threads to complete
        thread1.join()
        thread2.join()

        return expansion_terms

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
