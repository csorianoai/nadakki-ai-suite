"""
NADAKKI AI SUITE - Instagram Executor
Publicar posts en Instagram Business
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_social import BaseSocialExecutor, PostRequest, PostResponse

class InstagramExecutor(BaseSocialExecutor):
    """Executor para Instagram Business (via Facebook Graph API)"""
    
    def __init__(self, access_token: str = None, instagram_id: str = None):
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.instagram_id = instagram_id or os.getenv("INSTAGRAM_BUSINESS_ID")
        self.platform = "instagram"
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def post(self, request: PostRequest) -> PostResponse:
        """Publicar en Instagram (requiere imagen)"""
        if not self.access_token or not self.instagram_id:
            return PostResponse(
                success=False,
                platform=self.platform,
                error="Missing access_token or instagram_id"
            )
        
        if not request.media_urls:
            return PostResponse(
                success=False,
                platform=self.platform,
                error="Instagram requires at least one image URL"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                # Paso 1: Crear media container
                container_url = f"{self.base_url}/{self.instagram_id}/media"
                container_data = {
                    "image_url": request.media_urls[0],
                    "caption": request.content,
                    "access_token": self.access_token
                }
                
                container_response = await client.post(container_url, data=container_data, timeout=30.0)
                container_result = container_response.json()
                
                if "error" in container_result:
                    return PostResponse(
                        success=False,
                        platform=self.platform,
                        error=container_result["error"].get("message"),
                        metadata=container_result
                    )
                
                container_id = container_result.get("id")
                
                # Paso 2: Publicar el container
                publish_url = f"{self.base_url}/{self.instagram_id}/media_publish"
                publish_data = {
                    "creation_id": container_id,
                    "access_token": self.access_token
                }
                
                publish_response = await client.post(publish_url, data=publish_data, timeout=30.0)
                publish_result = publish_response.json()
                
                if "error" in publish_result:
                    return PostResponse(
                        success=False,
                        platform=self.platform,
                        error=publish_result["error"].get("message"),
                        metadata=publish_result
                    )
                
                post_id = publish_result.get("id")
                
                return PostResponse(
                    success=True,
                    post_id=post_id,
                    platform=self.platform,
                    url=f"https://instagram.com/p/{post_id}" if post_id else None,
                    metadata={"response": publish_result, "tenant_id": request.tenant_id}
                )
                
        except Exception as e:
            return PostResponse(
                success=False,
                platform=self.platform,
                error=str(e)
            )
    
    async def get_insights(self, post_id: str) -> Dict[str, Any]:
        """Obtener metricas de un post de Instagram"""
        url = f"{self.base_url}/{post_id}/insights"
        params = {
            "metric": "impressions,reach,engagement,likes,comments,shares,saved",
            "access_token": self.access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_post(self, post_id: str) -> bool:
        """Instagram no permite eliminar via API facilmente"""
        return False
