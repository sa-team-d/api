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

@pytest.fixture
def client():
    return TestClient(BASE_URL)

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
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_machine_by_id(auth_headers):
    machine_id = "6740f1cfa8e3f95f42703128"
    response = requests.get(
        f"{BASE_URL}{API_VERSION}machine/{machine_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == machine_id


def test_filter_machines_by_name(auth_headers):
    machine_name = "Laser Cutter"
    response = requests.get(
        f"{BASE_URL}/{API_VERSION}machine/filter",
        params={"machine_name": machine_name},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert isinstance(response.json(), list)

def test_filter_machines_no_params(auth_headers):
    response = requests.get(
        f"{BASE_URL}{API_VERSION}machine/filter",
        headers=auth_headers
    )
    assert response.status_code == 500
    assert "No filter provided" in response.json()["detail"]



