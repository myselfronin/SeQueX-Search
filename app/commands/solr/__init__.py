import requests
import os

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')

def check_core_exists(core_name):
    """Check if the Solr core exists and return True if it does, False otherwise."""
    status_url = f"{SOLR_BASE_URL}/admin/cores?action=STATUS"
    try:
        response = requests.get(status_url)
        response.raise_for_status()  

        # Parsing the response to check if the core exists
        cores = response.json().get('status').keys()
        
        return core_name in cores
    except requests.RequestException as e:
        # Handle any request-related errors here
        print(f"An error occurred: {e}")
        return False

def create_core(core_name):
    """ Create Solr Core"""
    create_url = f"{SOLR_BASE_URL}/admin/cores?action=CREATE&name={core_name}&configSet=_default"
    response = requests.get(create_url)

    return response.json()