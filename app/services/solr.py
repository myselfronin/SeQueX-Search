import pysolr
import os

class SolrService:
    def __init__(self):
        self.base_url = os.environ.get('SOLR_BASE_URL')

    def get_topic_matches(self, query_texts):
        solr = pysolr.Solr(self.base_url + '/topics')

        # Construct the query
        query = ' OR '.join([f'topic:"{text}"' for text in query_texts])

        # Set an initial limit for the number of rows per query
        rows_per_query = 100
        start = 0
        all_results = []

        while True:
            # Fetch a batch of results
            results = solr.search(query, **{'rows': rows_per_query, 'start': start})

            # If no more results, break out of the loop
            if not results.docs:
                break

            # Add results to the list
            all_results.extend(results.docs)

            # Move to the next batch
            start += rows_per_query

        return all_results
    
    def get_paper_matches(self, query_string, start=0, rows=10):
        solr = pysolr.Solr(self.base_url + '/papers')

        # Execute the query with pagination parameters
        results = solr.search(query_string, start=start, rows=rows)

        # Prepare the response
        response = {
            'documents': results.docs,
            'total_results': results.hits,  # Total number of results found
            'time_taken': results.qtime    # Time taken for the query in milliseconds
        }

        return response
    
    def make_keyword_based_query(self, keywords):
        solr_query_parts = [f"(title:{keyword} OR abstract:{keyword})" for keyword in keywords]

        solr_query = " OR ".join(solr_query_parts)

        return solr_query
    

    def make_query_for_expanded_entities(self, expanded_entities):
        # Function to join terms with the OR operator
        def join_terms(original_entity, expansion_term):
            all_terms = [original_entity] + expansion_term
            return " OR ".join(all_terms)

        # Create sub-queries for each mention and join them with OR
        sub_queries = [f"(title:({join_terms(entity, expansion_terms)}) OR abstract:({join_terms(entity, expansion_terms)}))" for entity, expansion_terms in expanded_entities.items()]

        # Join the sub-queries with the AND operator
        expanded_query = " AND ".join(sub_queries)

        return expanded_query
        