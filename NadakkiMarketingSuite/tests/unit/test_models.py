"""Unit tests for models."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCampaignModel:
    def test_campaign_creation(self):
        from backend.models.campaign import Campaign, CampaignStatus
        campaign = Campaign(tenant_id="t1", name="Test", content_text="Hello")
        assert campaign.id is not None
        assert campaign.status == CampaignStatus.DRAFT
    
    def test_campaign_to_dict(self):
        from backend.models.campaign import Campaign
        campaign = Campaign(tenant_id="t1", name="Test")
        data = campaign.to_dict()
        assert "id" in data
        assert data["status"] == "draft"
    
    def test_campaign_ready_to_publish(self):
        from backend.models.campaign import Campaign
        c1 = Campaign(tenant_id="t1", name="Empty")
        assert c1.is_ready_to_publish() == False
        
        c2 = Campaign(tenant_id="t1", name="Ready", content_text="Content", target_pages=[{"platform": "fb"}])
        assert c2.is_ready_to_publish() == True


class TestSocialConnectionModel:
    def test_connection_creation(self):
        from backend.models.social_connection import SocialConnection, ConnectionStatus
        conn = SocialConnection(tenant_id="t1", platform="facebook")
        assert conn.status == ConnectionStatus.ACTIVE
    
    def test_token_expiration(self):
        from backend.models.social_connection import SocialConnection
        from datetime import datetime, timedelta
        conn = SocialConnection(tenant_id="t1", platform="fb", token_expires_at=datetime.utcnow() - timedelta(hours=1))
        assert conn.is_token_expired() == True
