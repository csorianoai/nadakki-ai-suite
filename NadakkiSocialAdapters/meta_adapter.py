"""
NadakkiSocialAdapters/meta_adapter.py
Meta Adapter para NADAKKI AI Suite
"""

import os
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PublishResult:
    success: bool
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    platform: str = ""
    timestamp: str = ""

class MetaAdapter:
    def __init__(self, page_id: str = None, access_token: str = None, tenant_id: str = "default"):
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.tenant_id = tenant_id
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish_facebook_post(self, message: str, link: str = None, picture_url: str = None) -> PublishResult:
        url = f"{self.base_url}/{self.page_id}/feed"
        
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        
        if link:
            payload["link"] = link
        if picture_url:
            payload["picture"] = picture_url
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                
                return PublishResult(
                    success=True,
                    post_id=post_id,
                    url=f"https://facebook.com/{post_id}",
                    platform="facebook",
                    timestamp=datetime.utcnow().isoformat(),
                    message="Post publicado exitosamente"
                )
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                
                return PublishResult(
                    success=False,
                    error=error_msg,
                    platform="facebook",
                    timestamp=datetime.utcnow().isoformat()
                )
        except Exception as e:
            return PublishResult(
                success=False,
                error=str(e),
                platform="facebook",
                timestamp=datetime.utcnow().isoformat()
            )

    def get_facebook_comments(self, post_id: str = None, limit: int = 10) -> List[Dict]:
        if post_id:
            endpoint = f"{self.base_url}/{post_id}/comments"
        else:
            endpoint = f"{self.base_url}/{self.page_id}/comments"
        
        try:
            response = requests.get(
                endpoint,
                params={
                    "fields": "id,message,from,created_time,like_count",
                    "limit": limit,
                    "access_token": self.access_token
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                return []
        except Exception as e:
            return []

    def reply_facebook_comment(self, comment_id: str, message: str) -> Tuple[bool, str]:
        url = f"{self.base_url}/{comment_id}/comments"
        
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                reply_id = response.json().get("id")
                return True, reply_id
            else:
                error_msg = response.json().get("error", {}).get("message")
                return False, error_msg
        except Exception as e:
            return False, str(e)

_meta_adapter_instance = None

def get_meta_adapter(tenant_id: str = "default") -> MetaAdapter:
    global _meta_adapter_instance
    if _meta_adapter_instance is None:
        _meta_adapter_instance = MetaAdapter(tenant_id=tenant_id)
    return _meta_adapter_instance

if __name__ == "__main__":
    adapter = get_meta_adapter()
    result = adapter.publish_facebook_post(
        message="Hello from NADAKKI! 🚀",
        link="https://nadakiexcursions.com"
    )
    print("Publish Result:", result)
