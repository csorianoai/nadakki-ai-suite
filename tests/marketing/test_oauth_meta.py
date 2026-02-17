"""Tests for Meta OAuth Router."""
import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def set_env(monkeypatch, tmp_path):
    """Set required environment variables for testing."""
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", key)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("NADAKKI_META_APP_ID", "140247778746")
    monkeypatch.setenv("NADAKKI_META_APP_SECRET", "test_secret")
    monkeypatch.setenv("META_REDIRECT_URI", "https://nadakki-ai-suite.onrender.com/auth/meta/callback")
    monkeypatch.setenv("FRONTEND_URL", "https://dashboard.nadakki.com")
    # Reset global store
    import routers.auth.meta_oauth as mod
    mod._token_store = None


@pytest.fixture
def client():
    from fastapi import FastAPI
    from routers.auth.meta_oauth import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


def test_connect_redirects_to_facebook(client):
    """GET /auth/meta/connect/test should 307 redirect to facebook.com."""
    resp = client.get("/auth/meta/connect/test", follow_redirects=False)
    assert resp.status_code == 307
    location = resp.headers.get("location", "")
    assert "facebook.com" in location
    assert "140247778746" in location


def test_status_nonexistent_tenant(client):
    """GET /auth/meta/status/nonexistent should return connected=false."""
    resp = client.get("/auth/meta/status/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False
    assert data["page_name"] is None
    assert data["token_valid"] is False


def test_disconnect_nonexistent(client):
    """DELETE /auth/meta/disconnect/nonexistent should return disconnected=false."""
    resp = client.delete("/auth/meta/disconnect/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["disconnected"] is False


def test_callback_missing_params(client):
    """GET /auth/meta/callback without code/state should fail."""
    resp = client.get("/auth/meta/callback")
    assert resp.status_code == 400
