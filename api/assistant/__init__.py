"""
NADAKKI Assistant API
Chatbot conversacional para ayuda de la plataforma
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger("AssistantAPI")
router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general"
    tenant_id: Optional[str] = "default"

KNOWLEDGE_BASE = {
    "campana": {
        "keywords": ["campana", "campaign", "crear campana", "marketing campaign"],
        "response": """Para crear una campana de marketing:

1. Ve a Marketing > Campaign Builder
2. Sigue el wizard de 4 pasos:
   - **Compose**: Define nombre, canal (Email, SMS, Push, In-App) y contenido
   - **Schedule**: Programa cuando enviar (ahora o programado)
   - **Target**: Selecciona tu audiencia (todos, activos, leads, inactivos)
   - **Review**: Revisa los detalles y lanza la campana

Puedes usar IA para generar el contenido automaticamente con el boton 'Generar con IA'."""
    },
    "social": {
        "keywords": ["social", "red social", "conectar", "facebook", "instagram", "twitter", "linkedin", "conexion"],
        "response": """Para conectar tus redes sociales:

1. Ve a Social > Conexiones
2. Veras 6 plataformas disponibles: Facebook, Instagram, Twitter/X, LinkedIn, TikTok, YouTube
3. Haz clic en 'Conectar' en la red que desees

**Importante**: Para que la conexion funcione, necesitas:
- Configurar las credenciales OAuth en el backend
- Crear apps de desarrollador en cada plataforma
- Agregar los Client ID y Secret en las variables de entorno

Links de documentacion estan disponibles en la pagina de Conexiones."""
    },
    "agente": {
        "keywords": ["agente", "agent", "ia", "ai", "cuantos agentes"],
        "response": """NADAKKI tiene **245 agentes de IA** distribuidos en 20 cores especializados:

**Top Cores por cantidad de agentes:**
- Marketing: 36 agentes
- Legal: 33 agentes
- Logistica: 24 agentes
- Contabilidad: 23 agentes
- Presupuesto: 14 agentes
- RRHH: 11 agentes
- Originacion: 11 agentes

Cada agente esta entrenado para tareas especificas. Puedes explorar todos los cores desde el sidebar izquierdo."""
    },
    "workflow": {
        "keywords": ["workflow", "flujo", "automatizacion", "secuencia"],
        "response": """Los **workflows** son secuencias automatizadas de agentes que trabajan juntos:

**10 Workflows disponibles:**
1. Campaign Optimization - Optimiza campanas de marketing
2. Customer Acquisition Intelligence - Adquisicion de clientes
3. Customer Lifecycle Revenue - Ciclo de vida del cliente
4. Content Performance Engine - Rendimiento de contenido
5. Social Media Intelligence - Inteligencia de redes sociales
6. Email Automation Master - Automatizacion de emails
7. Multi-Channel Attribution - Atribucion multicanal
8. Competitive Intelligence Hub - Inteligencia competitiva
9. A/B Testing Experimentation - Experimentos A/B
10. Influencer Partnership Engine - Partnerships con influencers

Accede desde el menu Workflows en el sidebar."""
    },
    "stats": {
        "keywords": ["cuanto", "total", "estadistica", "numeros", "cantidad"],
        "response": """**NADAKKI AI Suite en numeros:**

- 245 agentes de IA activos
- 20 cores especializados
- 10 workflows automatizados
- 6 integraciones sociales
- Soporte multi-tenant
- API REST completa
- Dashboard en tiempo real

Todo conectado a APIs reales y listo para produccion."""
    }
}

@router.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint de chat conversacional"""
    message = request.message.lower()
    
    # Buscar en la base de conocimiento
    for topic, data in KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in message:
                logger.info(f"Chat match: {topic} for message: {request.message[:50]}")
                return {
                    "response": data["response"],
                    "topic": topic,
                    "confidence": 0.9
                }
    
    # Respuesta por defecto
    return {
        "response": """Gracias por tu pregunta. Puedo ayudarte con:

- **Campanas de marketing**: Como crear y gestionar campanas
- **Redes sociales**: Como conectar Facebook, Instagram, etc.
- **Agentes de IA**: Informacion sobre los 245 agentes disponibles
- **Workflows**: Secuencias automatizadas de agentes
- **Navegacion**: Como usar la plataforma

Por favor, pregunta algo mas especifico o usa los accesos rapidos disponibles.""",
        "topic": "general",
        "confidence": 0.5
    }

@router.get("/suggestions")
async def get_suggestions():
    """Obtiene preguntas sugeridas"""
    return {
        "suggestions": [
            "Como creo una campana de marketing?",
            "Como conecto mis redes sociales?",
            "Que agentes de IA hay disponibles?",
            "Como funciona el sistema de workflows?",
            "Cuantos agentes tiene la plataforma?"
        ]
    }

def get_router():
    return router
