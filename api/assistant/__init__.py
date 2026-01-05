"""
NADAKKI Assistant API v2.0
Chatbot conversacional con base de conocimiento expandida
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
import logging
import re

logger = logging.getLogger("AssistantAPI")
router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general"
    tenant_id: Optional[str] = "default"

# Base de conocimiento expandida
KNOWLEDGE_BASE = {
    # CAMPANAS Y MARKETING
    "campana_crear": {
        "keywords": ["crear campana", "nueva campana", "campaign builder", "como creo", "hacer campana"],
        "response": """**Como crear una campana de marketing:**

1. Ve a **Marketing > Campaign Builder**
2. Sigue el wizard de 4 pasos:

   **Paso 1 - Compose:**
   - Nombre de la campana
   - Canal (Email, SMS, Push, In-App)
   - Contenido del mensaje
   - Usa "Generar con IA" para crear contenido automatico

   **Paso 2 - Schedule:**
   - Enviar ahora (inmediato)
   - Programar para despues (fecha y hora)

   **Paso 3 - Target:**
   - Todos los usuarios (12,450)
   - Usuarios activos (8,230)
   - Leads calientes (1,850)
   - Usuarios inactivos (2,340)

   **Paso 4 - Review:**
   - Revisa todos los detalles
   - Haz clic en "Lanzar Campana"

La campana se enviara y podras ver las estadisticas en tiempo real."""
    },
    
    "campana_tipos": {
        "keywords": ["tipo campana", "canales", "email", "sms", "push", "in-app"],
        "response": """**Tipos de campanas disponibles:**

📧 **Email**
- Ideal para contenido largo
- Incluye asunto personalizable
- Mayor espacio para imagenes y links
- Tasa de apertura promedio: 35%

📱 **SMS**
- Mensajes cortos y directos
- Alta tasa de lectura (98%)
- Ideal para urgencias y promociones flash
- Limite de caracteres

🔔 **Push Notifications**
- Notificaciones en dispositivos moviles
- Requiere app instalada
- Engagement inmediato
- Ideal para recordatorios

📲 **In-App**
- Mensajes dentro de la aplicacion
- Contextuales y personalizados
- No requiere permisos externos
- Alto engagement"""
    },

    "campana_metricas": {
        "keywords": ["metrica", "estadistica", "open rate", "click rate", "rendimiento campana"],
        "response": """**Metricas de campanas:**

📊 **Metricas principales:**
- **Delivery Rate**: % de mensajes entregados (~95%)
- **Open Rate**: % de mensajes abiertos (~35%)
- **Click Rate**: % de clicks en links (~12%)
- **Bounce Rate**: % de rebotes (~5%)
- **Unsubscribe Rate**: % de bajas

📈 **Como mejorar metricas:**
- Personaliza el asunto (usa {nombre})
- Envia en horarios optimos (martes-jueves 10am)
- Segmenta tu audiencia
- Usa A/B testing
- Contenido relevante y corto

Ve a **Marketing > Analytics** para ver todas las metricas."""
    },

    # REDES SOCIALES
    "social_conectar": {
        "keywords": ["conectar red", "social", "facebook", "instagram", "twitter", "linkedin", "tiktok", "youtube", "vincular"],
        "response": """**Como conectar redes sociales:**

1. Ve a **Social > Conexiones**
2. Veras 6 plataformas disponibles:
   - 📘 Facebook
   - 📸 Instagram  
   - 🐦 Twitter/X
   - 💼 LinkedIn
   - 🎵 TikTok
   - ▶️ YouTube

3. Haz clic en "Conectar [Red]"

**⚠️ Configuracion requerida:**
Para que funcione, necesitas configurar OAuth:

1. Crea una app de desarrollador en cada plataforma
2. Obtén Client ID y Client Secret
3. Configura en el backend (variables de entorno)

**Links de documentacion:**
- Facebook: developers.facebook.com
- Twitter: developer.twitter.com
- LinkedIn: linkedin.com/developers"""
    },

    "social_programar": {
        "keywords": ["programar post", "scheduler", "publicar", "automatizar post"],
        "response": """**Programar posts en redes sociales:**

1. Ve a **Social > Programador**
2. Selecciona la red social
3. Escribe tu contenido
4. Elige fecha y hora
5. Haz clic en "Programar"

**Funcionalidades:**
- Vista de calendario
- Arrastrar y soltar posts
- Preview en tiempo real
- Publicacion en multiples redes
- Sugerencias de horarios optimos

**Nota:** Requiere tener redes sociales conectadas primero."""
    },

    # AGENTES DE IA
    "agentes_info": {
        "keywords": ["agente", "agent", "cuantos agentes", "ia disponible", "bot"],
        "response": """**Agentes de IA en NADAKKI:**

Tenemos **245 agentes** en **20 cores especializados**:

**Top 10 Cores:**
1. 📣 Marketing - 36 agentes
2. ⚖️ Legal - 33 agentes
3. 🚚 Logistica - 24 agentes
4. 🧮 Contabilidad - 23 agentes
5. 💰 Presupuesto - 14 agentes
6. 👥 RRHH - 11 agentes
7. 📋 Originacion - 11 agentes
8. 🔬 Investigacion - 10 agentes
9. 🎓 Educacion - 10 agentes
10. 🛒 VentasCRM - 10 agentes

