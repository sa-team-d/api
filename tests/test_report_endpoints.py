import pytest
import requests
import logging
import os


from define import ffmAuth, smoAuth

logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")
API_VERSION = os.getenv("API_VERSION")

@pytest.fixture
def auth_headers_ffm():
    return {"Authorization": f"Bearer {ffmAuth.token}"}

@pytest.fixture
def auth_headers_smo():
    return {"Authorization": f"Bearer {smoAuth.token}"}

def test_get_all_reports_ffm(auth_headers_ffm):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/",
        headers=auth_headers_ffm
    )
    json_response = response.json()

    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)
    

def test_get_all_reports_smo(auth_headers_smo):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/",
        headers=auth_headers_smo
    )
    json_response = response.json()

    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)

    
def test_reports_ffm_smo_disjointness(auth_headers_ffm, auth_headers_smo):
    response_ffm = requests.get(
        f"{BASE_URL}{API_VERSION}report/",
        headers=auth_headers_ffm
    )
    response_smo = requests.get(
        f"{BASE_URL}{API_VERSION}report/",
        headers=auth_headers_smo
    )
    json_response_ffm = response_ffm.json()
    json_response_smo = response_smo.json()
    
    assert response_ffm.status_code == 200
    assert response_smo.status_code == 200
    assert json_response_ffm['success'] == True
    assert json_response_smo['success'] == True
    assert isinstance(json_response_ffm['data'], list)
    assert isinstance(json_response_smo['data'], list)
    
    reports_ffm = json_response_ffm['data']
    reports_smo = json_response_smo['data']
    
    for report in reports_ffm:
        assert report not in reports_smo
        
    for report in reports_smo:
        assert report not in reports_ffm


def test_get_reports_by_machine_id(auth_headers_ffm):
    machine_id = "ast-anxkweo01vv2"  # Example machine ID
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter",
        params={"machine_id": machine_id},
        headers=auth_headers_ffm
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)
    if len(json_response['data']) > 0:
        assert machine_id in json_response['data'][0]['asset_id']
        assert json_response['data'][0]['user_uid'] == ffmAuth.uid
        assert json_response['data'][0]['user_uid'] != smoAuth.uid


def test_get_reports_by_machine_id_not_found(auth_headers_smo):
    machine_id = "nonexistent-id"
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter",
        params={"machine_id": machine_id},
        headers=auth_headers_smo
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == False
    assert "No reports found" in json_response['message']


# def test_create_report(auth_headers):
#     report_data = {
#         "name": "Test Report",
#         "site": "Test Site",
#         "kpi_name": "Monthly Revenue",
#         "frequency": "monthly"
#     }
    
#     response = requests.post(
#         f"{BASE_URL}{API_VERSION}report/",
#         params=report_data,
#         headers=auth_headers
#     )
#     json_response = response.json()
    
#     assert response.status_code == 201
#     assert json_response['kpi_name'] == report_data['kpi_name']
#     assert isinstance(json_response['user_uid'], str)
