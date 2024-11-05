from fastapi.testclient import TestClient
from fastapi import status
import pytest
import sys, os
sys.path.append(os.path.abspath(".."))
from src.plugins.user.repository import UserRepository
from main import app

client = TestClient(app)

@pytest.fixture
def user_repo():
    return UserRepository()

def test_register_user(user_repo):
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/users/auth/firebase/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == user_data["email"]

def test_get_current_user_profile(user_repo):
    response = client.get("/api/v1/users/users/me", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK

def test_update_current_user_profile(user_repo):
    user_update_data = {
        "full_name": "Updated User"
    }
    response = client.put("/api/v1/users/users/me", json=user_update_data, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == user_update_data["full_name"]

def test_get_user(user_repo):
    user_id = "test_user_id"
    response = client.get(f"/api/v1/users/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK

def test_list_users(user_repo):
    response = client.get("/api/v1/users/users", params={"page": 1, "per_page": 20})
    assert response.status_code == status.HTTP_200_OK

def test_update_user(user_repo):
    user_id = "test_user_id"
    user_update_data = {
        "full_name": "Updated User"
    }
    response = client.put(f"/api/v1/users/users/{user_id}", json=user_update_data, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == user_update_data["full_name"]

def test_delete_user(user_repo):
    user_id = "test_user_id"
    response = client.delete(f"/api/v1/users/users/{user_id}", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User deleted successfully"

def test_disable_user(user_repo):
    user_id = "test_user_id"
    response = client.post("/api/v1/users/admin/users/disable", json={"user_id": user_id}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK

def test_enable_user(user_repo):
    user_id = "test_user_id"
    response = client.post("/api/v1/users/admin/users/enable", json={"user_id": user_id}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK

def test_update_user_roles(user_repo):
    user_role_data = {
        "user_id": "test_user_id",
        "roles": ["admin"]
    }
    response = client.post("/api/v1/users/admin/users/roles", json=user_role_data, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK

def test_list_user_roles(user_repo):
    response = client.get("/api/v1/users/admin/users/roles", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK

def test_remove_user_roles(user_repo):
    user_id = "test_user_id"
    response = client.delete("/api/v1/users/admin/users/roles", json={"user_id": user_id}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK