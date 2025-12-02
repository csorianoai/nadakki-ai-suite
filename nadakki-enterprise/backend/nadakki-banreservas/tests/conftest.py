import pytest
import os

@pytest.fixture(scope="session")
def test_config():
    return {
        "institution": os.getenv("INSTITUTION", "banreservas"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "api_url": os.getenv("API_URL", "http://localhost:8000"),
        "timeout": 30
    }

@pytest.fixture
def sample_tenant(test_config):
    return {
        "id": "test-tenant-123",
        "name": test_config["institution"],
        "country": "US",
        "plan": "starter"
    }

@pytest.fixture
def sample_user(sample_tenant):
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "tenant_id": sample_tenant["id"],
        "full_name": "Test User"
    }

@pytest.fixture
def auth_headers(sample_user):
    return {
        "Authorization": "Bearer test-token-123",
        "X-Tenant-ID": sample_user["tenant_id"]
    }
