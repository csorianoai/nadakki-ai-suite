"""
AI Content Generator Service
Genera contenido de marketing usando plantillas y reglas.
Preparado para integración con OpenAI/Claude API.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ContentTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    INSPIRATIONAL = "inspirational"


class ContentLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


@dataclass
class ContentTemplate:
    """Plantilla de contenido."""
    id: str
    name: str
    category: str
    template: str
    variables: List[str]
    tone: ContentTone
    platforms: List[str]
    
    def render(self, variables: Dict[str, str]) -> str:
        content = self.template
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", value)
        return content


@dataclass
class GeneratedContent:
    """Contenido generado por IA."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    original_prompt: str = ""
    generated_text: str = ""
    hashtags: List[str] = field(default_factory=list)
    tone: ContentTone = ContentTone.PROFESSIONAL
    platform: str = ""
    language: str = "es"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "original_prompt": self.original_prompt,
            "generated_text": self.generated_text,
            "hashtags": self.hashtags,
            "tone": self.tone.value,
            "platform": self.platform,
            "language": self.language,
            "created_at": self.created_at.isoformat()
        }


class AIContentService:
    """Servicio de generación de contenido con IA."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._templates: Dict[str, ContentTemplate] = {}
        self._generated: Dict[str, GeneratedContent] = {}
        self._init_default_templates()
    
    def _init_default_templates(self):
        """Inicializa plantillas por defecto."""
        templates = [
            ContentTemplate(
                id="promo_product",
                name="Promoción de Producto",
                category="sales",
                template="🚀 ¡{{product_name}} está aquí! {{benefit}} Descubre más en {{link}} #{{hashtag1}} #{{hashtag2}}",
                variables=["product_name", "benefit", "link", "hashtag1", "hashtag2"],
                tone=ContentTone.PROFESSIONAL,
                platforms=["facebook", "instagram", "linkedin"]
            ),
            ContentTemplate(
                id="financial_tip",
                name="Consejo Financiero",
                category="education",
                template="💡 Tip financiero: {{tip}} ¿Sabías que {{fact}}? Aprende más sobre {{topic}} con nosotros. #FinanzasPersonales #{{hashtag}}",
                variables=["tip", "fact", "topic", "hashtag"],
                tone=ContentTone.FRIENDLY,
                platforms=["facebook", "instagram", "twitter", "linkedin"]
            ),
            ContentTemplate(
                id="event_announcement",
                name="Anuncio de Evento",
                category="events",
                template="📅 ¡No te pierdas {{event_name}}! 📍 {{location}} 🕐 {{date_time}} {{description}} Regístrate: {{link}}",
                variables=["event_name", "location", "date_time", "description", "link"],
                tone=ContentTone.URGENT,
                platforms=["facebook", "instagram", "linkedin"]
            ),
            ContentTemplate(
                id="testimonial",
                name="Testimonio de Cliente",
                category="social_proof",
                template="⭐ \"{{quote}}\" - {{customer_name}}, {{customer_title}} Gracias por confiar en nosotros. #ClientesFelices #{{hashtag}}",
                variables=["quote", "customer_name", "customer_title", "hashtag"],
                tone=ContentTone.INSPIRATIONAL,
                platforms=["facebook", "instagram", "linkedin"]
            ),
            ContentTemplate(
                id="new_service",
                name="Nuevo Servicio Financiero",
                category="product_launch",
                template="🎉 Presentamos {{service_name}}: {{description}} ✅ {{benefit1}} ✅ {{benefit2}} ✅ {{benefit3}} Solicita info: {{link}}",
                variables=["service_name", "description", "benefit1", "benefit2", "benefit3", "link"],
                tone=ContentTone.PROFESSIONAL,
                platforms=["facebook", "instagram", "linkedin", "twitter"]
            )
        ]
        for t in templates:
            self._templates[t.id] = t
    
    def get_templates(self, category: Optional[str] = None, platform: Optional[str] = None) -> List[ContentTemplate]:
        """Lista plantillas disponibles."""
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        if platform:
            templates = [t for t in templates if platform in t.platforms]
        return templates
    
    def generate_from_template(
        self,
        tenant_id: str,
        template_id: str,
        variables: Dict[str, str],
        platform: str = "facebook"
    ) -> Optional[GeneratedContent]:
        """Genera contenido desde una plantilla."""
        template = self._templates.get(template_id)
        if not template:
            return None
        
        generated_text = template.render(variables)
        hashtags = [word.lstrip("#") for word in generated_text.split() if word.startswith("#")]
        
        content = GeneratedContent(
            tenant_id=tenant_id,
            original_prompt=f"template:{template_id}",
            generated_text=generated_text,
            hashtags=hashtags,
            tone=template.tone,
            platform=platform
        )
        
        self._generated[content.id] = content
        self.logger.info(f"Generated content {content.id} from template {template_id}")
        return content
    
    def generate_ai_content(
        self,
        tenant_id: str,
        prompt: str,
        tone: ContentTone = ContentTone.PROFESSIONAL,
        platform: str = "facebook",
        max_length: int = 280,
        include_hashtags: bool = True,
        language: str = "es"
    ) -> GeneratedContent:
        """Genera contenido usando IA (mock - preparado para OpenAI/Claude)."""
        generated_text = self._rule_based_generation(prompt, tone, max_length, language)
        
        hashtags = []
        if include_hashtags:
            hashtags = self._generate_hashtags(prompt, platform)
            generated_text += " " + " ".join(f"#{h}" for h in hashtags[:5])
        
        content = GeneratedContent(
            tenant_id=tenant_id,
            original_prompt=prompt,
            generated_text=generated_text,
            hashtags=hashtags,
            tone=tone,
            platform=platform,
            language=language
        )
        
        self._generated[content.id] = content
        self.logger.info(f"Generated AI content {content.id}")
        return content
    
    def _rule_based_generation(self, prompt: str, tone: ContentTone, max_length: int, language: str) -> str:
        """Generación basada en reglas (fallback sin API)."""
        tone_prefixes = {
            ContentTone.PROFESSIONAL: "📊",
            ContentTone.CASUAL: "👋",
            ContentTone.FRIENDLY: "😊",
            ContentTone.URGENT: "🚨",
            ContentTone.INSPIRATIONAL: "✨"
        }
        prefix = tone_prefixes.get(tone, "📢")
        base_text = f"{prefix} {prompt}"
        if len(base_text) > max_length:
            base_text = base_text[:max_length-3] + "..."
        return base_text
    
    def _generate_hashtags(self, prompt: str, platform: str) -> List[str]:
        """Genera hashtags relevantes."""
        platform_tags = {
            "instagram": ["InstaFinanzas", "FinTech"],
            "facebook": ["Finanzas", "Inversiones"],
            "linkedin": ["Finance", "Business"],
            "twitter": ["Finanzas", "Money"],
            "tiktok": ["FinTok", "MoneyTips"]
        }
        base_tags = platform_tags.get(platform, ["Marketing"])
        keywords = [w.capitalize() for w in prompt.split() if len(w) > 4][:3]
        return base_tags + keywords
    
    def get_generated_content(self, content_id: str) -> Optional[GeneratedContent]:
        return self._generated.get(content_id)
    
    def list_generated_content(self, tenant_id: str, limit: int = 20) -> List[GeneratedContent]:
        contents = [c for c in self._generated.values() if c.tenant_id == tenant_id]
        contents.sort(key=lambda x: x.created_at, reverse=True)
        return contents[:limit]
    
    def get_content_suggestions(self, tenant_id: str, industry: str = "finance") -> List[Dict[str, Any]]:
        return [
            {"type": "trending", "title": "Tema trending: Tasas de interés", "prompt": "Las tasas de interés están cambiando.", "priority": "high"},
            {"type": "seasonal", "title": "Temporada de impuestos", "prompt": "¿Listo para la declaración?", "priority": "medium"},
            {"type": "engagement", "title": "Pregunta interactiva", "prompt": "¿Cuál es tu mayor reto financiero?", "priority": "medium"},
            {"type": "educational", "title": "Tip del día", "prompt": "Automatiza tus ahorros.", "priority": "low"}
        ]


ai_content_service = AIContentService()
