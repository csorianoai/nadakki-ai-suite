"""
═══════════════════════════════════════════════════════════════════════════════════════════════════
META EXECUTOR - NADAKKI AI SUITE
═══════════════════════════════════════════════════════════════════════════════════════════════════

Executor para acciones en Facebook e Instagram usando la Graph API de Meta.

Acciones soportadas:
  • PUBLISH_CONTENT - Publicar posts en Facebook/Instagram
  • POST_SOCIAL - Publicar en redes sociales
  • REPLY_COMMENT - Responder a comentarios

═══════════════════════════════════════════════════════════════════════════════════════════════════
"""

import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

try:
    import httpx
except ImportError:
    httpx = None

# Importar tipos del wrapper
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wrappers.operative_wrapper import BaseExecutor, ActionType


class MetaExecutor(BaseExecutor):
    """
    Executor para Facebook e Instagram (Meta Graph API).
    """
    
    API_VERSION = "v18.0"
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(f"MetaExecutor.{tenant_id}")
        
        # Cargar credenciales (en producción, usar vault seguro)
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.instagram_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    
    def get_supported_actions(self) -> List[ActionType]:
        return [
            ActionType.PUBLISH_CONTENT,
            ActionType.POST_SOCIAL,
            ActionType.REPLY_COMMENT
        ]
    
    async def execute(
        self,
        action_type: ActionType,
        data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Ejecuta una acción en Meta (Facebook/Instagram).
        """
        self.logger.info(f"Executing {action_type.value} for tenant {tenant_id}")
        
        # Actualizar tenant_id para esta ejecución
        self.tenant_id = tenant_id
        
        # Router de acciones
        if action_type in [ActionType.PUBLISH_CONTENT, ActionType.POST_SOCIAL]:
            return await self._publish_post(data)
        elif action_type == ActionType.REPLY_COMMENT:
            return await self._reply_comment(data)
        else:
            return {"error": f"Unsupported action: {action_type.value}"}
    
    async def _publish_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publica un post en Facebook.
        """
        content = data.get("content", "")
        platform = data.get("platform", "facebook")
        
        if not content:
            return {"success": False, "error": "No content provided"}
        
        if not self.access_token:
            return {"success": False, "error": "FACEBOOK_ACCESS_TOKEN not configured"}
        
        # Usar requests o httpx
        http_client = requests if requests else httpx
        if not http_client:
            return {"success": False, "error": "No HTTP client available (install requests or httpx)"}
        
        try:
            if platform == "facebook":
                url = f"{self.BASE_URL}/{self.page_id}/feed"
                payload = {
                    "message": content,
                    "access_token": self.access_token
                }
                
                response = http_client.post(url, data=payload, timeout=30)
                result = response.json() if hasattr(response, 'json') else response.json
                
                if response.status_code == 200:
                    post_id = result.get("id", "unknown")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "platform": "facebook",
                        "url": f"https://facebook.com/{post_id}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", {}).get("message", "Unknown error"),
                        "platform": "facebook"
                    }
            
            elif platform == "instagram":
                # Instagram requiere proceso de 2 pasos
                image_url = data.get("image_url")
                if not image_url:
                    return {"success": False, "error": "Instagram requires image_url"}
                
                # Paso 1: Crear container
                container_url = f"{self.BASE_URL}/{self.instagram_account_id}/media"
                container_payload = {
                    "image_url": image_url,
                    "caption": content,
                    "access_token": self.access_token
                }
                
                container_response = http_client.post(container_url, data=container_payload, timeout=30)
                container_result = container_response.json() if hasattr(container_response, 'json') else container_response.json
                
                if container_response.status_code != 200:
                    return {"success": False, "error": container_result.get("error", {}).get("message")}
                
                creation_id = container_result.get("id")
                
                # Paso 2: Publicar
                publish_url = f"{self.BASE_URL}/{self.instagram_account_id}/media_publish"
                publish_payload = {
                    "creation_id": creation_id,
                    "access_token": self.access_token
                }
                
                publish_response = http_client.post(publish_url, data=publish_payload, timeout=30)
                publish_result = publish_response.json() if hasattr(publish_response, 'json') else publish_response.json
                
                if publish_response.status_code == 200:
                    return {
                        "success": True,
                        "post_id": publish_result.get("id"),
                        "platform": "instagram",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {"success": False, "error": publish_result.get("error", {}).get("message")}
            
            else:
                return {"success": False, "error": f"Unsupported platform: {platform}"}
                
        except Exception as e:
            self.logger.error(f"Error publishing to {platform}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _reply_comment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Responde a un comentario en Facebook.
        """
        comment_id = data.get("comment_id")
        reply_text = data.get("content") or data.get("reply_text")
        
        if not comment_id or not reply_text:
            return {"success": False, "error": "comment_id and reply_text required"}
        
        http_client = requests if requests else httpx
        if not http_client:
            return {"success": False, "error": "No HTTP client available"}
        
        try:
            url = f"{self.BASE_URL}/{comment_id}/comments"
            payload = {
                "message": reply_text,
                "access_token": self.access_token
            }
            
            response = http_client.post(url, data=payload, timeout=30)
            result = response.json() if hasattr(response, 'json') else response.json
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "reply_id": result.get("id"),
                    "original_comment_id": comment_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": result.get("error", {}).get("message")}
                
        except Exception as e:
            self.logger.error(f"Error replying to comment: {e}")
            return {"success": False, "error": str(e)}


# Mock executor para testing sin API real
class MockMetaExecutor(BaseExecutor):
    """
    Executor mock para testing sin conexión real a Meta.
    """
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.execution_log = []
    
    def get_supported_actions(self) -> List[ActionType]:
        return [
            ActionType.PUBLISH_CONTENT,
            ActionType.POST_SOCIAL,
            ActionType.REPLY_COMMENT
        ]
    
    async def execute(
        self,
        action_type: ActionType,
        data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """Mock execution - logs action without real API call"""
        execution = {
            "action_type": action_type.value,
            "tenant_id": tenant_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.execution_log.append(execution)
        
        return {
            "success": True,
            "mock": True,
            "post_id": f"mock_{datetime.utcnow().timestamp()}",
            "message": f"[MOCK] Would execute {action_type.value}",
            "content_preview": str(data.get("content", ""))[:100]
        }


__all__ = ['MetaExecutor', 'MockMetaExecutor']
