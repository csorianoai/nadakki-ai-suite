"""
NADAKKI AI SUITE - META EXECUTOR
Executor para Facebook e Instagram via Meta Graph API.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# aiohttp es opcional - solo necesario para ejecución real
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

from .base_executor import (
    BaseExecutor, ActionRequest, ExecutionResult,
    ExecutionStatus, ActionRisk, register_executor
)


class MetaExecutor(BaseExecutor):
    """
    Executor para Meta (Facebook + Instagram).
    
    Requiere:
    - APP_ID: ID de la aplicación Meta
    - APP_SECRET: Secret de la aplicación
    - ACCESS_TOKEN: Token de acceso (page token o user token)
    - PAGE_ID: ID de la página de Facebook (opcional)
    - INSTAGRAM_ACCOUNT_ID: ID de la cuenta de Instagram (opcional)
    """
    
    EXECUTOR_NAME = "meta"
    SUPPORTED_ACTIONS = [
        # Facebook
        "publish_facebook_post",
        "schedule_facebook_post",
        "reply_facebook_comment",
        "create_facebook_ad",
        "update_facebook_ad",
        "pause_facebook_ad",
        "get_facebook_insights",
        
        # Instagram
        "publish_instagram_post",
        "publish_instagram_story",
        "reply_instagram_comment",
        "get_instagram_insights",
        
        # General
        "get_page_info",
        "get_audience_insights"
    ]
    
    DEFAULT_RISK_LEVELS = {
        "publish_facebook_post": ActionRisk.LOW,
        "schedule_facebook_post": ActionRisk.LOW,
        "reply_facebook_comment": ActionRisk.LOW,
        "create_facebook_ad": ActionRisk.HIGH,
        "update_facebook_ad": ActionRisk.HIGH,
        "pause_facebook_ad": ActionRisk.MEDIUM,
        "publish_instagram_post": ActionRisk.LOW,
        "publish_instagram_story": ActionRisk.LOW,
        "reply_instagram_comment": ActionRisk.LOW,
        "get_facebook_insights": ActionRisk.LOW,
        "get_instagram_insights": ActionRisk.LOW,
        "get_page_info": ActionRisk.LOW,
        "get_audience_insights": ActionRisk.LOW
    }
    
    API_VERSION = "v18.0"
    BASE_URL = "https://graph.facebook.com"
    
    def __init__(self, tenant_id: str, config: Dict[str, Any] = None):
        super().__init__(tenant_id, config)
        
        # Credenciales
        self.app_id = config.get("APP_ID") if config else None
        self.app_secret = config.get("APP_SECRET") if config else None
        self.access_token = config.get("ACCESS_TOKEN") if config else None
        self.page_id = config.get("PAGE_ID") if config else None
        self.instagram_account_id = config.get("INSTAGRAM_ACCOUNT_ID") if config else None
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> bool:
        """Conectar y validar credenciales"""
        if not AIOHTTP_AVAILABLE:
            print(f"[MetaExecutor] aiohttp no disponible - usando modo mock")
            self.is_connected = True
            return True
        
        try:
            if not self.access_token:
                print(f"[MetaExecutor] No access token configured")
                return False
            
            self._session = aiohttp.ClientSession()
            
            # Verificar token
            url = f"{self.BASE_URL}/{self.API_VERSION}/me"
            params = {"access_token": self.access_token}
            
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.is_connected = True
                    print(f"[MetaExecutor] Conectado como: {data.get('name', 'Unknown')}")
                    return True
                else:
                    error = await response.json()
                    print(f"[MetaExecutor] Error de conexión: {error}")
                    return False
                    
        except Exception as e:
            print(f"[MetaExecutor] Error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Cerrar conexión"""
        if self._session:
            await self._session.close()
            self._session = None
        self.is_connected = False
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de la conexión"""
        if not self.is_connected or not self._session:
            return {
                "status": "disconnected",
                "executor": self.EXECUTOR_NAME,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/me"
            params = {"access_token": self.access_token}
            
            async with self._session.get(url, params=params) as response:
                healthy = response.status == 200
                return {
                    "status": "healthy" if healthy else "unhealthy",
                    "executor": self.EXECUTOR_NAME,
                    "response_code": response.status,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_action(self, request: ActionRequest) -> ExecutionResult:
        """Ejecutar acción específica de Meta"""
        action_map = {
            "publish_facebook_post": self._publish_facebook_post,
            "schedule_facebook_post": self._schedule_facebook_post,
            "reply_facebook_comment": self._reply_facebook_comment,
            "publish_instagram_post": self._publish_instagram_post,
            "get_facebook_insights": self._get_facebook_insights,
            "get_instagram_insights": self._get_instagram_insights,
            "get_page_info": self._get_page_info
        }
        
        handler = action_map.get(request.action_type)
        
        if handler:
            return await handler(request)
        else:
            # Acción no implementada aún
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=f"Acción {request.action_type} aún no implementada"
            )
    
    async def _publish_facebook_post(self, request: ActionRequest) -> ExecutionResult:
        """Publicar post en Facebook"""
        params = request.params
        message = params.get("message", "")
        link = params.get("link")
        page_id = params.get("page_id", self.page_id)
        
        if not page_id:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="page_id no configurado"
            )
        
        if not message and not link:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="Se requiere message o link"
            )
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{page_id}/feed"
            data = {
                "message": message,
                "access_token": self.access_token
            }
            if link:
                data["link"] = link
            
            async with self._session.post(url, data=data) as response:
                result = await response.json()
                
                if response.status == 200 and "id" in result:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        external_id=result["id"],
                        result_data={
                            "post_id": result["id"],
                            "message": message[:100],
                            "platform": "facebook"
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _schedule_facebook_post(self, request: ActionRequest) -> ExecutionResult:
        """Programar post en Facebook"""
        params = request.params
        message = params.get("message", "")
        scheduled_time = params.get("scheduled_time")  # Unix timestamp
        page_id = params.get("page_id", self.page_id)
        
        if not scheduled_time:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="scheduled_time requerido (Unix timestamp)"
            )
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{page_id}/feed"
            data = {
                "message": message,
                "published": "false",
                "scheduled_publish_time": scheduled_time,
                "access_token": self.access_token
            }
            
            async with self._session.post(url, data=data) as response:
                result = await response.json()
                
                if response.status == 200 and "id" in result:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        external_id=result["id"],
                        result_data={
                            "post_id": result["id"],
                            "scheduled_time": scheduled_time,
                            "status": "scheduled"
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _reply_facebook_comment(self, request: ActionRequest) -> ExecutionResult:
        """Responder a un comentario en Facebook"""
        params = request.params
        comment_id = params.get("comment_id")
        message = params.get("message", "")
        
        if not comment_id or not message:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="comment_id y message requeridos"
            )
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{comment_id}/comments"
            data = {
                "message": message,
                "access_token": self.access_token
            }
            
            async with self._session.post(url, data=data) as response:
                result = await response.json()
                
                if response.status == 200 and "id" in result:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        external_id=result["id"],
                        result_data={
                            "reply_id": result["id"],
                            "parent_comment_id": comment_id
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _publish_instagram_post(self, request: ActionRequest) -> ExecutionResult:
        """Publicar en Instagram (requiere imagen)"""
        params = request.params
        image_url = params.get("image_url")
        caption = params.get("caption", "")
        ig_account_id = params.get("instagram_account_id", self.instagram_account_id)
        
        if not ig_account_id:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="instagram_account_id no configurado"
            )
        
        if not image_url:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="image_url requerido para Instagram"
            )
        
        try:
            # Paso 1: Crear contenedor de media
            url = f"{self.BASE_URL}/{self.API_VERSION}/{ig_account_id}/media"
            data = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            
            async with self._session.post(url, data=data) as response:
                result = await response.json()
                
                if response.status != 200 or "id" not in result:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=f"Error creando media: {result}"
                    )
                
                creation_id = result["id"]
            
            # Paso 2: Publicar el contenedor
            url = f"{self.BASE_URL}/{self.API_VERSION}/{ig_account_id}/media_publish"
            data = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            
            async with self._session.post(url, data=data) as response:
                result = await response.json()
                
                if response.status == 200 and "id" in result:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        external_id=result["id"],
                        result_data={
                            "media_id": result["id"],
                            "platform": "instagram",
                            "caption": caption[:100]
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _get_facebook_insights(self, request: ActionRequest) -> ExecutionResult:
        """Obtener insights de Facebook"""
        params = request.params
        page_id = params.get("page_id", self.page_id)
        metrics = params.get("metrics", ["page_impressions", "page_engaged_users"])
        period = params.get("period", "day")
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{page_id}/insights"
            query_params = {
                "metric": ",".join(metrics),
                "period": period,
                "access_token": self.access_token
            }
            
            async with self._session.get(url, params=query_params) as response:
                result = await response.json()
                
                if response.status == 200:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        result_data={
                            "insights": result.get("data", []),
                            "period": period,
                            "metrics": metrics
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _get_instagram_insights(self, request: ActionRequest) -> ExecutionResult:
        """Obtener insights de Instagram"""
        params = request.params
        ig_account_id = params.get("instagram_account_id", self.instagram_account_id)
        metrics = params.get("metrics", ["impressions", "reach", "profile_views"])
        period = params.get("period", "day")
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{ig_account_id}/insights"
            query_params = {
                "metric": ",".join(metrics),
                "period": period,
                "access_token": self.access_token
            }
            
            async with self._session.get(url, params=query_params) as response:
                result = await response.json()
                
                if response.status == 200:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        result_data={
                            "insights": result.get("data", []),
                            "platform": "instagram"
                        }
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )
    
    async def _get_page_info(self, request: ActionRequest) -> ExecutionResult:
        """Obtener información de la página"""
        params = request.params
        page_id = params.get("page_id", self.page_id)
        
        try:
            url = f"{self.BASE_URL}/{self.API_VERSION}/{page_id}"
            query_params = {
                "fields": "id,name,fan_count,followers_count,about,category",
                "access_token": self.access_token
            }
            
            async with self._session.get(url, params=query_params) as response:
                result = await response.json()
                
                if response.status == 200:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        result_data=result
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        action_type=request.action_type,
                        executor=self.EXECUTOR_NAME,
                        error=result.get("error", {}).get("message", str(result))
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=str(e)
            )


# Registrar el executor
register_executor("meta", MetaExecutor)
