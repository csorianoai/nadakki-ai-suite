"""Tests for Email Bridge and SendGrid Client - DRY_RUN only."""
import os
import pytest


@pytest.fixture(autouse=True)
def force_dry_run(monkeypatch):
    """Ensure DRY_RUN mode."""
    monkeypatch.setenv("SENDGRID_LIVE", "false")


def test_sendgrid_client_import():
    from integrations.sendgrid_client import AsyncSendGridClient
    assert AsyncSendGridClient is not None


def test_sendgrid_client_init():
    from integrations.sendgrid_client import AsyncSendGridClient
    client = AsyncSendGridClient()
    assert client.live is False
    assert client.from_email == os.getenv(
        "SENDGRID_FROM_EMAIL", "ramonalmontesoriano@gmail.com"
    )


@pytest.mark.asyncio
async def test_sendgrid_dry_run():
    from integrations.sendgrid_client import AsyncSendGridClient
    client = AsyncSendGridClient()
    result = await client.send_email(
        to="test@example.com",
        subject="Test Subject",
        html_content="<h1>Hello</h1>",
    )
    assert result["dry_run"] is True
    assert result["to"] == "test@example.com"
    assert result["subject"] == "Test Subject"


def test_email_bridge_import():
    from agents.marketing.bridges.email_bridge import EmailBridge, EmailOperationalWrapper
    assert EmailBridge is not None
    assert EmailOperationalWrapper is not None


@pytest.mark.asyncio
async def test_email_bridge_send():
    from integrations.sendgrid_client import AsyncSendGridClient
    from agents.marketing.bridges.email_bridge import EmailBridge

    client = AsyncSendGridClient()
    bridge = EmailBridge(sendgrid_client=client)

    result = await bridge.send(
        to="user@example.com",
        subject="Campaign Update",
        html_content="<p>Your campaign is live!</p>",
    )
    assert result["dry_run"] is True


@pytest.mark.asyncio
async def test_email_bridge_campaign():
    from integrations.sendgrid_client import AsyncSendGridClient
    from agents.marketing.bridges.email_bridge import EmailBridge

    client = AsyncSendGridClient()
    bridge = EmailBridge(sendgrid_client=client)

    result = await bridge.send_campaign_email(
        to="user@example.com",
        campaign_data={
            "subject": "Welcome Campaign",
            "html_content": "<h1>Welcome!</h1><p>Thanks for joining.</p>",
        },
    )
    assert result["dry_run"] is True


@pytest.mark.asyncio
async def test_email_wrapper_auto_send():
    from integrations.sendgrid_client import AsyncSendGridClient
    from agents.marketing.bridges.email_bridge import EmailBridge, EmailOperationalWrapper

    class MockEmailAgent:
        def execute(self, input_data):
            return {
                "subject": "Generated Subject",
                "html_content": "<p>AI generated email</p>",
                "content": "AI generated email",
            }

    client = AsyncSendGridClient()
    bridge = EmailBridge(sendgrid_client=client)
    wrapper = EmailOperationalWrapper(agent=MockEmailAgent(), email_bridge=bridge)

    result = await wrapper.execute({
        "auto_send": True,
        "to_email": "recipient@example.com",
    })

    assert result["email_sent"] is True
    assert result["email_result"]["dry_run"] is True
