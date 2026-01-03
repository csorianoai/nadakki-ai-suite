"""
Tests para el sistema de autenticación.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import SocialAuthManager, SocialConnection, TokenEncryptor


def run_async(coro):
    """Helper para ejecutar coroutines."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestTokenEncryptor:
    """Tests para encriptación de tokens."""

    def test_encrypt_decrypt_roundtrip(self):
        """Verifica que encrypt/decrypt son inversos."""
        encryptor = TokenEncryptor()
        original = "my_secret_token_12345"
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == original

    def test_encrypted_differs_from_original(self):
        """Verifica que el encriptado es diferente."""
        encryptor = TokenEncryptor()
        original = "secret"
        encrypted = encryptor.encrypt(original)
        assert encrypted != original


class TestSocialConnection:
    """Tests para el modelo SocialConnection."""

    def test_basic_creation(self):
        """Verifica creación básica."""
        conn = SocialConnection(
            id="conn_1",
            tenant_id="tenant_1",
            platform="facebook",
            platform_user_id="user_1",
            platform_username="testuser",
            access_token="token",
        )
        assert conn.id == "conn_1"
        assert conn.is_active is True

    def test_to_dict(self):
        """Verifica serialización."""
        conn = SocialConnection(
            id="conn_1",
            tenant_id="tenant_1",
            platform="facebook",
            platform_user_id="user_1",
            platform_username="testuser",
            access_token="token",
        )
        data = conn.to_dict()
        assert data["id"] == "conn_1"
        assert isinstance(data["connected_at"], str)


class TestSocialAuthManager:
    """Tests para el gestor de autenticación."""

    def test_generate_state(self):
        """Verifica generación de estado."""
        manager = SocialAuthManager()
        state = manager.generate_state("tenant_1", "facebook")
        assert state is not None
        assert len(state) > 20

    def test_validate_state(self):
        """Verifica validación de estado."""
        manager = SocialAuthManager()
        state = manager.generate_state("tenant_1", "facebook")
        data = manager.validate_state(state)
        assert data is not None
        assert data["tenant_id"] == "tenant_1"
        assert data["platform"] == "facebook"

    def test_state_only_valid_once(self):
        """Verifica que estado solo se puede usar una vez."""
        manager = SocialAuthManager()
        state = manager.generate_state("tenant_1", "facebook")
        data1 = manager.validate_state(state)
        data2 = manager.validate_state(state)
        assert data1 is not None
        assert data2 is None

    def test_save_and_get_connection(self):
        """Verifica guardar y obtener conexión."""
        manager = SocialAuthManager()
        conn = SocialConnection(
            id="conn_test",
            tenant_id="tenant_1",
            platform="facebook",
            platform_user_id="user_1",
            platform_username="testuser",
            access_token="secret_token_123",
        )
        run_async(manager.save_connection(conn))
        retrieved = run_async(manager.get_connection("conn_test"))
        assert retrieved is not None
        assert retrieved.access_token == "secret_token_123"


def run_auth_tests():
    """Ejecuta tests de auth."""
    print("\n" + "=" * 70)
    print(" AUTH SYSTEM TESTS")
    print("=" * 70 + "\n")

    passed = 0
    failed = 0

    test_classes = [
        TestTokenEncryptor,
        TestSocialConnection,
        TestSocialAuthManager,
    ]

    for test_class in test_classes:
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✅ {test_class.__name__}.{method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {test_class.__name__}.{method_name}: {e}")
                    failed += 1

    print(f"\n RESULTS: {passed} passed, {failed} failed\n")
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_auth_tests()
    exit(0 if failed == 0 else 1)