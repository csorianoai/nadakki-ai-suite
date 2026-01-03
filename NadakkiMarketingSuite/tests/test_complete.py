"""Tests completos - Nadakki Marketing Suite."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_tenant_manager():
    from core.tenant_manager import TenantManager, tenant_manager
    from core.config import TenantConfig
    assert tenant_manager is not None
    config = TenantConfig.default("bank_test", "Test Bank")
    # Clean previous
    tenant_manager.delete_tenant("bank_test")
    tenant = tenant_manager.register_tenant(config)
    assert tenant.tenant_id == "bank_test"
    assert tenant_manager.check_feature("bank_test", "campaigns") == True
    print("  [OK] TenantManager")


def test_campaign_model():
    from backend.models.campaign import Campaign, CampaignStatus
    c = Campaign(tenant_id="t1", name="Test")
    assert c.status == CampaignStatus.DRAFT
    print("  [OK] Campaign Model")


def test_scheduler_service():
    from backend.services.scheduler_service import SchedulerService
    s1 = SchedulerService()
    s2 = SchedulerService()
    assert s1 is s2
    print("  [OK] SchedulerService Singleton")


def test_metrics_service():
    from backend.services.metrics_service import MetricsService
    svc = MetricsService()
    summary = svc.get_tenant_summary("test")
    assert "tenant_id" in summary
    print("  [OK] MetricsService")


def test_main_app():
    from backend.main import app
    assert app.title == "Nadakki Marketing Suite"
    print("  [OK] Main App")


def run_all_tests():
    print("\n" + "=" * 60)
    print(" NADAKKI MARKETING SUITE - COMPLETE TESTS")
    print("=" * 60 + "\n")
    tests = [test_tenant_manager, test_campaign_model, test_scheduler_service, test_metrics_service, test_main_app]
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
