import pytest
import requests
import logging
import os
import datetime


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

def test_get_report_by_name(auth_headers_ffm):
    report_name = "Q1 Production Summary"
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter?name={report_name}",
        headers=auth_headers_ffm
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response['message'] == "Reports retrieved successfully"
    assert json_response['success'] == True
    data = json_response['data']

    
    assert data['name'] == report_name
    assert data['user_uid'] == ffmAuth.uid
    assert data['user_uid'] != smoAuth.uid

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

def test_get_reports_by_site_id_smo(auth_headers_smo):
    site_id = 0  # Example machine ID
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter",
        params={"site_id": site_id},
        headers=auth_headers_smo
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)
    if len(json_response['data']) > 0:
        assert site_id in json_response['data'][0]['sites_id']
        assert json_response['data'][0]['user_uid'] == smoAuth.uid
        assert json_response['data'][0]['user_uid'] != ffmAuth.uid
        

def test_get_reports_by_site_id_ffm(auth_headers_ffm):
    site_id = 1  # Example machine ID
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter",
        params={"site_id": site_id},
        headers=auth_headers_ffm
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)
    if len(json_response['data']) > 0:
        assert site_id in json_response['data'][0]['sites_id']
        assert json_response['data'][0]['user_uid'] == ffmAuth.uid
        assert json_response['data'][0]['user_uid'] != smoAuth.uid


def test_get_reports_by_site_id_not_found(auth_headers_smo):
    site_id = -1
    response = requests.get(
        f"{BASE_URL}{API_VERSION}report/filter",
        params={"site_id":site_id},
        headers=auth_headers_smo
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == False
    assert "No reports found" in json_response['message']


# def test_create_report_success(auth_headers_ffm):
#     report_data = {
#         "name": "Test Production Report",
#         "site": 1,
#         "kpi_names": "production_rate,efficiency",
#         "start_date": "2024-01-01 00:00:00",
#         "end_date": "2024-02-10 00:00:00",
#         "operation": "sum"
#     }
    
#     response = requests.post(
#         f"{BASE_URL}{API_VERSION}report/",
#         params=report_data,
#         headers=auth_headers_ffm
#     )
#     json_response = response.json()
    
#     assert response.status_code == 201
#     assert json_response['success'] == True
#     assert json_response['message'] == "Report created successfully"
#     assert isinstance(json_response['data'], str)  # PDF URL
#     assert json_response['data'].startswith("https://")

def test_create_report_invalid_date(auth_headers_ffm):
    report_data = {
        "name": "Invalid Date Report",
        "site": "Factory A",
        "kpi_names": "production_rate",
        "start_date": "invalid-date",
        "end_date": "2024-11-10 00:00:00",
        "operation": "sum"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}report/",
        params=report_data,
        headers=auth_headers_ffm
    )
    
    assert response.status_code == 422  # FastAPI validation error

def test_create_report_missing_params(auth_headers_ffm):
    report_data = {
        "name": "Incomplete Report"
        # Missing required parameters
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}report/",
        params=report_data,
        headers=auth_headers_ffm
    )
    
    assert response.status_code == 422

def test_create_report_invalid_operation(auth_headers_ffm):
    report_data = {
        "name": "Invalid Operation Report",
        "site": "Factory A",
        "kpi_names": "production_rate",
        "start_date": "2024-11-02 00:00:00",
        "end_date": "2024-11-10 00:00:00",
        "operation": "invalid_op"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}report/",
        params=report_data,
        headers=auth_headers_ffm
    )
    json_response = response.json()
    
    assert response.status_code == 200  # API returns 200 even for errors
    assert json_response['success'] == False

def test_create_report_unauthorized():
    report_data = {
        "name": "Unauthorized Report",
        "site": "Factory A",
        "kpi_names": "production_rate",
        "start_date": "2024-11-02 00:00:00",
        "end_date": "2024-11-10 00:00:00"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}report/",
        params=report_data,
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401

def test_create_report_future_dates(auth_headers_ffm):
    future_start = datetime.datetime.now() + datetime.timedelta(days=30)
    future_end = future_start + datetime.timedelta(days=7)
    
    report_data = {
        "name": "Future Report",
        "site": "Factory A",
        "kpi_names": "production_rate",
        "start_date": future_start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": future_end.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}report/",
        params=report_data,
        headers=auth_headers_ffm
    )
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['success'] == False