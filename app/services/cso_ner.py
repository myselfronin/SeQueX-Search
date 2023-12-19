import os
import requests

class CSONER:
    def __init__(self):
        self.api_url = os.getenv("CSO_NER_API_URL")
        self.headers = {"Authorization": f"Bearer {os.getenv('CSO_NER_ACCESS_TOKEN')}"}
    
    def query(self, text):
        payload = {"inputs": text}
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            return [item['word'] for item in response_data if 'word' in item]
        else:
            return {"error": f"API request failed with status code {response.status_code}"}


