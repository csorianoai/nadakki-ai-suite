# NADAKKI AI SUITE - HYPER AGENTS MODULE v3.0.0

## 🚀 Sistema de Agentes Inteligentes Nivel 0.1%

**Módulo completamente independiente y reutilizable para múltiples instituciones financieras.**

---

## ✅ CARACTERÍSTICAS

| Característica | Descripción |
|----------------|-------------|
| **Pensamiento Paralelo** | Múltiples streams de pensamiento simultáneos con síntesis de consenso |
| **Memoria Semántica** | Búsqueda vectorial por similitud sin dependencias externas |
| **Aprendizaje por Refuerzo** | UCB, Thompson Sampling, Epsilon-Greedy |
| **Gestión de Presupuesto** | Selección automática de modelo según budget |
| **Filtros de Seguridad** | Multi-capa contra contenido dañino, PII, compliance |
| **Multi-tenant** | Configuración por institución financiera |
| **Sin Dependencias Externas** | No requiere `agents.shared_layers` ni otros módulos |

---

## 📦 INSTALACIÓN

### Opción 1: Copiar directamente
```bash
# Copiar la carpeta hyper_agents a tu proyecto
cp -r hyper_agents C:\Users\ramon\Projects\nadakki-ai-suite\

# El módulo quedará en:
# C:\Users\ramon\Projects\nadakki-ai-suite\hyper_agents\
```

### Opción 2: Como submódulo
```bash
cd C:\Users\ramon\Projects\nadakki-ai-suite
# La carpeta hyper_agents ya está lista para usar
```

---

## 🔧 USO BÁSICO

### 1. Usar el Agente de Contenido
```python
import asyncio
from hyper_agents import HyperContentGenerator

async def main():
    # Crear agente para una institución específica
    agent = HyperContentGenerator(tenant_id="mi_banco")
    
    # Ejecutar ciclo completo
    result = await agent.run({
        "topic": "Nuevas tasas de préstamos - Enero 2026",
        "content_type": "social_post",
        "platforms": ["facebook", "linkedin"]
    })
    
    print(f"Contenido: {result.content}")
    print(f"Consenso: {result.parallel_thoughts['consensus_level']}")
    print(f"Ética: {result.ethical_assessment['score']}")
    print(f"Seguridad: {result.safety_check['score']}")

asyncio.run(main())
```

### 2. Crear tu Propio Agente
```python
from hyper_agents import (
    BaseHyperAgent, HyperAgentProfile, AutonomyLevel,
    ActionType, ActionDef
)

class MiAgentePersonalizado(BaseHyperAgent):
    def __init__(self, tenant_id: str = "default"):
        profile = HyperAgentProfile(
            agent_id="mi_agente",
            agent_name="Mi Agente Personalizado",
            description="Descripción de mi agente",
            category="Mi Categoría",
            tenant_id=tenant_id,
            autonomy_level=AutonomyLevel.SEMI
        )
        super().__init__(profile)
    
    def get_system_prompt(self) -> str:
        return "Eres un agente experto en..."
    
    async def execute_task(self, input_data, context):
        # Tu lógica aquí
        content = "Resultado generado"
        actions = [self.create_action(ActionType.LOG_EVENT, {"message": content})]
        return content, actions
```

### 3. Configurar Multi-tenant para Instituciones
```python
from hyper_agents import create_financial_tenant_config

# Configurar para un banco específico
config = create_financial_tenant_config(
    tenant_id="banco_popular",
    institution_name="Banco Popular",
    institution_type="bank",
    country="DO"
)

# Usar con el agente
agent = HyperContentGenerator(tenant_id="banco_popular")
```

---

## 📁 ESTRUCTURA DEL MÓDULO

```
hyper_agents/
├── __init__.py              # Exports principales
├── test_hyper_agents.py     # Tests completos
├── README.md                # Esta documentación
│
├── core/                    # Componentes principales
│   ├── __init__.py
│   ├── types.py             # ActionType, ActionDef, HyperAgentProfile, etc.
│   ├── adapters.py          # MockLLM, OpenAILLM, DeepSeekLLM
│   ├── hyper_cortex.py      # Pensamiento paralelo + ética
│   └── base_hyper_agent.py  # Clase base abstracta
│
├── memory/                  # Sistema de memoria
│   ├── __init__.py
│   └── quantum_memory.py    # Memoria vectorial semántica
│
├── learning/                # Aprendizaje por refuerzo
│   ├── __init__.py
│   └── rl_engine.py         # UCB, Thompson Sampling
│
├── budget/                  # Gestión de costos
│   ├── __init__.py
│   └── budget_manager.py    # Presupuesto y selección de modelo
│
├── safety/                  # Filtros de seguridad
│   ├── __init__.py
│   └── safety_filter.py     # Multi-capa de seguridad
│
└── agents/                  # Agentes específicos
    ├── __init__.py
    └── hyper_content_generator.py  # Agente de ejemplo
```

---

## 🧪 EJECUTAR TESTS

```bash
# Desde el directorio padre del módulo
cd C:\Users\ramon\Projects\nadakki-ai-suite
python hyper_agents/test_hyper_agents.py
```

**Resultado esperado:**
```
🏆 CRITERIOS NIVEL 0.1%:
✅ Pensamiento Paralelo (multi-stream)
✅ Memoria Vectorial Semántica
✅ Aprendizaje por Refuerzo (UCB/Thompson)
✅ Gestión de Costos Inteligente
✅ Filtro de Seguridad Robusto
✅ Ciclo Completo Integrado

Criterios cumplidos: 6/6
🎉 ¡NIVEL 0.1% ALCANZADO!
VEREDICTO: ELITE
```

---

## 🔄 COMPARACIÓN CON SOLUCIÓN ALTERNATIVA

### Esta solución (INDEPENDIENTE)
- ✅ Sin dependencias de `agents.shared_layers`
- ✅ Funciona en cualquier proyecto
- ✅ Reutilizable para múltiples instituciones
- ✅ Autocontenida

### Solución alternativa (crear `agents/shared_layers`)
- ⚠️ Crea dependencia entre módulos
- ⚠️ Requiere modificar estructura existente
- ⚠️ Puede causar conflictos con otros imports

---

## 📊 COMPONENTES DISPONIBLES

### Types
```python
from hyper_agents import (
    ActionType,        # PUBLISH_SOCIAL, SEND_EMAIL, CREDIT_EVALUATION, etc.
    ActionDef,         # Definición de acción con params
    AutonomyLevel,     # MANUAL, SEMI, FULL_AUTO, LEARNING
    SafetyLevel,       # SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, BLOCKED
    MemoryType,        # SHORT_TERM, LONG_TERM, EPISODIC, SEMANTIC
    HyperAgentProfile, # Perfil completo del agente
    HyperAgentOutput,  # Output del ciclo de ejecución
)
```

### LLM Adapters
```python
from hyper_agents import get_llm, MockLLM, OpenAILLM, DeepSeekLLM

# Auto-detecta según API keys disponibles
llm = get_llm()  # MockLLM si no hay keys

# O especificar explícitamente
llm = get_llm("openai", api_key="sk-...")
```

### Memory System
```python
from hyper_agents import QuantumMemory, MemoryType

memory = QuantumMemory(tenant_id="mi_banco", agent_id="mi_agente")
await memory.store("key", {"data": "valor"}, MemoryType.SHORT_TERM, importance=0.8)
results = await memory.get_context("búsqueda semántica", limit=5)
```

### RL Engine
```python
from hyper_agents import RLLearningEngine

rl = RLLearningEngine(agent_id="mi_agente", algorithm="ucb")
rl.update_policy("contexto", "accion", success=True, reward=0.9)
action, meta = rl.select_action("contexto", ["a", "b", "c"])
```

### Budget Manager
```python
from hyper_agents import BudgetManager

budget = BudgetManager(tenant_id="mi_banco", monthly_budget_usd=100)
model = budget.select_model("gpt-4", task_complexity=0.8)
status = budget.get_budget_status()
```

### Safety Filter
```python
from hyper_agents import SafetyFilter

safety = SafetyFilter(tenant_id="mi_banco", strictness=0.8)
result = safety.check_content("contenido a verificar", content_type="marketing")
if not result.is_safe:
    print(f"Issues: {result.issues}")
```

---

## 🏦 USO PARA MÚLTIPLES INSTITUCIONES FINANCIERAS

```python
# Banco 1
agent_banco1 = HyperContentGenerator(tenant_id="banco_popular")

# Banco 2
agent_banco2 = HyperContentGenerator(tenant_id="banco_reservas")

# Fintech
agent_fintech = HyperContentGenerator(tenant_id="credicefi")

# Cada uno tiene su propia:
# - Memoria (no comparten contexto)
# - Política RL (aprenden independientemente)
# - Presupuesto (límites separados)
# - Configuración de seguridad
```

---

## 📝 LICENCIA

Propietario - Nadakki AI Suite
