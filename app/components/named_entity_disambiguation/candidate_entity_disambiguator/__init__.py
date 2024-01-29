from .ranking import CandidateRanking
from .local_disambiguation import LocalDisambiguation
from app.models import Topics
from app import logger

DISAMBIGUATION_THRESHOLD = 0.7
class CandidateDisambiguator:
    def __init__(self, query_context, mentions_with_candidate_set):
        """
        :param query_context: The context or query text.
        :param mentions_with_candidate_set: Dict of recognized entities and their candidate URIs.
        """
        
        self.query_context = query_context
        self.mentions_with_candidate_set = mentions_with_candidate_set
        self.candidate_ranker = CandidateRanking()
        self.local_disambiguator = LocalDisambiguation()

    def disambiguate(self, mention_label):
        """
        Disambiguate a specific entity based on the query context.

        :param entity: The entity to be disambiguated.
        :return: The top candidate for the given entity.
        :raises: ValueError if the entity is not in recognized entities.
        """
        if mention_label not in self.mentions_with_candidate_set:
            raise ValueError(f"Entity '{mention_label}' not found in recognized entities.")

        candidate_uris = self.mentions_with_candidate_set[mention_label]

        topics_with_description = (
            Topics.query.with_entities(Topics.cso_uri, Topics.label, Topics.description)
            .filter(Topics.cso_uri.in_(candidate_uris)).all()
        )

        # Disambiguation Score
        score_card = {}

        # Local Disambiguation Scores
        for uri, label, description in topics_with_description:
            # If the description is empty then just assign label and caculate similarity based on that
            description_text = description if description is not None else label

            # Context Similarity Calculation
            context_similarity_score = self.local_disambiguator.context_similarity(self.query_context, description_text)

            # Named Entity Similarity Calculation
            named_entity_similarity_score = self.local_disambiguator.entity_name_similarity(mention_label, label)

            score_card[uri] = {
                'context_similarity_score': context_similarity_score, 
                'named_entity_similarity_score': named_entity_similarity_score
            }

        # Rank the Candidate
        ranked_candidates = self.candidate_ranker.rank_candidates(score_card)

        # Return the top candidate if the list is not empty
        if ranked_candidates:
            #--------
            formatted_tuples = '\n'.join(str(tup) for tup in ranked_candidates)
            logger.info("Ranking of mention: " + mention_label + "\n" + formatted_tuples)
            #--------

            # If the score of the top ranked tuple is greater than a threshold value then only its linked
            return ranked_candidates[0][0] if ranked_candidates[0][1] >= DISAMBIGUATION_THRESHOLD else None
        else:
            return None
    

