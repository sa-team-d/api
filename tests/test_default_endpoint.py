import requests
import logging
import os



logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")
API_VERSION = os.getenv("API_VERSION")

def test_mongodb_health_check():
    response = requests.get(
        f"{BASE_URL}health/mongodb",
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['status'] == 'ok'
    assert "smart_app" in json_response["databases"]


def test_mongodb_list_all_data():
    response = requests.get(
        f"{BASE_URL}mongodb/list_all_data",
    )
    
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/html')
    

