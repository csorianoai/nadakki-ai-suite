"""End-to-end workflow tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestCampaignWorkflow:
    def test_full_lifecycle(self):
        headers = {"X-Tenant-Id": "e2e_test"}
        
        # Create
        r1 = client.post("/api/v1/campaigns", headers=headers, json={"name": "E2E Test", "objective": "engagement", "content_type": "text", "content_text": "E2E content"})
        assert r1.status_code == 201
        campaign_id = r1.json()["id"]
        
        # Get
        r2 = client.get(f"/api/v1/campaigns/{campaign_id}", headers=headers)
        assert r2.status_code == 200
        
        # Update
        r3 = client.patch(f"/api/v1/campaigns/{campaign_id}", headers=headers, json={"name": "Updated"})
        assert r3.status_code == 200
        assert r3.json()["name"] == "Updated"


class TestAIWorkflow:
    def test_content_generation(self):
        headers = {"X-Tenant-Id": "e2e_ai"}
        
        # Templates
        r1 = client.get("/api/v1/ai/templates")
        assert r1.status_code == 200
        
        # Generate
        r2 = client.post("/api/v1/ai/generate", headers=headers, json={"prompt": "New product launch", "tone": "professional"})
        assert r2.status_code == 200
        assert "generated_text" in r2.json()


class TestAnalyticsWorkflow:
    def test_reporting(self):
        headers = {"X-Tenant-Id": "e2e_analytics"}
        
        # Dashboard
        r1 = client.get("/api/v1/analytics/dashboard", headers=headers)
        assert r1.status_code == 200
        
        # Generate report
        r2 = client.post("/api/v1/analytics/reports?report_type=weekly", headers=headers)
        assert r2.status_code == 200
        assert "insights" in r2.json()
