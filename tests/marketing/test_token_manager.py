"""Tests for Token Manager."""
import os
import pytest
from datetime import datetime, timedelta


@pytest.fixture(autouse=True)
def set_env(monkeypatch, tmp_path):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", key)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("NADAKKI_GOOGLE_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("NADAKKI_GOOGLE_CLIENT_SECRET", "test_secret")


@pytest.fixture
def store():
    from database.token_store import TokenStore
    return TokenStore()


@pytest.fixture
def manager(store):
    from integrations.token_manager import TokenManager
    return TokenManager(store)


@pytest.mark.asyncio
async def test_valid_token_returns_without_refresh(store, manager):
    """A valid, non-expired token should be returned directly."""
    future = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    await store.save_integration("tenant1", "google", {
        "access_token": "valid_token_123",
        "refresh_token": "refresh_123",
        "expires_at": future,
    })

    token = await manager.get_valid_token("tenant1", "google")
    assert token == "valid_token_123"


@pytest.mark.asyncio
async def test_no_integration_raises(manager):
    """Missing integration should raise TokenExpiredError."""
    from integrations.token_manager import TokenExpiredError
    with pytest.raises(TokenExpiredError):
        await manager.get_valid_token("nonexistent", "google")


@pytest.mark.asyncio
async def test_expired_no_refresh_raises(store, manager):
    """Expired token without refresh token should raise TokenExpiredError."""
    from integrations.token_manager import TokenExpiredError

    past = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    await store.save_integration("tenant2", "meta", {
        "access_token": "expired_token",
        "expires_at": past,
    })

    with pytest.raises(TokenExpiredError):
        await manager.get_valid_token("tenant2", "meta")


@pytest.mark.asyncio
async def test_meta_expired_raises(store, manager):
    """Meta tokens can't be auto-refreshed - should raise."""
    from integrations.token_manager import TokenExpiredError

    past = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    await store.save_integration("tenant3", "meta", {
        "access_token": "old_meta_token",
        "refresh_token": "meta_refresh",
        "expires_at": past,
    })

    with pytest.raises(TokenExpiredError, match="User must reconnect"):
        await manager.get_valid_token("tenant3", "meta")
