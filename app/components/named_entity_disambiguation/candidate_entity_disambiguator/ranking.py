class CandidateRanking:

    def rank_candidates(self, score_card):
        """
        Rank candidates based on the sum of context similarity and named entity similarity scores.

        :param score_card: Dictionary containing the scores for each candidate.
        :return: A list of tuples (candidate URI, total score) sorted by total score in descending order.
        """
        total_scores = []
        for uri, scores in score_card.items():
            total_score = scores['context_similarity_score'] + scores['named_entity_similarity_score']
            total_scores.append((uri, total_score))

        # Sort the candidates based on the total score in descending order
        total_scores.sort(key=lambda x: x[1], reverse=True)
        return total_scores