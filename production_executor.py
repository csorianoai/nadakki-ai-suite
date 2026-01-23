"""
NADAKKI AI SUITE - PRODUCTION EXECUTOR v4.0
Ejecutores reales para Meta, SendGrid, Google
"""

import os
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProductionExecutor")

class ExecutorMode(Enum):
    MOCK = "mock"
    PRODUCTION = "production"

@dataclass
class ExecutionResult:
    success: bool
    action: str
    platform: str
    data: Dict[str, Any]
    error: Optional[str] = None
    external_id: Optional[str] = None
    url: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "platform": self.platform,
            "data": self.data,
            "error": self.error,
            "external_id": self.external_id,
            "url": self.url,
            "timestamp": self.timestamp
        }

class MetaExecutor:
    """Ejecutor para Meta (Facebook/Instagram)"""
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.page_token = os.getenv("META_PAGE_ACCESS_TOKEN")
        self.page_id = os.getenv("META_PAGE_ID")
        self.mode = ExecutorMode(os.getenv("EXECUTOR_MODE", "mock"))
    
    async def publish_post(self, message: str, link: str = None) -> ExecutionResult:
        if self.mode == ExecutorMode.MOCK:
            return self._mock_result("publish_post", {"message": message})
        
        if not self.page_token:
            return ExecutionResult(False, "publish_post", "meta", {}, "META_PAGE_ACCESS_TOKEN not set")
        
        payload = {"message": message, "access_token": self.page_token}
        if link:
            payload["link"] = link
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/{self.page_id}/feed"
            async with session.post(url, data=payload) as response:
                result = await response.json()
                if "id" in result:
                    return ExecutionResult(True, "publish_post", "facebook", 
                        {"message": message}, external_id=result["id"],
                        url=f"https://facebook.com/{result['id']}")
                return ExecutionResult(False, "publish_post", "facebook", {},
                    error=result.get("error", {}).get("message", "Unknown error"))
    
    def _mock_result(self, action: str, data: Dict) -> ExecutionResult:
        import uuid
        mock_id = f"mock_{uuid.uuid4().hex[:12]}"
        return ExecutionResult(True, action, "meta_mock", data, 
            external_id=mock_id, url=f"https://mock.facebook.com/{mock_id}")

class SendGridExecutor:
    """Ejecutor para SendGrid (Email)"""
    BASE_URL = "https://api.sendgrid.com/v3"
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@nadakki.com")
        self.mode = ExecutorMode(os.getenv("EXECUTOR_MODE", "mock"))
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> ExecutionResult:
        if self.mode == ExecutorMode.MOCK:
            return self._mock_result("send_email", {"to": to_email, "subject": subject})
        
        if not self.api_key:
            return ExecutionResult(False, "send_email", "sendgrid", {}, "SENDGRID_API_KEY not set")
        
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content}]
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE_URL}/mail/send", json=payload, headers=headers) as response:
                if response.status == 202:
                    msg_id = response.headers.get("X-Message-Id", "")
                    return ExecutionResult(True, "send_email", "sendgrid",
                        {"to": to_email, "subject": subject}, external_id=msg_id)
                error = await response.text()
                return ExecutionResult(False, "send_email", "sendgrid", {}, error=error)
    
    def _mock_result(self, action: str, data: Dict) -> ExecutionResult:
        import uuid
        return ExecutionResult(True, action, "sendgrid_mock", data, 
            external_id=f"mock_email_{uuid.uuid4().hex[:8]}")

class ProductionExecutorManager:
    """Gestor central de ejecutores"""
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.meta = MetaExecutor(tenant_id)
        self.sendgrid = SendGridExecutor(tenant_id)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": os.getenv("EXECUTOR_MODE", "mock"),
            "meta_configured": bool(os.getenv("META_PAGE_ACCESS_TOKEN")),
            "sendgrid_configured": bool(os.getenv("SENDGRID_API_KEY")),
            "tenant_id": self.tenant_id
        }

def get_executor_manager(tenant_id: str = "default") -> ProductionExecutorManager:
    return ProductionExecutorManager(tenant_id)

if __name__ == "__main__":
    manager = get_executor_manager("test")
    print("Status:", manager.get_status())
