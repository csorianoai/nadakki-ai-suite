"""Tests for Google OAuth Router."""
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
    monkeypatch.setenv("NADAKKI_GOOGLE_CLIENT_ID", "843291109142-eesto8c8uek6g8ettceh49ekvk4mrekd.apps.googleusercontent.com")
    monkeypatch.setenv("NADAKKI_GOOGLE_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "https://nadakki-ai-suite.onrender.com/auth/google/callback")
    monkeypatch.setenv("FRONTEND_URL", "https://dashboard.nadakki.com")
    # Reset global store
    import routers.auth.google_oauth as mod
    mod._token_store = None


@pytest.fixture
def client():
    from fastapi import FastAPI
    from routers.auth.google_oauth import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


def test_connect_redirects_to_google(client):
    """GET /auth/google/connect/test should 307 redirect to accounts.google.com."""
    resp = client.get("/auth/google/connect/test", follow_redirects=False)
    assert resp.status_code == 307
    location = resp.headers.get("location", "")
    assert "accounts.google.com" in location
    assert "843291109142" in location


def test_status_nonexistent_tenant(client):
    """GET /auth/google/status/nonexistent should return connected=false."""
    resp = client.get("/auth/google/status/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False
    assert data["user_email"] is None
    assert data["token_valid"] is False


def test_disconnect_nonexistent(client):
    """DELETE /auth/google/disconnect/nonexistent should return disconnected=false."""
    resp = client.delete("/auth/google/disconnect/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["disconnected"] is False


def test_callback_missing_params(client):
    """GET /auth/google/callback without code/state should fail."""
    resp = client.get("/auth/google/callback")
    assert resp.status_code == 400
