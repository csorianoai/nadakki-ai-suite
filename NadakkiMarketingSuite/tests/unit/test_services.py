"""Unit tests for services."""
import pytest
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestCampaignService:
    def test_create_campaign(self):
        from backend.services.campaign_service import CampaignService
        from backend.schemas.campaign_schemas import CampaignCreate
        service = CampaignService()
        data = CampaignCreate(name="Test", content_text="Content")
        campaign = run_async(service.create_campaign("t1", data))
        assert campaign.name == "Test"
    
    def test_list_campaigns(self):
        from backend.services.campaign_service import CampaignService
        from backend.schemas.campaign_schemas import CampaignCreate
        service = CampaignService()
        data = CampaignCreate(name="List Test", content_text="Content")
        run_async(service.create_campaign("t1", data))
        result = run_async(service.list_campaigns("t1"))
        assert "campaigns" in result


class TestSchedulerService:
    def test_singleton(self):
        from backend.services.scheduler_service import SchedulerService
        s1 = SchedulerService()
        s2 = SchedulerService()
        assert s1 is s2
    
    def test_start_stop(self):
        from backend.services.scheduler_service import scheduler_service
        result = scheduler_service.start()
        assert result["status"] in ["started", "already_running"]
        scheduler_service.stop()


class TestAIContentService:
    def test_get_templates(self):
        from backend.services.ai_content_service import ai_content_service
        templates = ai_content_service.get_templates()
        assert len(templates) >= 5
    
    def test_generate_content(self):
        from backend.services.ai_content_service import ai_content_service, ContentTone
        content = ai_content_service.generate_ai_content(tenant_id="test", prompt="Test", tone=ContentTone.PROFESSIONAL, platform="linkedin")
        assert content.id is not None


class TestAnalyticsService:
    def test_dashboard_metrics(self):
        from backend.services.analytics_service import analytics_service
        metrics = analytics_service.get_dashboard_metrics("test", 30)
        assert "summary" in metrics
    
    def test_generate_report(self):
        from backend.services.analytics_service import analytics_service, ReportType
        report = analytics_service.generate_report("test", ReportType.WEEKLY)
        assert len(report.insights) > 0


class TestExportService:
    def test_export_formats(self):
        from backend.services.export_service import export_service
        formats = export_service.get_export_formats()
        assert len(formats) >= 4


class TestNotificationService:
    def test_create_notification(self):
        from backend.services.notification_service import notification_service
        n = notification_service.create_notification("test", "Title", "Message")
        assert n.id is not None
