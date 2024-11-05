import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(".."))
from main import app

client = TestClient(app)

@pytest.fixture
def machine_data():
    return {
        "name": "Test Machine",
        "type": "Type A",
        "description": "A test machine",
        "tags": ["test", "machine"]
    }

def test_create_machine(machine_data):
    response = client.post("/api/v1/machines/", json=machine_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == machine_data["name"]
    assert data["type"] == machine_data["type"]
    assert data["description"] == machine_data["description"]
    assert data["tags"] == machine_data["tags"]

def test_get_machine(machine_data):
    # First, create a machine
    create_response = client.post("/api/v1/machines/", json=machine_data)
    machine_id = create_response.json()["id"]

    # Then, retrieve the machine
    response = client.get(f"/api/v1/machines/{machine_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == machine_id
    assert data["name"] == machine_data["name"]
    assert data["type"] == machine_data["type"]

def test_update_machine(machine_data):
    # First, create a machine
    create_response = client.post("/api/v1/machines/", json=machine_data)
    machine_id = create_response.json()["id"]

    # Update the machine
    updated_data = machine_data.copy()
    updated_data["name"] = "Updated Machine"
    response = client.put(f"/api/v1/machines/{machine_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Machine"

def test_delete_machine(machine_data):
    # First, create a machine
    create_response = client.post("/api/v1/machines/", json=machine_data)
    machine_id = create_response.json()["id"]

    # Delete the machine
    response = client.delete(f"/api/v1/machines/{machine_id}")
    assert response.status_code == 204

    # Verify the machine is deleted
    response = client.get(f"/api/v1/machines/{machine_id}")
    assert response.status_code == 404

def test_list_machines(machine_data):
    # Create a machine
    client.post("/api/v1/machines/", json=machine_data)

    # List machines
    response = client.get("/api/v1/machines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0