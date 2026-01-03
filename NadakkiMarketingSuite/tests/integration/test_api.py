"""Integration tests for API endpoints."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["service"] == "Nadakki Marketing Suite"
    
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


class TestCampaignAPI:
    def test_create_campaign(self):
        r = client.post("/api/v1/campaigns", headers={"X-Tenant-Id": "test"}, json={"name": "API Test", "objective": "awareness", "content_type": "text", "content_text": "Test"})
        assert r.status_code == 201
    
    def test_list_campaigns(self):
        r = client.get("/api/v1/campaigns", headers={"X-Tenant-Id": "test"})
        assert r.status_code == 200
        assert "campaigns" in r.json()


class TestTenantAPI:
    def test_list_tenants(self):
        r = client.get("/api/v1/tenants")
        assert r.status_code == 200


class TestAIContentAPI:
    def test_list_templates(self):
        r = client.get("/api/v1/ai/templates")
        assert r.status_code == 200
        assert len(r.json()["templates"]) >= 5
    
    def test_generate(self):
        r = client.post("/api/v1/ai/generate", headers={"X-Tenant-Id": "test"}, json={"prompt": "Test", "tone": "professional"})
        assert r.status_code == 200


class TestAnalyticsAPI:
    def test_dashboard(self):
        r = client.get("/api/v1/analytics/dashboard", headers={"X-Tenant-Id": "test"})
        assert r.status_code == 200
        assert "summary" in r.json()


class TestSchedulerAPI:
    def test_status(self):
        r = client.get("/api/v1/scheduler/status")
        assert r.status_code == 200


class TestNotificationsAPI:
    def test_list(self):
        r = client.get("/api/v1/notifications", headers={"X-Tenant-Id": "test"})
        assert r.status_code == 200

