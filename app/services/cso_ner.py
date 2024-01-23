import os
import requests
from app import logger

class CSONER:
    def __init__(self, text):
        self.api_url = os.getenv("CSO_NER_API_URL")
        self.headers = {"Authorization": f"Bearer {os.getenv('CSO_NER_ACCESS_TOKEN')}"}
        self.text = text
    
    def get_entities(self):
        payload = {"inputs": self.text}
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            return [item['word'] for item in response_data if 'word' in item]
        else:
            logger.info(f"Error requesting CSO NER {response.status_code}")
            return []


