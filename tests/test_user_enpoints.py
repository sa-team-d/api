import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pytest
from fastapi.testclient import TestClient

import requests as req
import os

API_VERSION = os.getenv("API_VERSION", "v1")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

REQ_URL = f"{BASE_URL}{API_VERSION}user"



@pytest.fixture
def auth_headers():
    # Login to get token
    response = req.post(f"{REQ_URL}/login", json={
        "email": "ffm@example.com",
        "password": "passwordffm"
    })
    json_response = response.json()

    assert json_response["success"] == True

    token = response.json()["data"]["id_token"]
    return {"Authorization": f"Bearer {token}"}

def test_list_users(auth_headers):
    
    response = req.get(f"{REQ_URL}/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert len(data["data"]) >= 2
    assert data["message"] == "Users listed successfully"

def test_get_current_user(auth_headers):
    response = req.get(f"{REQ_URL}/", headers=auth_headers)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["uid"] is not None

def test_filter_users_by_name(auth_headers):
    response = req.get(
        f"{REQ_URL}/filter",
        params={"first_name": "Giovanni", "last_name": "Bianchi"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "Giovanni Bianchi"

def test_filter_users_by_email(auth_headers):
    response = req.get(
        f"{REQ_URL}/filter",
        params={"email": "smo@example.com"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["data"]) == 1
    assert data["data"][0]["email"] == "smo@example.com"

def test_filter_users_not_found(auth_headers):
    response = req.get(
        f"{REQ_URL}/filter",
        params={"first_name": "NonExistent", "last_name": "User"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["data"] is None
    assert "No users found" in data["message"]

def test_unauthorized_access():
    response = req.get(f"{REQ_URL}/list")
    assert response.status_code == 403