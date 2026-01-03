"""Tests Day 4 - AI Content + Analytics + Export + Notifications."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ai_content_service():
    from backend.services.ai_content_service import AIContentService, ai_content_service
    assert ai_content_service is not None
    templates = ai_content_service.get_templates()
    assert len(templates) >= 5
    print("  [OK] AIContentService")


def test_ai_generate_content():
    from backend.services.ai_content_service import ai_content_service, ContentTone
    content = ai_content_service.generate_ai_content(tenant_id="test", prompt="Nuevo producto", tone=ContentTone.PROFESSIONAL, platform="linkedin")
    assert content.id is not None
    assert len(content.generated_text) > 0
    print("  [OK] AI Generate Content")


def test_ai_template_generation():
    from backend.services.ai_content_service import ai_content_service
    content = ai_content_service.generate_from_template(tenant_id="test", template_id="financial_tip", variables={"tip": "Ahorra 20%", "fact": "ahorro genera riqueza", "topic": "finanzas", "hashtag": "Ahorro"})
    assert content is not None
    print("  [OK] AI Template Generation")


def test_analytics_service():
    from backend.services.analytics_service import AnalyticsService, analytics_service
    metrics = analytics_service.get_dashboard_metrics("test", 30)
    assert "summary" in metrics
    print("  [OK] AnalyticsService")


def test_analytics_report():
    from backend.services.analytics_service import analytics_service, ReportType
    report = analytics_service.generate_report("test", ReportType.WEEKLY)
    assert report.id is not None
    assert len(report.insights) > 0
    print("  [OK] Analytics Report")


def test_export_service():
    from backend.services.export_service import ExportService, export_service
    formats = export_service.get_export_formats()
    assert len(formats) >= 4
    print("  [OK] ExportService")


def test_export_csv():
    from backend.services.export_service import export_service, ExportFormat
    result = export_service.export_campaigns("test", ExportFormat.CSV)
    assert "content" in result
    print("  [OK] Export CSV")


def test_notification_service():
    from backend.services.notification_service import NotificationService, notification_service
    notification = notification_service.create_notification(tenant_id="test", title="Test", message="Test msg")
    assert notification.id is not None
    print("  [OK] NotificationService")


def test_notification_webhook():
    from backend.services.notification_service import notification_service
    webhook = notification_service.register_webhook(tenant_id="test", url="https://example.com/hook", events=["notification.created"])
    assert webhook.id is not None
    print("  [OK] Notification Webhook")


def test_main_app():
    from backend.main import app
    assert app.title == "Nadakki Marketing Suite"
    print("  [OK] Main App Day 4")


def run_all_tests():
    print("\n" + "=" * 60)
    print(" NADAKKI MARKETING SUITE - DAY 4 TESTS")
    print("=" * 60 + "\n")
    tests = [test_ai_content_service, test_ai_generate_content, test_ai_template_generation, test_analytics_service, test_analytics_report, test_export_service, test_export_csv, test_notification_service, test_notification_webhook, test_main_app]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
    print(f"\n RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    return passed, failed


if __name__ == "__main__":
    run_all_tests()
