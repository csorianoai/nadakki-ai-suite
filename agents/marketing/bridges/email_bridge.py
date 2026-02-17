"""
Nadakki AI Suite - Email Bridge
Connects email marketing agents (emailautomationia) with SendGrid.
Decorator pattern: same as social_bridge.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("EmailBridge")


class EmailBridge:
    """Bridge between email marketing agents and SendGrid."""

    def __init__(self, sendgrid_client):
        self.client = sendgrid_client

    async def send(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email through SendGrid client."""
        return await self.client.send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_campaign_email(
        self,
        to: str,
        campaign_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send a campaign email using agent output."""
        subject = campaign_data.get("subject", "Nadakki Campaign")
        html = campaign_data.get("html_content", campaign_data.get("content", ""))
        text = campaign_data.get("text_content")

        if not html:
            return {"success": False, "error": "No email content provided"}

        return await self.send(
            to=to,
            subject=subject,
            html_content=html,
            text_content=text,
        )


class EmailOperationalWrapper:
    """Wraps email agents to auto-send via EmailBridge."""

    def __init__(self, agent, email_bridge: Optional[EmailBridge] = None):
        self.agent = agent
        self.bridge = email_bridge

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent, optionally send email."""
        if hasattr(self.agent, "execute"):
            result = self.agent.execute(input_data)
        else:
            result = {"error": "Agent has no execute method"}

        if hasattr(result, "__await__"):
            result = await result

        sent = False

        if input_data.get("auto_send") and self.bridge:
            to = input_data.get("to_email")
            if to and result.get("content") or result.get("html_content"):
                try:
                    send_result = await self.bridge.send_campaign_email(
                        to=to,
                        campaign_data=result,
                    )
                    result["email_result"] = send_result
                    sent = send_result.get("success", False) or send_result.get(
                        "dry_run", False
                    )
                except Exception as e:
                    logger.error(f"Auto-send failed: {e}")
                    result["email_result"] = {"success": False, "error": str(e)}

        result["email_sent"] = sent
        return result
