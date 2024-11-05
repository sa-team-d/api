import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(".."))
from main import app
from src.models import Report, User
from src.plugins.report.repository import ReportRepository

client = TestClient(app)

@pytest.fixture
def mock_current_user():
    return User(id="test_user", username="testuser")

@pytest.fixture
def mock_report():
    return Report(id="test_report", title="Test Report", content="This is a test report.")

@pytest.fixture
def mock_repository(mocker, mock_report):
    repository = mocker.patch("src.plugins.report.repository.ReportRepository")
    repository.create_report.return_value = mock_report
    repository.get_report.return_value = mock_report
    repository.list_reports.return_value = {"reports": [mock_report]}
    return repository

@pytest.mark.asyncio
async def test_create_report(mock_current_user, mock_report, mock_repository):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/reports/", json=mock_report.dict())
    assert response.status_code == 200
    assert response.json() == mock_report.dict()

@pytest.mark.asyncio
async def test_get_report(mock_current_user, mock_report, mock_repository):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/reports/{mock_report.id}")
    assert response.status_code == 200
    assert response.json() == mock_report.dict()

@pytest.mark.asyncio
async def test_list_reports(mock_current_user, mock_report, mock_repository):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/")
    assert response.status_code == 200
    assert response.json() == {"reports": [mock_report.dict()]}

@pytest.mark.asyncio
async def test_export_report(mock_current_user, mock_report, mock_repository):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/api/v1/reports/{mock_report.id}/export", params={"format": "pdf"})
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Report exported as pdf",
        "download_url": f"/downloads/reports/{mock_report.id}.pdf"
    }

@pytest.mark.asyncio
async def test_delete_report(mock_current_user, mock_report, mock_repository):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/reports/{mock_report.id}")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Report deleted"}