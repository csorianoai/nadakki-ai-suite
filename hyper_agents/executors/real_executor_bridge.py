"""
NADAKKI AI SUITE - REAL EXECUTOR BRIDGE
Conecta el sistema autonomo con los executors reales de redes sociales.
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Importar executors reales existentes
from agents.shared_layers.executors.social import get_social, SocialManager
from agents.shared_layers.executors.social.base_social import PostRequest, PostResponse


class RealExecutorBridge:
    """
    Puente que conecta el sistema autonomo con los executors reales.
    
    Cuando un agente decide EXECUTE_NOW, este bridge ejecuta la accion
    real en la plataforma correspondiente (Facebook, Instagram, etc.)
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.social = get_social()
        
        # Estadisticas
        self.stats = {
            "total_executions": 0,
            "successful": 0,
            "failed": 0,
            "by_platform": {},
            "by_agent": {}
        }
        
        print(f"🔌 RealExecutorBridge inicializado para tenant: {tenant_id}")
        print(f"   Plataformas disponibles: {self.social.get_platforms()}")
    
    async def execute_social_post(
        self,
        content: str,
        platforms: List[str] = None,
        media_urls: List[str] = None,
        agent_id: str = "unknown"
    ) -> Dict[str, Any]:
        """Ejecutar publicacion real en redes sociales"""
        platforms = platforms or self.social.get_platforms()
        
        if not platforms:
            return {
                "success": False,
                "error": "No hay plataformas configuradas",
                "agent_id": agent_id
            }
        
        # Publicar
        results = await self.social.post(
            content=content,
            platforms=platforms,
            media_urls=media_urls,
            tenant_id=self.tenant_id
        )
        
        # Actualizar stats
        self.stats["total_executions"] += 1
        success = all(r.success for r in results.values())
        
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        # Stats por plataforma
        for platform, result in results.items():
            if platform not in self.stats["by_platform"]:
                self.stats["by_platform"][platform] = {"total": 0, "success": 0}
            self.stats["by_platform"][platform]["total"] += 1
            if result.success:
                self.stats["by_platform"][platform]["success"] += 1
        
        # Stats por agente
        if agent_id not in self.stats["by_agent"]:
            self.stats["by_agent"][agent_id] = {"total": 0, "success": 0}
        self.stats["by_agent"][agent_id]["total"] += 1
        if success:
            self.stats["by_agent"][agent_id]["success"] += 1
        
        return {
            "success": success,
            "agent_id": agent_id,
            "platforms": platforms,
            "results": {
                p: {
                    "success": r.success,
                    "post_id": r.post_id,
                    "url": r.url,
                    "error": r.error
                }
                for p, r in results.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def execute_social_post_with_ai(
        self,
        topic: str,
        platforms: List[str] = None,
        agent_id: str = "unknown",
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """Generar contenido con AI y publicar"""
        platforms = platforms or self.social.get_platforms()
        
        if not platforms:
            return {
                "success": False,
                "error": "No hay plataformas configuradas",
                "agent_id": agent_id
            }
        
        result = await self.social.post_with_ai(
            topic=topic,
            platforms=platforms,
            tenant_id=self.tenant_id,
            model=model
        )
        
        # Actualizar stats
        self.stats["total_executions"] += 1
        success = all(r["success"] for r in result["post_results"].values())
        
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        return {
            "success": success,
            "agent_id": agent_id,
            "content_generated": result["content_generated"],
            "ai_model": result["ai_model"],
            "ai_cost": result["ai_cost"],
            "post_results": result["post_results"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadisticas del bridge"""
        return {
            "tenant_id": self.tenant_id,
            "platforms_available": self.social.get_platforms(),
            "stats": self.stats,
            "social_manager_stats": self.social.get_stats()
        }


# Singleton por tenant
_bridges: Dict[str, RealExecutorBridge] = {}


def get_real_executor(tenant_id: str) -> RealExecutorBridge:
    """Obtener bridge para un tenant"""
    if tenant_id not in _bridges:
        _bridges[tenant_id] = RealExecutorBridge(tenant_id)
    return _bridges[tenant_id]