**Como usar un agente:**
1. Selecciona el core en el sidebar
2. Busca el agente que necesitas
3. Haz clic para ver detalles
4. Ejecuta con "Run Agent" """
    },

    "agentes_marketing": {
        "keywords": ["agente marketing", "marketing agent", "content generator", "lead scoring"],
        "response": """**Agentes de Marketing (36 disponibles):**

**Lead Management:**
- LeadScorIA - Puntuador de leads
- PredictiveLeadIA - Predictor de conversion
- LeadNurturingIA - Nutricion de leads

**Content:**
- ContentGeneratorIA - Genera contenido
- CopywriterIA - Escribe copys
- HeadlineOptimizerIA - Optimiza titulos

**Social Media:**
- SocialPostGeneratorIA - Crea posts
- HashtagOptimizerIA - Sugiere hashtags
- EngagementAnalyzerIA - Analiza engagement

**Email:**
- EmailWriterIA - Redacta emails
- SubjectLineIA - Crea asuntos
- PersonalizationIA - Personaliza mensajes

**Analytics:**
- CampaignOptimizerIA - Optimiza campanas
- ABTestingIA - Analiza pruebas A/B
- ROICalculatorIA - Calcula ROI"""
    },

    # WORKFLOWS
    "workflow_info": {
        "keywords": ["workflow", "flujo", "automatizacion", "secuencia", "pipeline"],
        "response": """**Workflows Automatizados:**

Los workflows combinan multiples agentes para tareas complejas.

**10 Workflows disponibles:**

🎯 **ESTRATEGIA:**
1. Campaign Optimization
2. Customer Acquisition Intelligence
3. Competitive Intelligence Hub

📊 **EJECUCION:**
4. Content Performance Engine
5. Social Media Intelligence
6. Email Automation Master

💰 **REVENUE:**
7. Customer Lifecycle Revenue
8. Multi-Channel Attribution

🧪 **EXPERIMENTACION:**
9. A/B Testing Experimentation
10. Influencer Partnership Engine

**Como ejecutar un workflow:**
1. Ve a **Workflows** en el menu
2. Selecciona el workflow
3. Configura los parametros
4. Haz clic en "Execute" """
    },

    # DASHBOARD Y NAVEGACION
    "dashboard": {
        "keywords": ["dashboard", "inicio", "home", "principal", "resumen"],
        "response": """**Dashboard Principal:**

El dashboard muestra un resumen de toda la plataforma:

**Secciones:**
- 📊 Stats generales (agentes, cores, workflows)
- 🎯 Accesos rapidos a modulos
- 📈 Actividad reciente
- ⚡ Estado del sistema

**Navegacion:**
- **Sidebar izquierdo**: Todos los 20 cores de IA
- **Menu superior**: Home, Marketing, Social, AI Studio
- **Barra de busqueda**: Ctrl+K para buscar

**Accesos rapidos:**
- Marketing Hub: /marketing
- Social Hub: /social
- Campaign Builder: /marketing/campaign-builder
- Workflows: /workflows"""
    },

    "sidebar": {
        "keywords": ["sidebar", "menu", "navegacion", "cores", "donde encuentro"],
        "response": """**Navegacion por Sidebar:**

El sidebar izquierdo muestra los 20 cores de IA:

**Cores disponibles:**
- Marketing (36) - Agentes de marketing
- Legal (33) - Documentos y contratos
- Logistica (24) - Cadena de suministro
- Contabilidad (23) - Finanzas
- Presupuesto (14) - Planificacion
- RRHH (11) - Recursos humanos
- Originacion (11) - Creditos
- Investigacion (10) - Research
- Educacion (10) - Capacitacion
- VentasCRM (10) - Ventas
- RegTech (9) - Regulacion
- Y 9 cores mas...

**Tips:**
- Haz clic en un core para ver sus agentes
- El numero indica cantidad de agentes
- Usa Ctrl+K para buscar rapidamente"""
    },

    # CONFIGURACION Y CUENTA
    "configuracion": {
        "keywords": ["configuracion", "settings", "config", "ajustes", "cuenta"],
        "response": """**Configuracion de la plataforma:**

**Tenant Settings:**
- ID del tenant: credicefi
- Plan: Enterprise
- API Key: Configurado en backend

**Integraciones:**
- Redes sociales: Social > Conexiones
- APIs externas: AI Studio > Integraciones

**Variables de entorno necesarias:**
```
NEXT_PUBLIC_API_URL=https://nadakki-ai-suite.onrender.com
TENANT_ID=credicefi
```

**Para soporte:**
- Email: support@nadakki.com
- Documentacion: docs.nadakki.com"""
    },

    # ERRORES Y SOLUCION DE PROBLEMAS
    "error_conexion": {
        "keywords": ["error", "no funciona", "problema", "falla", "no carga"],
        "response": """**Solucion de problemas comunes:**

