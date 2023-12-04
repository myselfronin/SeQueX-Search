import pysolr
import os

class SolrService:
    def __init__(self):
        self.base_url = os.environ.get('SOLR_BASE_URL')

    def get_topic_matches(self, query_texts):
        solr = pysolr.Solr(self.base_url + '/topics')

        # Construct query to get all possibe match in the query_texts array
        query = ' OR '.join([f'topic:"{text}"' for text in query_texts])

        # Send request to Solr
        results = solr.search(query)

        return results.docs
    
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
    
        