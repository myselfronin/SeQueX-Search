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
        solr = pysolr.Solr(self.base_url + '/evaluationpapers')

        # Execute the query with pagination parameters
        results = solr.search(query_string, start=start, rows=rows)

        # Prepare the response
        response = {
            'documents': results.docs,
            'total_results': results.hits,  # Total number of results found
            'time_taken': results.qtime    # Time taken for the query in milliseconds
        }

        return response
    
    def make_keyword_based_query(self, query_string):
        query_string = self.escape_solr_special_char(query_string)
        
        return f"(title:*{query_string}* OR abstract:*{query_string}*)"

    def make_query_for_expanded_entities(self, expanded_entities):
        # Function to join terms with the OR operator
        def join_terms(original_entity, expansion_term):
            all_terms = [original_entity] + expansion_term

            all_term_with_removed_special_char = [self.escape_solr_special_char(term) for term in all_terms]
            return " OR ".join(all_term_with_removed_special_char)

        # Create sub-queries for each mention and join them with OR
        sub_queries = [f"(title:({join_terms(entity, expansion_terms)}) OR abstract:({join_terms(entity, expansion_terms)}) OR semantic_topics:({join_terms(entity, expansion_terms)}))" for entity, expansion_terms in expanded_entities.items()]

        # Join the sub-queries with the AND operator
        expanded_query = " OR ".join(sub_queries)

        return expanded_query
    
    def escape_solr_special_char(self, query):
        special_chars = ["+", "-", "&&", "||", "!", "(", ")", "{", "}", "[", "]", "^", '"', "~", "*", "?", ":"]
        for char in special_chars:
            query = query.replace(char, "\\" + char)
        return query
        