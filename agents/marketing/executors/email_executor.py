"""
═══════════════════════════════════════════════════════════════════════════════════════════════════
EMAIL EXECUTOR - NADAKKI AI SUITE
═══════════════════════════════════════════════════════════════════════════════════════════════════

Executor para envío de emails usando SendGrid o SMTP.

Acciones soportadas:
  • SEND_EMAIL - Enviar emails transaccionales y de marketing

═══════════════════════════════════════════════════════════════════════════════════════════════════
"""

import os
import logging
from typing import Any, Dict, List
from datetime import datetime

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wrappers.operative_wrapper import BaseExecutor, ActionType


class EmailExecutor(BaseExecutor):
    """
    Executor para envío de emails.
    Soporta SendGrid (preferido) y SMTP como fallback.
    """
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(f"EmailExecutor.{tenant_id}")
        
        # Credenciales
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@nadakki.com")
        
        # SMTP fallback
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    def get_supported_actions(self) -> List[ActionType]:
        return [ActionType.SEND_EMAIL]
    
    async def execute(
        self,
        action_type: ActionType,
        data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """Ejecuta envío de email"""
        if action_type != ActionType.SEND_EMAIL:
            return {"success": False, "error": f"Unsupported action: {action_type.value}"}
        
        to_email = data.get("to_email") or data.get("recipient")
        subject = data.get("subject", "Mensaje de NADAKKI AI Suite")
        content = data.get("content") or data.get("body") or data.get("message", "")
        html_content = data.get("html_content")
        
        if not to_email:
            return {"success": False, "error": "to_email is required"}
        
        # Intentar SendGrid primero
        if SENDGRID_AVAILABLE and self.sendgrid_api_key:
            return await self._send_via_sendgrid(to_email, subject, content, html_content)
        
        # Fallback a SMTP
        if SMTP_AVAILABLE and self.smtp_user:
            return await self._send_via_smtp(to_email, subject, content, html_content)
        
        return {
            "success": False,
            "error": "No email service configured (need SENDGRID_API_KEY or SMTP credentials)"
        }
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str = None
    ) -> Dict[str, Any]:
        """Envía email via SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=content,
                html_content=html_content or content
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                return {
                    "success": True,
                    "method": "sendgrid",
                    "to": to_email,
                    "subject": subject,
                    "status_code": response.status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"SendGrid returned {response.status_code}",
                    "method": "sendgrid"
                }
                
        except Exception as e:
            self.logger.error(f"SendGrid error: {e}")
            return {"success": False, "error": str(e), "method": "sendgrid"}
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str = None
    ) -> Dict[str, Any]:
        """Envía email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            msg.attach(MIMEText(content, 'plain'))
            if html_content:
                msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            return {
                "success": True,
                "method": "smtp",
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"SMTP error: {e}")
            return {"success": False, "error": str(e), "method": "smtp"}


class MockEmailExecutor(BaseExecutor):
    """Mock executor para testing"""
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.sent_emails = []
    
    def get_supported_actions(self) -> List[ActionType]:
        return [ActionType.SEND_EMAIL]
    
    async def execute(
        self,
        action_type: ActionType,
        data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        email = {
            "to": data.get("to_email"),
            "subject": data.get("subject"),
            "content": data.get("content", "")[:100],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.sent_emails.append(email)
        
        return {
            "success": True,
            "mock": True,
            "message": f"[MOCK] Would send email to {email['to']}",
            **email
        }


__all__ = ['EmailExecutor', 'MockEmailExecutor']
