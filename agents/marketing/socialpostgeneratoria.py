# agents/marketing/socialpostgeneratoria.py
"""SocialPostGeneratorIA v3.0.0 - SUPER AGENT - Generador de Posts Sociales"""

from __future__ import annotations
import time, logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False

class SocialPostGeneratorIA:
    VERSION = "3.0.0"
    AGENT_ID = "socialpostgeneratoria"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            topic = data.get("topic", "financial tips")
            platform = data.get("platform", "linkedin")
            tone = data.get("tone", "professional")
            
            posts = self._generate_posts(topic, platform, tone)
            hashtags = self._suggest_hashtags(topic, platform)
            timing = self._optimal_timing(platform)
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {"generation_id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "tenant_id": self.tenant_id, "topic": topic, "platform": platform, "posts": posts, "hashtags": hashtags, "optimal_timing": timing, "posts_generated": len(posts), "key_insights": [f"Posts generados: {len(posts)}", f"Plataforma: {platform}", f"Mejor horario: {timing['best_time']}"], "decision_trace": [f"topic={topic}", f"platform={platform}"], "version": self.VERSION, "latency_ms": latency_ms}
            
            if DECISION_LAYER_AVAILABLE:
                try: result = apply_decision_layer(result)
                except: pass
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            return {"generation_id": "error", "posts": [], "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _generate_posts(self, topic: str, platform: str, tone: str) -> List[Dict]:
        templates = {
            "linkedin": [
                {"type": "insight", "text": f"3 insights clave sobre {topic} que todo profesional debe conocer...", "cta": "Lee más en el link", "expected_engagement": 0.045},
                {"type": "question", "text": f"¿Cuál es tu mayor desafío con {topic}? Comparte tu experiencia en los comentarios.", "cta": None, "expected_engagement": 0.062},
                {"type": "tip", "text": f"Tip del día: Optimiza tu {topic} con esta estrategia simple pero efectiva.", "cta": "Guarda este post", "expected_engagement": 0.038}
            ],
            "twitter": [
                {"type": "thread", "text": f"🧵 Hilo: Todo lo que necesitas saber sobre {topic}...", "cta": "RT para guardar", "expected_engagement": 0.025},
                {"type": "quick_tip", "text": f"💡 {topic.capitalize()}: El 80% de los resultados viene del 20% de las acciones.", "cta": None, "expected_engagement": 0.032}
            ]
        }
        return templates.get(platform, templates["linkedin"])
    
    def _suggest_hashtags(self, topic: str, platform: str) -> List[str]:
        base = ["#fintech", "#finance", "#tips", "#business"]
        topic_tags = [f"#{topic.replace(' ', '')}", f"#{topic.split()[0]}tips"]
        return base[:3] + topic_tags
    
    def _optimal_timing(self, platform: str) -> Dict[str, Any]:
        timing = {"linkedin": {"best_time": "10:00 AM", "best_days": ["Tuesday", "Wednesday"], "avoid": "weekends"}, "twitter": {"best_time": "12:00 PM", "best_days": ["Monday", "Thursday"], "avoid": "late_night"}, "instagram": {"best_time": "6:00 PM", "best_days": ["Wednesday", "Friday"], "avoid": "early_morning"}}
        return timing.get(platform, timing["linkedin"])
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()

def create_agent_instance(tenant_id: str, config: Dict = None):
    return SocialPostGeneratorIA(tenant_id, config)
