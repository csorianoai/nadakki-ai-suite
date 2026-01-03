"""Tests para campañas."""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.campaign import Campaign, CampaignStatus, CampaignObjective
from backend.services.campaign_service import CampaignService
from backend.schemas.campaign_schemas import CampaignCreate, CampaignUpdate


def run_async(coro):
    loop = asyncio.new_event_loop()
    try: return loop.run_until_complete(coro)
    finally: loop.close()


def test_campaign_creation():
    campaign = Campaign(tenant_id="t1", name="Test", objective=CampaignObjective.AWARENESS, content_text="Hello")
    assert campaign.name == "Test"
    assert campaign.status == CampaignStatus.DRAFT
    print("  [OK] Campaign creation")


def test_campaign_to_dict():
    campaign = Campaign(tenant_id="t1", name="Test", content_text="Content")
    data = campaign.to_dict()
    assert data["name"] == "Test"
    assert "id" in data
    print("  [OK] Campaign to_dict")


def test_campaign_ready_to_publish():
    c1 = Campaign(tenant_id="t1", name="Empty")
    assert not c1.is_ready_to_publish()
    c2 = Campaign(tenant_id="t1", name="Content", content_text="Hello")
    assert not c2.is_ready_to_publish()
    c3 = Campaign(tenant_id="t1", name="Ready", content_text="Hello", target_pages=[{"platform": "facebook", "page_id": "123"}])
    assert c3.is_ready_to_publish()
    print("  [OK] Campaign ready_to_publish")


def test_service_create():
    service = CampaignService()
    data = CampaignCreate(name="Service Test", objective="engagement", content_text="Test")
    campaign = run_async(service.create_campaign("t1", data))
    assert campaign.name == "Service Test"
    print("  [OK] CampaignService create")


def test_service_list():
    service = CampaignService()
    for i in range(3):
        data = CampaignCreate(name=f"Campaign {i}", content_text=f"Content {i}")
        run_async(service.create_campaign("t1", data))
    result = run_async(service.list_campaigns("t1"))
    assert result["total"] >= 3
    print("  [OK] CampaignService list")


def test_service_update():
    service = CampaignService()
    data = CampaignCreate(name="Original", content_text="Original")
    campaign = run_async(service.create_campaign("t1", data))
    update = CampaignUpdate(name="Updated")
    updated = run_async(service.update_campaign(campaign.id, "t1", update))
    assert updated.name == "Updated"
    print("  [OK] CampaignService update")


def test_service_delete():
    service = CampaignService()
    data = CampaignCreate(name="ToDelete", content_text="Delete")
    campaign = run_async(service.create_campaign("t1", data))
    result = run_async(service.delete_campaign(campaign.id, "t1"))
    assert result == True
    deleted = run_async(service.get_campaign(campaign.id, "t1"))
    assert deleted is None
    print("  [OK] CampaignService delete")


def run_all_tests():
    print("\n" + "=" * 60)
    print(" NADAKKI MARKETING - CAMPAIGN TESTS")
    print("=" * 60 + "\n")
    tests = [test_campaign_creation, test_campaign_to_dict, test_campaign_ready_to_publish, test_service_create, test_service_list, test_service_update, test_service_delete]
    passed = failed = 0
    for test in tests:
        try: test(); passed += 1
        except Exception as e: print(f"  [FAIL] {test.__name__}: {e}"); failed += 1
    print(f"\n RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    return passed, failed


if __name__ == "__main__":
    run_all_tests()
