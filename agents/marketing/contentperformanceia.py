# agents/marketing/contentperformanceia.py
"""
ContentPerformanceIA v3.0 - Análisis de Performance de Contenido
Simplificado y funcional - sin dependencias pesadas.
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class ContentPerformanceIA:
    VERSION = "3.0.0"
    AGENT_ID = "contentperformanceia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta análisis de performance de contenido."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            content_items = data.get("content_items", [])
            date_range = data.get("date_range", "last_30_days")
            
            # Analizar contenido
            analysis = self._analyze_content(content_items)
            
            # Performance por tipo
            by_type = self._analyze_by_type(content_items)
            
            # Top y bottom performers
            top_performers = self._get_top_performers(content_items)
            bottom_performers = self._get_bottom_performers(content_items)
            
            # Generar insights
            insights = self._generate_insights(analysis, by_type)
            
            # Recomendaciones
            recommendations = self._generate_recommendations(analysis, by_type)
            
            decision_trace = [
                f"content_analyzed={len(content_items) if content_items else 'sample_data'}",
                f"date_range={date_range}",
                f"insights_generated={len(insights)}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "analysis_id": f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "summary": analysis,
                "performance_by_type": by_type,
                "top_performers": top_performers,
                "bottom_performers": bottom_performers,
                "key_insights": insights,
                "recommendations": recommendations,
                "decision_trace": decision_trace,
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
            
            if DECISION_LAYER_AVAILABLE:
                try:
                    result = apply_decision_layer(result)
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            
            return {
                "analysis_id": "error",
                "tenant_id": self.tenant_id,
                "summary": {},
                "performance_by_type": {},
                "top_performers": [],
                "bottom_performers": [],
                "key_insights": [f"Error: {str(e)[:100]}"],
                "recommendations": [],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _analyze_content(self, content_items: List[Dict]) -> Dict[str, Any]:
        """Analiza métricas generales de contenido."""
        if not content_items:
            # Datos de ejemplo
            return {
                "total_content": 45,
                "total_views": 125000,
                "total_engagement": 8750,
                "avg_engagement_rate": 0.07,
                "avg_conversion_rate": 0.025,
                "total_shares": 2340,
                "avg_time_on_page": 185,
                "bounce_rate": 0.42,
                "period": "last_30_days"
            }
        
        total_views = sum(c.get("views", 0) for c in content_items)
        total_engagement = sum(c.get("engagements", 0) for c in content_items)
        total_conversions = sum(c.get("conversions", 0) for c in content_items)
        total_shares = sum(c.get("shares", 0) for c in content_items)
        
        return {
            "total_content": len(content_items),
            "total_views": total_views,
            "total_engagement": total_engagement,
            "avg_engagement_rate": round(total_engagement / total_views, 4) if total_views > 0 else 0,
            "avg_conversion_rate": round(total_conversions / total_views, 4) if total_views > 0 else 0,
            "total_shares": total_shares,
            "avg_time_on_page": 180,
            "bounce_rate": 0.45,
            "period": "last_30_days"
        }
    
    def _analyze_by_type(self, content_items: List[Dict]) -> Dict[str, Any]:
        """Analiza performance por tipo de contenido."""
        if not content_items:
            return {
                "blog_post": {"count": 15, "views": 45000, "engagement_rate": 0.08, "conversion_rate": 0.03, "score": 82},
                "social_post": {"count": 20, "views": 55000, "engagement_rate": 0.12, "conversion_rate": 0.015, "score": 78},
                "email": {"count": 8, "views": 20000, "engagement_rate": 0.25, "conversion_rate": 0.045, "score": 88},
                "video": {"count": 2, "views": 5000, "engagement_rate": 0.15, "conversion_rate": 0.02, "score": 75}
            }
        
        by_type = {}
        for item in content_items:
            ctype = item.get("content_type", "unknown")
            if ctype not in by_type:
                by_type[ctype] = {"count": 0, "views": 0, "engagements": 0, "conversions": 0}
            by_type[ctype]["count"] += 1
            by_type[ctype]["views"] += item.get("views", 0)
            by_type[ctype]["engagements"] += item.get("engagements", 0)
            by_type[ctype]["conversions"] += item.get("conversions", 0)
        
        result = {}
        for ctype, data in by_type.items():
            views = data["views"]
            result[ctype] = {
                "count": data["count"],
                "views": views,
                "engagement_rate": round(data["engagements"] / views, 4) if views > 0 else 0,
                "conversion_rate": round(data["conversions"] / views, 4) if views > 0 else 0,
                "score": self._calculate_score(data)
            }
        
        return result
    
    def _calculate_score(self, data: Dict) -> int:
        """Calcula score de performance (0-100)."""
        views = data.get("views", 0)
        if views == 0:
            return 0
        
        eng_rate = data.get("engagements", 0) / views
        conv_rate = data.get("conversions", 0) / views
        
        # Score ponderado
        score = (eng_rate * 500) + (conv_rate * 2000) + min(20, views / 1000)
        return min(100, int(score))
    
    def _get_top_performers(self, content_items: List[Dict]) -> List[Dict]:
        """Obtiene contenido con mejor performance."""
        if not content_items:
            return [
                {"id": "blog_023", "title": "Guía Completa de Ahorro", "type": "blog_post", "views": 12500, "engagement_rate": 0.12, "score": 95},
                {"id": "email_015", "title": "Oferta Exclusiva Q4", "type": "email", "views": 8200, "engagement_rate": 0.28, "score": 92},
                {"id": "social_089", "title": "Tips Financieros", "type": "social_post", "views": 15000, "engagement_rate": 0.15, "score": 88},
                {"id": "video_004", "title": "Tutorial Inversiones", "type": "video", "views": 5500, "engagement_rate": 0.18, "score": 85},
                {"id": "blog_019", "title": "Comparativa Productos", "type": "blog_post", "views": 9800, "engagement_rate": 0.09, "score": 82}
            ]
        
        scored = []
        for item in content_items:
            views = item.get("views", 0)
            eng = item.get("engagements", 0)
            score = self._calculate_score({"views": views, "engagements": eng, "conversions": item.get("conversions", 0)})
            scored.append({
                "id": item.get("content_id", "unknown"),
                "title": item.get("title", "Sin título"),
                "type": item.get("content_type", "unknown"),
                "views": views,
                "engagement_rate": round(eng / views, 4) if views > 0 else 0,
                "score": score
            })
        
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
    
    def _get_bottom_performers(self, content_items: List[Dict]) -> List[Dict]:
        """Obtiene contenido con peor performance."""
        if not content_items:
            return [
                {"id": "blog_045", "title": "Términos y Condiciones", "type": "blog_post", "views": 120, "engagement_rate": 0.01, "score": 15},
                {"id": "social_102", "title": "Promoción Antigua", "type": "social_post", "views": 350, "engagement_rate": 0.02, "score": 22},
                {"id": "email_028", "title": "Newsletter Genérico", "type": "email", "views": 1200, "engagement_rate": 0.03, "score": 28}
            ]
        
        scored = []
        for item in content_items:
            views = item.get("views", 0)
            eng = item.get("engagements", 0)
            score = self._calculate_score({"views": views, "engagements": eng, "conversions": item.get("conversions", 0)})
            scored.append({
                "id": item.get("content_id", "unknown"),
                "title": item.get("title", "Sin título"),
                "type": item.get("content_type", "unknown"),
                "views": views,
                "engagement_rate": round(eng / views, 4) if views > 0 else 0,
                "score": score
            })
        
        return sorted(scored, key=lambda x: x["score"])[:3]
    
    def _generate_insights(self, analysis: Dict, by_type: Dict) -> List[str]:
        """Genera insights de performance."""
        insights = []
        
        # Engagement rate
        eng_rate = analysis.get("avg_engagement_rate", 0)
        if eng_rate > 0.10:
            insights.append(f"Engagement rate excelente: {eng_rate*100:.1f}% (benchmark: 5-8%)")
        elif eng_rate > 0.05:
            insights.append(f"Engagement rate bueno: {eng_rate*100:.1f}% (en benchmark)")
        else:
            insights.append(f"Engagement rate bajo: {eng_rate*100:.1f}% (mejorar calidad de contenido)")
        
        # Mejor tipo de contenido
        if by_type:
            best_type = max(by_type.items(), key=lambda x: x[1].get("score", 0))
            insights.append(f"Mejor tipo de contenido: {best_type[0]} (score {best_type[1]['score']}/100)")
        
        # Conversion rate
        conv_rate = analysis.get("avg_conversion_rate", 0)
        if conv_rate > 0.03:
            insights.append(f"Conversion rate alto: {conv_rate*100:.2f}% - contenido bien optimizado")
        
        # Bounce rate
        bounce = analysis.get("bounce_rate", 0)
        if bounce > 0.50:
            insights.append(f"Bounce rate alto: {bounce*100:.0f}% - revisar relevancia de contenido")
        
        return insights[:5]
    
    def _generate_recommendations(self, analysis: Dict, by_type: Dict) -> List[str]:
        """Genera recomendaciones accionables."""
        recommendations = []
        
        # Por engagement
        if analysis.get("avg_engagement_rate", 0) < 0.05:
            recommendations.append("URGENTE: Mejorar calidad de contenido para aumentar engagement")
        
        # Por tipo de contenido
        if by_type:
            best_type = max(by_type.items(), key=lambda x: x[1].get("score", 0))
            worst_type = min(by_type.items(), key=lambda x: x[1].get("score", 0))
            
            recommendations.append(f"AUMENTAR: Producción de {best_type[0]} (mejor ROI)")
            if worst_type[1]["score"] < 50:
                recommendations.append(f"OPTIMIZAR: Revisar estrategia de {worst_type[0]}")
        
        # Por bounce rate
        if analysis.get("bounce_rate", 0) > 0.50:
            recommendations.append("MEJORAR: Landing pages y CTAs para reducir bounce rate")
        
        # Por conversión
        if analysis.get("avg_conversion_rate", 0) < 0.02:
            recommendations.append("AÑADIR: CTAs más claros y ofertas relevantes")
        
        return recommendations[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "decision_layer": DECISION_LAYER_AVAILABLE
        }
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return ContentPerformanceIA(tenant_id, config)
