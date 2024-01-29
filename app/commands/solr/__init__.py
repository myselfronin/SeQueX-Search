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

def update_solr_schema(core_name, fields_to_update):
    """
    Update the schemea of the core to configure which fields to be indexed
    """
    headers = {'Content-Type': 'application/json'}
    schema_api_url = f"{SOLR_BASE_URL}/{core_name}/schema"


    # Create a payload with all the fields to be updated
    payload = {"add-field": fields_to_update}
    response = requests.post(schema_api_url, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Error updating fields: {response.text}")
        return False
    else:
        print("Fields updated successfully.")
        return True

