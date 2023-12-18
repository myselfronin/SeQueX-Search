from .semantic_similarity import SemanticSimilarity

class CandidateRanking:
    def __init__(self):
        self.similarity_calculator = SemanticSimilarity()

    def rank_candidates(self, query_context, candidates_with_description):
        """
        Rank candidates based on their cosine similarity to the query.

        :param query_context: The query text
        :param candidates_with_description: A list of tuples, each containing (URI, label, description) of a candidate
        :return: A list of tuples (candidate URI, label, score) sorted by score in descending order
        """
        rankings = []
        for uri, label, description in candidates_with_description:
            # If the description is empty then just assign label and caculate similarity based on that
            description_text = description if description is not None else label
            score = self.similarity_calculator.cosine_similarity(query_context, description_text)
            rankings.append((uri, score))

        # Sort the candidates based on the similarity score in descending order
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings