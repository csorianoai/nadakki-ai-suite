"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, X, Send, Loader2, Sparkles, MessageCircle,
  Minimize2, Maximize2, HelpCircle, Zap, BookOpen,
  ChevronRight, Lightbulb
} from "lucide-react";
import { useTenant } from "@/contexts/TenantContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

const QUICK_QUESTIONS = [
  "¿Cómo funciona el workflow de Campaign Optimization?",
  "¿Qué agentes tiene Customer Acquisition?",
  "¿Cómo puedo optimizar mis campañas?",
  "Explícame el sistema de workflows",
  "¿Qué puedo hacer después de ejecutar un workflow?",
  "¿Cuál es la diferencia entre CORE y INTELLIGENCE?"
];

const SYSTEM_CONTEXT = `Eres NADAKKI AI Copilot, el asistente inteligente del sistema NADAKKI AI Suite.

SOBRE NADAKKI AI SUITE:
- Plataforma enterprise de marketing automation con IA
- 225 agentes de IA especializados
- 20 cores funcionales (marketing, legal, finanzas, etc.)
- 10 workflows de marketing automatizados
- Multi-tenant: cada cliente tiene su propio entorno aislado

WORKFLOWS DISPONIBLES (10 total, 43 agentes):

1. CAMPAIGN OPTIMIZATION (CORE - 5 agentes):
   - AudienceAnalyzerAI: Segmenta audiencias con ML
   - BudgetOptimizerAI: Optimiza distribución de presupuesto
   - ContentGeneratorAI: Genera copies y creativos
   - ROIPredictorAI: Predice retorno de inversión
   - RecommendationEngineAI: Sintetiza recomendaciones
   Uso: Optimizar campañas de marketing para maximizar ROI

2. CUSTOMER ACQUISITION INTELLIGENCE (CORE - 7 agentes):
   - LeadScorerAI: Scoring predictivo de leads
   - BehaviorAnalyzerAI: Análisis de comportamiento
   - ChannelOptimizerAI: Selección óptima de canal
   - MessagePersonalizerAI: Mensajes hiperpersonalizados
   - FunnelAnalyzerAI: Análisis de embudo
   - OfferOptimizerAI: Optimización de ofertas
   - ConversionPredictorAI: Predicción de conversión
   Uso: Adquirir clientes de alto valor eficientemente

3. CUSTOMER LIFECYCLE REVENUE (CORE - 6 agentes):
   - LifecycleMapperAI: Mapea etapa del cliente
   - ChurnPredictorAI: Predice riesgo de abandono
   - ExpansionIdentifierAI: Identifica oportunidades upsell
   - EngagementOptimizerAI: Optimiza interacciones
   - ValueCalculatorAI: Calcula CLV
   - ActionRecommenderAI: Recomienda acciones
   Uso: Maximizar valor del cliente en su ciclo de vida

4. CONTENT PERFORMANCE ENGINE (EXECUTION - 5 agentes):
   - ContentAnalyzerAI: Analiza rendimiento de contenido
   - SEOOptimizerAI: Optimización para buscadores
   - EngagementPredictorAI: Predice engagement
   - GapIdentifierAI: Identifica gaps de contenido
   - CalendarOptimizerAI: Optimiza calendario editorial
   Uso: Optimizar estrategia de contenido

5. SOCIAL MEDIA INTELLIGENCE (EXECUTION - 4 agentes):
   - SocialListenerAI: Escucha social en tiempo real
   - SentimentAnalyzerAI: Análisis de sentimiento
   - TrendDetectorAI: Detecta tendencias
   - EngagementStrategistAI: Estrategia de engagement
   Uso: Inteligencia de redes sociales

6. EMAIL AUTOMATION MASTER (EXECUTION - 4 agentes):
   - ListSegmenterAI: Segmentación de listas
   - SubjectOptimizerAI: Optimiza subject lines
   - ContentPersonalizerAI: Personaliza emails
   - SendOptimizerAI: Optimiza timing de envío
   Uso: Automatización avanzada de email marketing

7. MULTI-CHANNEL ATTRIBUTION (INTELLIGENCE - 4 agentes):
   - JourneyMapperAI: Mapea customer journeys
   - AttributionModelerAI: Modelos de atribución
   - IncrementalityAnalyzerAI: Análisis de incrementalidad
   - BudgetAllocatorAI: Asignación óptima de presupuesto
   Uso: Entender contribución de cada canal

8. COMPETITIVE INTELLIGENCE HUB (INTELLIGENCE - 3 agentes):
   - CompetitorTrackerAI: Monitorea competidores
   - StrategyAnalyzerAI: Analiza estrategias
   - OpportunityFinderAI: Encuentra oportunidades
   Uso: Inteligencia competitiva automatizada

9. A/B TESTING & EXPERIMENTATION (INTELLIGENCE - 3 agentes):
   - ExperimentDesignerAI: Diseña experimentos
   - ResultsAnalyzerAI: Análisis estadístico
   - InsightGeneratorAI: Genera insights
   Uso: Experimentación científica para optimización

10. INFLUENCER & PARTNERSHIP ENGINE (INTELLIGENCE - 2 agentes):
    - InfluencerFinderAI: Encuentra influencers
    - PartnershipOptimizerAI: Optimiza partnerships
    Uso: Gestión inteligente de influencers

TIERS DE WORKFLOWS:
- CORE: Workflows fundamentales, alta prioridad
- EXECUTION: Workflows de ejecución táctica
- INTELLIGENCE: Workflows de análisis e insights

CÓMO FUNCIONAN LOS WORKFLOWS:
1. El usuario configura parámetros (nombre, objetivo, presupuesto, etc.)
2. Hace clic en "Ejecutar Workflow"
3. Los agentes se ejecutan en secuencia automáticamente
4. Cada agente procesa datos y pasa resultados al siguiente
5. El usuario recibe resultados consolidados con recomendaciones
6. Puede tomar acciones basadas en las recomendaciones

MÓDULOS PRINCIPALES:
- Marketing Hub: Campañas, contenido, audiencias
- Analytics: Métricas, reportes, ROI
- Workflows: Automatizaciones con IA
- Admin: Configuración, usuarios, logs

INSTRUCCIONES PARA TI:
- Responde en español
- Sé conciso pero completo
- Usa ejemplos prácticos
- Sugiere próximos pasos
- Si no sabes algo, admítelo
- Ofrece guiar paso a paso cuando sea apropiado`;

export default function OnboardingAgent() {
  const { tenantId, settings } = useTenant();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `¡Hola! 👋 Soy el **NADAKKI AI Copilot**, tu asistente inteligente.

Puedo ayudarte con:
- Explicar cómo funcionan los workflows
- Describir qué hace cada agente de IA
- Guiarte paso a paso en cualquier proceso
- Responder dudas sobre el sistema

¿En qué puedo ayudarte hoy?`,
      timestamp: new Date(),
      suggestions: QUICK_QUESTIONS.slice(0, 3)
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Preparar historial para el API
      const history = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch("/api/ai/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          history,
          context: {
            tenant_id: tenantId,
            tenant_name: settings.name,
            current_page: window.location.pathname
          }
        })
      });

      if (!response.ok) {
        throw new Error("Error en la respuesta");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: "assistant",
        content: data.response || "Lo siento, no pude procesar tu pregunta. ¿Podrías reformularla?",
        timestamp: new Date(),
        suggestions: data.suggestions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      
      // Fallback: respuesta local basada en keywords
      const fallbackResponse = generateFallbackResponse(content);
      
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: "assistant",
        content: fallbackResponse,
        timestamp: new Date(),
        suggestions: QUICK_QUESTIONS.slice(0, 2)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateFallbackResponse = (query: string): string => {
    const q = query.toLowerCase();
    
    if (q.includes("campaign optimization") || q.includes("optimización de campaña")) {
      return `**Campaign Optimization** es un workflow CORE con 5 agentes:

1. **AudienceAnalyzerAI** - Segmenta tu audiencia objetivo
2. **BudgetOptimizerAI** - Distribuye presupuesto óptimamente
3. **ContentGeneratorAI** - Genera copies y creativos
4. **ROIPredictorAI** - Predice el retorno de inversión
5. **RecommendationEngineAI** - Sintetiza recomendaciones

**Cómo usarlo:**
1. Ve a Workflows → Campaign Optimization
2. Configura nombre, objetivo, canal y presupuesto
3. Haz clic en "Ejecutar Workflow"
4. Revisa los resultados y toma acción

¿Te gustaría que te explique algún agente en detalle?`;
    }
    
    if (q.includes("workflow") || q.includes("flujo")) {
      return `NADAKKI tiene **10 workflows de marketing** organizados en 3 tiers:

**CORE (3 workflows):**
- Campaign Optimization (5 agentes)
- Customer Acquisition Intelligence (7 agentes)
- Customer Lifecycle Revenue (6 agentes)

**EXECUTION (3 workflows):**
- Content Performance Engine (5 agentes)
- Social Media Intelligence (4 agentes)
- Email Automation Master (4 agentes)

**INTELLIGENCE (4 workflows):**
- Multi-Channel Attribution (4 agentes)
- Competitive Intelligence Hub (3 agentes)
- A/B Testing & Experimentation (3 agentes)
- Influencer Partnership Engine (2 agentes)

**Total: 43 agentes de IA trabajando para ti.**

¿Sobre cuál workflow te gustaría saber más?`;
    }

    if (q.includes("agente") || q.includes("agent")) {
      return `Los **agentes de IA** son componentes especializados que realizan tareas específicas.

Cada workflow tiene múltiples agentes que trabajan en secuencia:
- Cada agente recibe inputs del anterior
- Procesa datos con modelos de ML/IA
- Genera outputs para el siguiente agente
- El último agente consolida todo en recomendaciones

**Ejemplo en Campaign Optimization:**
\`\`\`
Usuario → AudienceAnalyzerAI → BudgetOptimizerAI → 
ContentGeneratorAI → ROIPredictorAI → RecommendationEngineAI → Resultado
\`\`\`

¿Te gustaría conocer los agentes de un workflow específico?`;
    }

    if (q.includes("tier") || q.includes("core") || q.includes("intelligence")) {
      return `Los workflows están organizados en **3 tiers**:

🧠 **CORE** - Workflows fundamentales
- Mayor prioridad de ejecución
- Casos de uso principales
- Más agentes involucrados

⚡ **EXECUTION** - Workflows tácticos
- Ejecución de campañas
- Operaciones del día a día
- Automatizaciones específicas

💡 **INTELLIGENCE** - Workflows analíticos
- Análisis profundo
- Insights estratégicos
- Experimentación

El tier determina la complejidad y el enfoque del workflow.`;
    }

    return `¡Buena pregunta! Puedo ayudarte con información sobre:

- **Workflows**: Cómo funcionan, qué agentes tienen
- **Agentes de IA**: Qué hace cada uno
- **Procesos**: Guías paso a paso
- **Módulos**: Marketing, Analytics, Admin

¿Podrías ser más específico sobre qué te gustaría saber?`;
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-gradient-to-r from-purple-600 to-cyan-600 text-white shadow-2xl hover:shadow-purple-500/25 hover:scale-110 transition-all group"
          >
            <Bot className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            <div className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              AI Copilot
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className={`fixed z-50 bg-gray-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden ${
              isMinimized 
                ? "bottom-6 right-6 w-80 h-14" 
                : "bottom-6 right-6 w-96 h-[600px] max-h-[80vh]"
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-gradient-to-r from-purple-600/20 to-cyan-600/20">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/20">
                  <Bot className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm">NADAKKI AI Copilot</h3>
                  {!isMinimized && (
                    <p className="text-xs text-gray-400">Tu asistente inteligente</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                </button>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Content */}
            {!isMinimized && (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[440px]">
                  {messages.map((message) => (
                    <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[85%] ${message.role === "user" ? "order-1" : "order-2"}`}>
                        <div className={`p-3 rounded-2xl text-sm ${
                          message.role === "user" 
                            ? "bg-purple-600 text-white rounded-br-md" 
                            : "bg-white/5 text-gray-200 rounded-bl-md"
                        }`}>
                          <div className="whitespace-pre-wrap" dangerouslySetInnerHTML={{ 
                            __html: message.content
                              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                              .replace(/`([^`]+)`/g, '<code class="bg-black/30 px-1 rounded">$1</code>')
                              .replace(/\n/g, '<br/>')
                          }} />
                        </div>
                        
                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {message.suggestions.map((suggestion, i) => (
                              <button
                                key={i}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="flex items-center gap-2 w-full p-2 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-gray-300 hover:text-white transition-colors text-left"
                              >
                                <Lightbulb className="w-3 h-3 text-yellow-400 flex-shrink-0" />
                                <span className="truncate">{suggestion}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="flex items-center gap-2 text-gray-400">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Pensando...</span>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-white/10">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Pregúntame lo que quieras..."
                      className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-purple-500"
                    />
                    <button
                      onClick={() => sendMessage(input)}
                      disabled={!input.trim() || isLoading}
                      className="p-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <Send className="w-4 h-4 text-white" />
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}