"""
NADAKKI AI SUITE - Facebook Executor
Publicar posts en Facebook Pages
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_social import BaseSocialExecutor, PostRequest, PostResponse

class FacebookExecutor(BaseSocialExecutor):
    """Executor para Facebook Pages"""
    
    def __init__(self, access_token: str = None, page_id: str = None):
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.platform = "facebook"
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def post(self, request: PostRequest) -> PostResponse:
        """Publicar en Facebook Page"""
        if not self.access_token or not self.page_id:
            return PostResponse(
                success=False,
                platform=self.platform,
                error="Missing access_token or page_id"
            )
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        data = {
            "message": request.content,
            "access_token": self.access_token
        }
        
        # Si hay imagen, usar endpoint de photos
        if request.media_urls:
            url = f"{self.base_url}/{self.page_id}/photos"
            data["url"] = request.media_urls[0]
        
        # Si es programado
        if request.scheduled_time:
            data["published"] = "false"
            data["scheduled_publish_time"] = int(request.scheduled_time.timestamp())
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, timeout=30.0)
                result = response.json()
                
                if "error" in result:
                    return PostResponse(
                        success=False,
                        platform=self.platform,
                        error=result["error"].get("message", "Unknown error"),
                        metadata=result
                    )
                
                post_id = result.get("id") or result.get("post_id")
                
                return PostResponse(
                    success=True,
                    post_id=post_id,
                    platform=self.platform,
                    url=f"https://facebook.com/{post_id}" if post_id else None,
                    metadata={"response": result, "tenant_id": request.tenant_id}
                )
                
        except Exception as e:
            return PostResponse(
                success=False,
                platform=self.platform,
                error=str(e)
            )
    
    async def get_insights(self, post_id: str) -> Dict[str, Any]:
        """Obtener metricas de un post"""
        url = f"{self.base_url}/{post_id}/insights"
        params = {
            "metric": "post_impressions,post_engagements,post_reactions_by_type_total",
            "access_token": self.access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_post(self, post_id: str) -> bool:
        """Eliminar un post"""
        url = f"{self.base_url}/{post_id}"
        params = {"access_token": self.access_token}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params, timeout=30.0)
                result = response.json()
                return result.get("success", False)
        except:
            return False
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Obtener info de la pagina"""
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "name,fan_count,followers_count,about",
            "access_token": self.access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
