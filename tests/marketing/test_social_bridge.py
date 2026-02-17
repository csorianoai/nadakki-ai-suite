"""Tests for Social Bridge - DRY_RUN mode."""
import os
import pytest
import asyncio


@pytest.fixture(autouse=True)
def force_dry_run(monkeypatch):
    """Ensure DRY_RUN mode for all tests."""
    monkeypatch.setenv("META_POST_LIVE", "false")


def test_social_bridge_import():
    from agents.marketing.bridges.social_bridge import SocialBridge
    assert SocialBridge is not None


def test_social_bridge_init():
    from agents.marketing.bridges.social_bridge import SocialBridge
    bridge = SocialBridge(tenant_id="test_tenant")
    assert bridge.tenant_id == "test_tenant"
    assert bridge.page_id == os.getenv("FACEBOOK_PAGE_ID", "59633914943")


@pytest.mark.asyncio
async def test_publish_dry_run():
    from agents.marketing.bridges.social_bridge import SocialBridge
    bridge = SocialBridge(tenant_id="test_tenant")
    result = await bridge.publish(
        platform="meta",
        content="Test post content for Nadakki",
    )
    assert result["dry_run"] is True
    assert result["platform"] == "meta"
    assert "would_publish" in result


@pytest.mark.asyncio
async def test_get_status():
    from agents.marketing.bridges.social_bridge import SocialBridge
    bridge = SocialBridge(tenant_id="test_tenant")
    status = await bridge.get_status()
    assert status["tenant_id"] == "test_tenant"
    assert "meta" in status["platforms"]


def test_operational_wrapper_import():
    from agents.marketing.bridges.operational_wrapper import OperationalWrapper
    assert OperationalWrapper is not None


@pytest.mark.asyncio
async def test_operational_wrapper_execute():
    from agents.marketing.bridges.social_bridge import SocialBridge
    from agents.marketing.bridges.operational_wrapper import OperationalWrapper

    class MockAgent:
        def execute(self, input_data):
            return {"content": "Generated post content", "score": 0.95}

    bridge = SocialBridge(tenant_id="test_tenant")
    wrapper = OperationalWrapper(agent=MockAgent(), bridge=bridge)

    result = await wrapper.execute({
        "auto_publish": True,
        "platform": "meta",
    })

    assert "published" in result
    assert result["published"] is True  # dry_run counts as published
    assert result["publish_result"]["dry_run"] is True


@pytest.mark.asyncio
async def test_operational_wrapper_no_publish():
    from agents.marketing.bridges.operational_wrapper import OperationalWrapper

    class MockAgent:
        def execute(self, input_data):
            return {"content": "test", "score": 0.9}

    wrapper = OperationalWrapper(agent=MockAgent(), bridge=None)
    result = await wrapper.execute({"auto_publish": False})
    assert result["published"] is False
