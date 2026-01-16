"""
NADAKKI AI SUITE - Social Manager
Gestiona publicaciones en multiples redes sociales
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from .base_social import PostRequest, PostResponse
from .facebook_executor import FacebookExecutor
from .instagram_executor import InstagramExecutor

class SocialManager:
    """Manager unificado para todas las redes sociales"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.executors = {}
        self.stats = {"posts": 0, "success": 0, "failed": 0, "by_platform": {}}
        self._init_executors()
        self._initialized = True
    
    def _init_executors(self):
        """Inicializar executors disponibles"""
        print("Inicializando Social Executors...")
        
        # Facebook
        if os.getenv("FACEBOOK_ACCESS_TOKEN") and os.getenv("FACEBOOK_PAGE_ID"):
            self.executors["facebook"] = FacebookExecutor()
            print("   OK Facebook")
        
        # Instagram
        if os.getenv("FACEBOOK_ACCESS_TOKEN") and os.getenv("INSTAGRAM_BUSINESS_ID"):
            self.executors["instagram"] = InstagramExecutor()
            print("   OK Instagram")
    
    async def post(self, content: str, platforms: List[str] = None, media_urls: List[str] = None, tenant_id: str = "default") -> Dict[str, PostResponse]:
        """Publicar en una o mas plataformas"""
        platforms = platforms or ["facebook"]
        results = {}
        
        request = PostRequest(
            content=content,
            media_urls=media_urls or [],
            tenant_id=tenant_id
        )
        
        for platform in platforms:
            executor = self.executors.get(platform)
            if not executor:
                results[platform] = PostResponse(
                    success=False,
                    platform=platform,
                    error=f"Platform {platform} not configured"
                )
                continue
            
            response = await executor.post(request)
            results[platform] = response
            
            # Update stats
            self.stats["posts"] += 1
            if response.success:
                self.stats["success"] += 1
            else:
                self.stats["failed"] += 1
            
            if platform not in self.stats["by_platform"]:
                self.stats["by_platform"][platform] = {"posts": 0, "success": 0}
            self.stats["by_platform"][platform]["posts"] += 1
            if response.success:
                self.stats["by_platform"][platform]["success"] += 1
        
        return results
    
    async def post_with_ai(self, topic: str, platforms: List[str] = None, tenant_id: str = "default", model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Generar contenido con IA y publicar"""
        from ..llm_executor import get_llm
        
        llm = get_llm()
        
        # Generar contenido
        prompt = f"""Crea un post para redes sociales sobre: {topic}
        
Requisitos:
- Maximo 280 caracteres
- Incluye 2-3 emojis relevantes
- Incluye 2-3 hashtags
- Tono profesional pero amigable
- En espanol

Responde SOLO con el texto del post, nada mas."""
        
        ai_result = await llm.generate(prompt, model=model, tenant_id=tenant_id)
        content = ai_result["content"]
        
        # Publicar
        post_results = await self.post(content, platforms, tenant_id=tenant_id)
        
        return {
            "content_generated": content,
            "ai_model": model,
            "ai_cost": ai_result["cost"],
            "post_results": {p: {"success": r.success, "post_id": r.post_id, "url": r.url, "error": r.error} for p, r in post_results.items()}
        }
    
    def get_stats(self) -> Dict:
        return self.stats
    
    def get_platforms(self) -> List[str]:
        return list(self.executors.keys())

# Singleton
_social = None

def get_social() -> SocialManager:
    global _social
    if _social is None:
        _social = SocialManager()
    return _social

async def post(content: str, **kwargs) -> Dict[str, PostResponse]:
    return await get_social().post(content, **kwargs)

async def post_with_ai(topic: str, **kwargs) -> Dict[str, Any]:
    return await get_social().post_with_ai(topic, **kwargs)