**Si algo no carga:**
1. Refresca la pagina (F5)
2. Verifica el estado del sistema (badge verde arriba)
3. Espera 30 segundos (el servidor puede estar iniciando)
4. Intenta de nuevo

**Si las redes sociales no conectan:**
- Verifica credenciales OAuth en backend
- Revisa los permisos de la app
- Consulta la documentacion de cada plataforma

**Si los agentes no responden:**
- El backend puede estar en cold start
- Espera hasta 30 segundos
- Haz clic en "Reintentar"

**Contactar soporte:**
Si el problema persiste, envia email a support@nadakki.com con:
- Descripcion del error
- Captura de pantalla
- URL donde ocurre"""
    },

    # PRECIOS Y PLANES
    "precios": {
        "keywords": ["precio", "costo", "plan", "suscripcion", "pago"],
        "response": """**Planes de NADAKKI AI Suite:**

**🚀 Starter**
- 50 agentes
- 5 cores
- 3 workflows
- 1 usuario
- Soporte email

**💼 Professional**
- 150 agentes
- 12 cores
- 7 workflows
- 5 usuarios
- Soporte prioritario

**🏢 Enterprise (Actual)**
- 245 agentes (todos)
- 20 cores (todos)
- 10 workflows (todos)
- Usuarios ilimitados
- Soporte 24/7
- API completa
- Multi-tenant

Contacta a sales@nadakki.com para cotizacion personalizada."""
    },

    # API Y DESARROLLO
    "api": {
        "keywords": ["api", "endpoint", "developer", "integracion", "programar"],
        "response": """**API de NADAKKI:**

**Base URL:** https://nadakki-ai-suite.onrender.com

**Endpoints principales:**
- GET /health - Estado del sistema
- GET /api/catalog/{core}/agents - Listar agentes
- POST /execute/{core}/{agent} - Ejecutar agente
- GET /workflows - Listar workflows
- POST /workflows/{id} - Ejecutar workflow
- GET /api/campaigns - Listar campanas
- POST /api/campaigns - Crear campana

**Autenticacion:**
Header: X-Tenant-ID: tu_tenant_id

**Documentacion:**
- Swagger: /docs
- ReDoc: /redoc

**SDKs disponibles:**
- Python: pip install nadakki
- JavaScript: npm install @nadakki/sdk"""
    }
}

def find_best_match(message: str) -> tuple:
    """Encuentra la mejor coincidencia en la base de conocimiento"""
    message_lower = message.lower()
    best_match = None
    best_score = 0
    
    for topic, data in KNOWLEDGE_BASE.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in message_lower:
                # Dar mas peso a coincidencias exactas
                if keyword == message_lower:
                    score += 10
                elif message_lower.startswith(keyword) or message_lower.endswith(keyword):
                    score += 5
                else:
                    score += len(keyword.split())  # Mas peso a frases largas
        
        if score > best_score:
            best_score = score
            best_match = topic
    
    return best_match, best_score

@router.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint de chat conversacional"""
    message = request.message
    
    # Buscar mejor coincidencia
    topic, score = find_best_match(message)
    
    if topic and score > 0:
        logger.info(f"Chat match: {topic} (score: {score}) for: {message[:50]}")
        return {
            "response": KNOWLEDGE_BASE[topic]["response"],
            "topic": topic,
            "confidence": min(score / 10, 1.0)
        }
    
    # Respuesta por defecto mejorada
    return {
        "response": """No encontre informacion especifica sobre eso, pero puedo ayudarte con:

**📣 Marketing**
- Como crear campanas
- Tipos de canales (email, SMS, push)
- Metricas y analytics

**📱 Redes Sociales**
- Conectar Facebook, Instagram, etc.
- Programar publicaciones
- Gestionar inbox

**🤖 Agentes de IA**
- 245 agentes disponibles
- 20 cores especializados
- Como ejecutar agentes

**⚡ Workflows**
- 10 workflows automatizados
- Como configurarlos

**🔧 Configuracion**
- Solucionar problemas
- API y desarrollo

Intenta ser mas especifico o pregunta sobre alguno de estos temas.""",
        "topic": "general",
        "confidence": 0.3
    }

@router.get("/suggestions")
async def get_suggestions():
    """Obtiene preguntas sugeridas"""
    return {
        "suggestions": [
            "Como creo una campana de marketing?",
            "Como conecto mis redes sociales?",
            "Cuantos agentes de IA hay?",
            "Que tipos de campanas puedo crear?",
            "Como funciona el workflow de Campaign Optimization?",
            "Donde veo las metricas de mis campanas?",
            "Como programo posts en redes sociales?",
            "Que agentes de marketing hay disponibles?",
            "Como soluciono errores de conexion?",
            "Cual es la API de NADAKKI?"
        ]
    }

@router.get("/topics")
async def get_topics():
    """Lista todos los temas disponibles"""
    return {
        "topics": list(KNOWLEDGE_BASE.keys()),
        "total": len(KNOWLEDGE_BASE)
    }

def get_router():
    return router
