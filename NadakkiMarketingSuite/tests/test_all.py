"""Master Test Runner - All tests with coverage report."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_unit_tests():
    print("\n--- UNIT TESTS ---\n")
    from tests.unit.test_models import TestCampaignModel, TestSocialConnectionModel
    from tests.unit.test_services import TestCampaignService, TestSchedulerService, TestAIContentService, TestAnalyticsService, TestExportService, TestNotificationService
    
    results = {"passed": 0, "failed": 0}
    test_classes = [TestCampaignModel(), TestSocialConnectionModel(), TestCampaignService(), TestSchedulerService(), TestAIContentService(), TestAnalyticsService(), TestExportService(), TestNotificationService()]
    
    for tc in test_classes:
        for method in dir(tc):
            if method.startswith("test_"):
                try:
                    getattr(tc, method)()
                    print(f"  [OK] {tc.__class__.__name__}.{method}")
                    results["passed"] += 1
                except Exception as e:
                    print(f"  [FAIL] {tc.__class__.__name__}.{method}: {e}")
                    results["failed"] += 1
    return results


def run_integration_tests():
    print("\n--- INTEGRATION TESTS ---\n")
    from tests.integration.test_api import TestHealthEndpoints, TestCampaignAPI, TestTenantAPI, TestAIContentAPI, TestAnalyticsAPI, TestSchedulerAPI, TestNotificationsAPI
    
    results = {"passed": 0, "failed": 0}
    test_classes = [TestHealthEndpoints(), TestCampaignAPI(), TestTenantAPI(), TestAIContentAPI(), TestAnalyticsAPI(), TestSchedulerAPI(), TestNotificationsAPI()]
    
    for tc in test_classes:
        for method in dir(tc):
            if method.startswith("test_"):
                try:
                    getattr(tc, method)()
                    print(f"  [OK] {tc.__class__.__name__}.{method}")
                    results["passed"] += 1
                except Exception as e:
                    print(f"  [FAIL] {tc.__class__.__name__}.{method}: {e}")
                    results["failed"] += 1
    return results


def run_e2e_tests():
    print("\n--- E2E TESTS ---\n")
    from tests.e2e.test_workflows import TestCampaignWorkflow, TestAIWorkflow, TestAnalyticsWorkflow
    
    results = {"passed": 0, "failed": 0}
    test_classes = [TestCampaignWorkflow(), TestAIWorkflow(), TestAnalyticsWorkflow()]
    
    for tc in test_classes:
        for method in dir(tc):
            if method.startswith("test_"):
                try:
                    getattr(tc, method)()
                    print(f"  [OK] {tc.__class__.__name__}.{method}")
                    results["passed"] += 1
                except Exception as e:
                    print(f"  [FAIL] {tc.__class__.__name__}.{method}: {e}")
                    results["failed"] += 1
    return results


def main():
    print("\n" + "=" * 70)
    print(" NADAKKI MARKETING SUITE - COMPLETE TEST SUITE v5.1")
    print("=" * 70)
    
    unit = run_unit_tests()
    integration = run_integration_tests()
    e2e = run_e2e_tests()
    
    total_passed = unit["passed"] + integration["passed"] + e2e["passed"]
    total_failed = unit["failed"] + integration["failed"] + e2e["failed"]
    total = total_passed + total_failed
    
    print("\n" + "=" * 70)
    print(" FINAL RESULTS")
    print("=" * 70)
    print(f"\n  Unit:        {unit['passed']} passed, {unit['failed']} failed")
    print(f"  Integration: {integration['passed']} passed, {integration['failed']} failed")
    print(f"  E2E:         {e2e['passed']} passed, {e2e['failed']} failed")
    print(f"\n  TOTAL: {total_passed} passed, {total_failed} failed ({total} tests)")
    
    if total_failed == 0:
        print("\n  ✅ ALL TESTS PASSED!")
    else:
        print(f"\n  ⚠️  {total_failed} TESTS FAILED")
    
    print("=" * 70 + "\n")
    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
