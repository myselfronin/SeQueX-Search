from .ranking import CandidateRanking
from app.models import Topics
from app import logger

class CandidateDisambiguator:
    def __init__(self, query_context, mentions_with_candidate_set):
        """
        :param query_context: The context or query text.
        :param mentions_with_candidate_set: Dict of recognized entities and their candidate URIs.
        """
        
        self.query_context = query_context
        self.mentions_with_candidate_set = mentions_with_candidate_set
        self.candidate_ranker = CandidateRanking()

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

        # Rank the Candidate
        ranked_candidates = self.candidate_ranker.rank_candidates(self.query_context, topics_with_description)

        # Return the top candidate if the list is not empty
        if ranked_candidates:
            #--------
            formatted_tuples = '\n'.join(str(tup) for tup in ranked_candidates)
            logger.info("Ranking of mention: " + mention_label + "\n" + formatted_tuples)
            #--------

            top_candidate = ranked_candidates[0][0]
            return top_candidate
        else:
            return None
    

