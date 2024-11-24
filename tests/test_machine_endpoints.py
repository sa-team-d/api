import pytest
import requests
import logging
import os

from typing import Generator
from fastapi.testclient import TestClient

from FFM.test_ffm import ffmAuth

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

def test_get_all_machines(auth_headers):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}machine/",
        headers=auth_headers
    )
    json_response = response.json()

    assert response.status_code == 200
    assert json_response['success'] == True
    assert isinstance(json_response['data'], list)

def test_get_machine_by_id(auth_headers):
    machine_id = "6740f1cfa8e3f95f42703128"
    response = requests.get(
        f"{BASE_URL}{API_VERSION}machine/{machine_id}",
        headers=auth_headers
    )
    json_response = response.json()
    assert response.status_code == 200
    assert json_response['success'] == True
    data = json_response['data']
    assert data["_id"] == machine_id


def test_filter_machines_by_name(auth_headers):
    machine_name = "Laser Cutter"
    response = requests.get(
        f"{BASE_URL}/{API_VERSION}machine/filter",
        params={"machine_name": machine_name},
        headers=auth_headers
    )
    json_response = response.json()
    assert response.status_code == 201
    assert json_response['success'] == True

    assert isinstance(json_response['data'], list)
    for machine in json_response['data']:
        assert machine["name"] == machine_name

def test_filter_machines_no_params(auth_headers):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}machine/filter",
        headers=auth_headers
    )
    json_response = response.json()
    assert json_response['success'] == False

    logger.info(f"Response: {json_response}")
    assert "No filter provided" in json_response["message"]



