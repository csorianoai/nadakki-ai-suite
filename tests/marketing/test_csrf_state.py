"""Tests for CSRF OAuth State management."""
import os
import pytest
from datetime import datetime, timedelta


@pytest.fixture(autouse=True)
def set_env(monkeypatch, tmp_path):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", key)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))


@pytest.fixture
def store():
    from database.token_store import TokenStore
    return TokenStore()


@pytest.mark.asyncio
async def test_save_and_validate_state(store):
    """State should be saveable and validatable."""
    await store.save_oauth_state("state_key_1", "tenant_test", "nonce123", ttl_minutes=10)

    result = await store.validate_and_consume_state("state_key_1")
    assert result is not None
    assert result["tenant_id"] == "tenant_test"
    assert result["nonce"] == "nonce123"


@pytest.mark.asyncio
async def test_state_consumed_once(store):
    """State should be one-time use - second validation returns None."""
    await store.save_oauth_state("state_key_2", "tenant_test", "nonce456")

    first = await store.validate_and_consume_state("state_key_2")
    assert first is not None

    second = await store.validate_and_consume_state("state_key_2")
    assert second is None


@pytest.mark.asyncio
async def test_state_expired_returns_none(store):
    """Expired state should return None."""
    # Save with 0 minute TTL (already expired)
    await store.save_oauth_state("state_key_3", "tenant_test", "nonce789", ttl_minutes=0)

    result = await store.validate_and_consume_state("state_key_3")
    assert result is None


@pytest.mark.asyncio
async def test_nonexistent_state_returns_none(store):
    """Non-existent state key should return None."""
    result = await store.validate_and_consume_state("does_not_exist")
    assert result is None


@pytest.mark.asyncio
async def test_token_encryption(store):
    """Tokens should be encrypted and decryptable."""
    plaintext = "super_secret_token_12345"
    encrypted = store.encrypt(plaintext)
    assert encrypted != plaintext
    decrypted = store.decrypt(encrypted)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_integration_save_and_get(store):
    """Integration should round-trip correctly with encryption."""
    await store.save_integration("tenant_crypto", "meta", {
        "access_token": "my_access_token",
        "refresh_token": "my_refresh_token",
        "page_id": "12345",
        "page_name": "Test Page",
        "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
    })

    result = await store.get_integration("tenant_crypto", "meta")
    assert result is not None
    assert result["access_token"] == "my_access_token"
    assert result["refresh_token"] == "my_refresh_token"
    assert result["page_id"] == "12345"
    assert result["page_name"] == "Test Page"


@pytest.mark.asyncio
async def test_integration_delete(store):
    """Deleted integration should no longer be retrievable."""
    await store.save_integration("tenant_del", "google", {
        "access_token": "token_to_delete",
    })

    deleted = await store.delete_integration("tenant_del", "google")
    assert deleted is True

    result = await store.get_integration("tenant_del", "google")
    assert result is None
