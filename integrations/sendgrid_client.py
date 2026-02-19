"""
Nadakki AI Suite - Async SendGrid Client
DRY_RUN by default unless SENDGRID_LIVE=true.
"""
import os
import logging
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger("SendGridClient")


class AsyncSendGridClient:
    """Async client for SendGrid email API."""

    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, tenant_slug: Optional[str] = None):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv(
            "SENDGRID_FROM_EMAIL", "ramonalmontesoriano@gmail.com"
        )
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Nadakki AI Suite")
        self.live = os.getenv("SENDGRID_LIVE", "false").lower() == "true"
        self.tenant_slug = tenant_slug

    async def _tenant_sendgrid_live(self) -> bool:
        """Check per-tenant sendgrid_live_enabled from DB."""
        if not self.tenant_slug:
            return False
        try:
            from services.db import db_available, get_session
            if not db_available():
                return False
            async with get_session() as session:
                from sqlalchemy import text
                result = await session.execute(
                    text(
                        "SELECT tc.sendgrid_live_enabled FROM tenant_config tc "
                        "JOIN tenants t ON t.id = tc.tenant_id "
                        "WHERE t.slug = :slug"
                    ),
                    {"slug": self.tenant_slug},
                )
                row = result.first()
                return bool(row and row[0])
        except Exception:
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an email via SendGrid.

        Returns dry_run result unless SENDGRID_LIVE=true (env) AND
        tenant_config.sendgrid_live_enabled=true (DB).
        """
        tenant_live = await self._tenant_sendgrid_live() if self.live else False
        if not self.live or not tenant_live:
            logger.info(f"[DRY_RUN] Email to {to}: {subject}")
            return {
                "dry_run": True,
                "to": to,
                "subject": subject,
                "from_email": self.from_email,
            }

        if not self.api_key:
            return {"success": False, "error": "SENDGRID_API_KEY not configured"}

        content_list = [{"type": "text/html", "value": html_content}]
        if text_content:
            content_list.insert(0, {"type": "text/plain", "value": text_content})

        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self.from_email, "name": self.from_name},
            "subject": subject,
            "content": content_list,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    self.SENDGRID_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                return {
                    "success": resp.status_code == 202,
                    "status_code": resp.status_code,
                }
        except httpx.TimeoutException:
            return {"success": False, "error": "SendGrid request timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
