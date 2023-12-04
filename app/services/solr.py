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
        