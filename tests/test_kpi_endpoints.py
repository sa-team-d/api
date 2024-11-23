import pytest
import os
import logging
import requests

from datetime import datetime
from fastapi.testclient import TestClient
from bson import ObjectId

from FFM.test_ffm import ffmAuth


logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")
API_VERSION = os.getenv("API_VERSION")

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {ffmAuth.token}"}

@pytest.fixture
def client():
    return TestClient(BASE_URL)


def test_server_is_up():
    try:
        response = requests.get(f"{BASE_URL}")
        assert response.status_code == 200
    except requests.ConnectionError:
        pytest.fail("Server is not running at http://127.0.0.1:8000")

def test_list_kpis(auth_headers):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/",
        headers=auth_headers    
    )
    print(response)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_kpi(auth_headers):
    sample_kpi = {
        "name": "test_kpi",
        "type": "atomic",
        "description": "Test KPI",
        "unite_of_measure": "units",
        "formula": "consumption/cycles",
        "config": {
            "children":  [
                "673a6ad2d9e0b151b88cbed0",
                "673a6ad3d9e0b151b88cbed2"
            ],
            "formula": "working_time/offline_time"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}kpi/",
        headers=auth_headers,
        json=sample_kpi
    )

    logger.info(f"Response: {response.json()}")
    assert response.status_code == 200
    created_kpi = response.json()
    assert created_kpi["name"] == sample_kpi["name"]
    
    # Cleanup
    requests.delete(
        f"{BASE_URL}{API_VERSION}kpi/{created_kpi['_id']}", 
        headers=auth_headers
    )

# def test_get_kpi_by_id(auth_headers):
#     # First create a KPI
#     sample_kpi = {
#         "name": "test_get_kpi",
#         "type": "atomic",
#         "description": "Test Get KPI",
#         "unite_of_measure": "units",
#         "config": {
#             "children": [],
#             "formula": None
#         }
#     }
    
#     create_response = requests.post(
#         f"{BASE_URL}{API_VERSION}kpi/",
#         headers=auth_headers,
#         json=sample_kpi
#     )
#     created_kpi = create_response.json()
#     kpi_id = created_kpi["_id"]
    
#     # Get the created KPI
#     response = requests.get(
#         f"{BASE_URL}{API_VERSION}kpi/{kpi_id}",
#         headers=auth_headers
#     )
#     assert response.status_code == 200
#     assert response.json()["name"] == sample_kpi["name"]
    
#     # Cleanup
#     requests.delete(
#         f"{BASE_URL}{API_VERSION}kpi/{kpi_id}", 
#         headers=auth_headers
#     )

# def test_compute_kpi(auth_headers):
#     # Create test KPI with sample data
#     sample_kpi = {
#         "name": "test_compute_kpi",
#         "type": "atomic",
#         "description": "Test Compute KPI",
#         "unite_of_measure": "units",
#         "config": {
#             "children": [],
#             "formula": None
#         },
#         "data": [{
#             "machine_id": "test_machine",
#             "datetime": datetime.now().isoformat(),
#             "sum": 10,
#             "avg": 5,
#             "min": 1,
#             "max": 10
#         }]
#     }
    
#     create_response = requests.post(
#         f"{BASE_URL}{API_VERSION}kpi/",
#         headers=auth_headers,
#         json=sample_kpi
#     )
#     created_kpi = create_response.json()
    
#     params = {
#         "machine_id": "test_machine",
#         "kpi_id": created_kpi["_id"],
#         "start_date": (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y-%m-%d %H:%M:%S"),
#         "end_date": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
#         "granularity_days": 1,
#         "granularity_op": "sum"
#     }
    
#     response = requests.get(
#         f"{BASE_URL}{API_VERSION}kpi/compute",
#         headers=auth_headers,
#         params=params
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)
    
#     # Cleanup
#     requests.delete(
#         f"{BASE_URL}{API_VERSION}kpi/{created_kpi['_id']}", 
#         headers=auth_headers
#     )

# def test_compute_composite_kpi(auth_headers):
#     # Create atomic KPI first
#     atomic_kpi = {
#         "name": "test_atomic_kpi",
#         "type": "atomic",
#         "description": "Test Atomic KPI",
#         "unite_of_measure": "units",
#         "config": {
#             "children": [],
#             "formula": None
#         }
#     }
    
#     atomic_response = requests.post(
#         f"{BASE_URL}{API_VERSION}kpi/",
#         headers=auth_headers,
#         json=atomic_kpi
#     )
#     atomic = atomic_response.json()
    
#     # Create composite KPI
#     composite_kpi = {
#         "name": "test_composite_kpi",
#         "type": "composite",
#         "description": "Test Composite KPI",
#         "unite_of_measure": "units",
#         "config": {
#             "children": [atomic["_id"]],
#             "formula": atomic["name"]
#         }
#     }
    
#     composite_response = requests.post(
#         f"{BASE_URL}{API_VERSION}kpi/",
#         headers=auth_headers,
#         json=composite_kpi
#     )
#     composite = composite_response.json()
    
#     params = {
#         "machine_id": "test_machine",
#         "kpi_id": composite["_id"],
#         "start_date": (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y-%m-%d %H:%M:%S"),
#         "end_date": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
#         "granularity_days": 1,
#         "granularity_op": "sum"
#     }
    
#     response = requests.get(
#         f"{BASE_URL}{API_VERSION}kpi/compute",
#         headers=auth_headers,
#         params=params
#     )
#     assert response.status_code == 200
    
#     # Cleanup
#     requests.delete(
#         f"{BASE_URL}{API_VERSION}kpi/{atomic['_id']}", 
#         headers=auth_headers
#     )
#     requests.delete(
#         f"{BASE_URL}{API_VERSION}kpi/{composite['_id']}", 
#         headers=auth_headers
#     )

# def test_invalid_kpi_id(auth_headers):
#     params = {
#         "machine_id": "test_machine",
#         "kpi_id": "invalid_id",
#         "start_date": (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y-%m-%d %H:%M:%S"),
#         "end_date": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
#         "granularity_days": 1,
#         "granularity_op": "sum"
#     }
    
#     response = requests.get(
#         f"{BASE_URL}{API_VERSION}kpi/compute",
#         headers=auth_headers,
#         params=params
#     )
#     assert response.status_code == 400