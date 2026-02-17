"""Tests for Agent Execution endpoint - POST /api/v1/agents/{agent_id}/execute"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def real_agent_id(client):
    """Obtiene un agent_id operativo (marketing/*.py) con execute()."""
    resp = client.get("/api/catalog", params={"module": "marketing", "limit": 253})
    agents = resp.json()["data"]["agents"]
    for a in agents:
        fp = a.get("file_path", "")
        if (
            "_archived" not in fp
            and a.get("status") != "template"
            and "execute" in a.get("action_methods", [])
            and fp.count("/") == 1  # marketing/xxx.py (sin subdirs profundos)
        ):
            return a["id"]
    pytest.skip("No se encontro agente operativo con execute()")


def test_404_agent_not_found(client):
    """Agent inexistente retorna 404."""
    resp = client.post(
        "/api/v1/agents/agente_inexistente_xyz/execute",
        json={"payload": {}, "dry_run": True},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_409_archived_agent(client):
    """Agent archived retorna 409."""
    resp = client.get("/api/catalog", params={"module": "marketing", "limit": 253})
    agents = resp.json()["data"]["agents"]
    archived = [a for a in agents if "_archived" in a.get("file_path", "")]
    if not archived:
        pytest.skip("No hay agentes archived")

    agent_id = archived[0]["id"]
    resp = client.post(
        f"/api/v1/agents/{agent_id}/execute",
        json={"payload": {}, "dry_run": True},
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()


def test_409_template_agent(client):
    """Agent template retorna 409."""
    resp = client.get("/api/catalog", params={"module": "marketing", "status": "template", "limit": 253})
    agents = resp.json()["data"]["agents"]
    templates = [a for a in agents if "_archived" not in a.get("file_path", "")]
    if not templates:
        pytest.skip("No hay agentes template")

    agent_id = templates[0]["id"]
    resp = client.post(
        f"/api/v1/agents/{agent_id}/execute",
        json={"payload": {}, "dry_run": True},
    )
    assert resp.status_code == 409
    assert "template" in resp.json()["detail"].lower()


def test_200_execute_real_agent(client, real_agent_id):
    """Agent real ejecuta con dry_run=True y retorna 200."""
    resp = client.post(
        f"/api/v1/agents/{real_agent_id}/execute",
        json={"payload": {"test": True}, "dry_run": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["agent_id"] == real_agent_id
    assert data["dry_run"] is True
    assert "result" in data


def test_dry_run_default(client, real_agent_id):
    """dry_run es True por defecto."""
    resp = client.post(
        f"/api/v1/agents/{real_agent_id}/execute",
        json={"payload": {}},
    )
    assert resp.status_code == 200
    assert resp.json()["dry_run"] is True
