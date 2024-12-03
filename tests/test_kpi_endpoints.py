import pytest
import os
import logging
import requests

from datetime import datetime
from fastapi.testclient import TestClient
from bson import ObjectId

from define import ffmAuth


logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")
API_VERSION = os.getenv("API_VERSION")

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {ffmAuth.token}"}



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
    assert response.status_code == 200
    assert isinstance(response.json()['data'], list)

def test_create_kpi(auth_headers):
    sample_kpi = {
        "name": "test_kpi",
        "type": "atomic",
        "description": "Test KPI",
        "unite_of_measure": "units",
        "formula": "consumption/cycles",
    }

    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/:name?name=test_kpi",
        headers=auth_headers
    )
    
    if response.json()['success'] == True:
        response = requests.delete(
            f"{BASE_URL}{API_VERSION}kpi/:name?name=test_kpi",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    response = requests.post(
        f"{BASE_URL}{API_VERSION}kpi/",
        headers=auth_headers,
        json=sample_kpi
    )
    assert response.status_code == 200
    created_kpi = response.json()["data"]
    logger.info("Created KPI: %s", created_kpi)
    assert created_kpi["name"] == sample_kpi["name"]
    
    # Cleanup
    requests.delete(
        f"{BASE_URL}{API_VERSION}kpi/:id?id={created_kpi['_id']}", 
        headers=auth_headers
    )

def test_get_kpi_by_id(auth_headers):
    # First create a KPI
    sample_kpi = {
        "name": "test_get_kpi",
        "type": "atomic",
        "description": "Test Get KPI",
        "unite_of_measure": "units",
        "formula": "consumption/cycles",
    }
    
    create_response = requests.post(
        f"{BASE_URL}{API_VERSION}kpi/",
        headers=auth_headers,
        json=sample_kpi
    )
    created_kpi = create_response.json()['data']
    kpi_id = created_kpi["_id"]
    
    # Get the created KPI
    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/:id?id={kpi_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    logger.info("Response: %s", response.json())
    assert response.json()["data"]["name"] == sample_kpi["name"]
    
    # Cleanup
    requests.delete(
        f"{BASE_URL}{API_VERSION}kpi/:id?id={kpi_id}", 
        headers=auth_headers
    )

def test_compute_kpi_atomic(auth_headers):
    # Create test KPI with sample data

    params = {
        "machine_id": "6740f1cfa8e3f95f42703128",
        "kpi_id": "673a6ad2d9e0b151b88cbed0",
        "start_date": "2024-09-30 00:00:00",
        "end_date": "2024-10-07 00:00:00",
        "granularity_days": 7,
        "granularity_op": "sum"
    }
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/compute",
        headers=auth_headers,
        params=params
    )
    data = response.json()['data']
    assert response.status_code == 200
    assert isinstance(data, list)


    assert len(data) == 2
    assert data[0]["value"] == 82178.0
    assert data[1]["value"] == 21795.0
    

def test_compute_kpi_composite(auth_headers):

    params = {
        "machine_id": "6740f1cfa8e3f95f42703128",
        "kpi_id": "673c80f2d688f1ba31c15ca6",
        "start_date": "2024-09-30 00:00:00",
        "end_date": "2024-10-07 00:00:00",
        "granularity_days": 7,
        "granularity_op": "sum"
    }
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/compute",
        headers=auth_headers,
        params=params
    )
    data = response.json()['data']
    assert response.status_code == 200
    assert isinstance(data, list)

    assert len(data) == 2
    assert data[0]["value"] == 3.640436235059484e-06
    assert data[1]["value"] == 1.9069123253897118e-06

def test_invalid_kpi_id(auth_headers):
    params = {
        "machine_id": "test_machine",
        "kpi_id": "invalid_id",
        "start_date": (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
        "granularity_days": 1,
        "granularity_op": "sum"
    }
    
    response = requests.get(
        f"{BASE_URL}{API_VERSION}kpi/compute",
        headers=auth_headers,
        params=params
    )

    assert response.json()['success'] == False