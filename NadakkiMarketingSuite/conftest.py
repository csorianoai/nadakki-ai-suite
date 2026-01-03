"""Pytest Configuration and Fixtures."""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(scope="session")
def test_tenant_id() -> str:
    return "test_tenant_001"


@pytest.fixture
def sample_campaign_data() -> Dict[str, Any]:
    return {
        "name": "Test Campaign",
        "objective": "awareness",
        "content_type": "text",
        "content_text": "Test content",
        "hashtags": ["test"]
    }


@pytest.fixture
def api_headers(test_tenant_id: str) -> Dict[str, str]:
    return {"X-Tenant-Id": test_tenant_id, "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def test_client():
    from fastapi.testclient import TestClient
    from backend.main import app
    with TestClient(app) as client:
        yield client
