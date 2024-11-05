import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(".."))
from main import app
from src.plugins.dashboard import schema
from src.models import User

client = TestClient(app)

@pytest.fixture
def current_user():
    return User(id="test_user", username="testuser")

def test_list_dashboards(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.list_dashboards", return_value=[])

    response = client.get("/api/v1/dashboards")
    assert response.status_code == 200
    assert response.json() == {"data": []}

def test_create_dashboard(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.auth.dependencies.check_permissions", return_value=True)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.create_dashboard", return_value=schema.DashboardResponse(id="1", name="Test Dashboard"))

    dashboard_data = {"name": "Test Dashboard"}
    response = client.post("/api/v1/dashboards", json=dashboard_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Dashboard"

def test_get_dashboard(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.get_dashboard", return_value=schema.DashboardResponse(id="1", name="Test Dashboard"))

    response = client.get("/api/v1/dashboards/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Dashboard"

def test_update_dashboard(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.auth.dependencies.check_permissions", return_value=True)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.update_dashboard", return_value=schema.DashboardResponse(id="1", name="Updated Dashboard"))

    dashboard_data = {"name": "Updated Dashboard"}
    response = client.put("/api/v1/dashboards/1", json=dashboard_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Dashboard"

def test_delete_dashboard(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.auth.dependencies.check_permissions", return_value=True)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.delete_dashboard", return_value=None)

    response = client.delete("/api/v1/dashboards/1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Dashboard deleted"}

def test_add_widget(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.auth.dependencies.check_permissions", return_value=True)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.get_dashboard", return_value=schema.DashboardResponse(id="1", name="Test Dashboard"))

    widget_data = {"name": "Test Widget"}
    response = client.post("/api/v1/dashboards/1/widgets", json=widget_data)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Widget"

def test_delete_widget(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.auth.dependencies.check_permissions", return_value=True)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.get_dashboard", return_value=schema.DashboardResponse(id="1", name="Test Dashboard"))

    response = client.delete("/api/v1/dashboards/1/widgets/1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Widget deleted"}

def test_list_widgets(current_user, mocker):
    mocker.patch("src.plugins.auth.dependencies.get_current_user", return_value=current_user)
    mocker.patch("src.plugins.dashboard.repository.DashboardRepository.get_dashboard", return_value=schema.DashboardResponse(id="1", name="Test Dashboard", widgets=[]))

    response = client.get("/api/v1/dashboards/1/widgets")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "data": []}