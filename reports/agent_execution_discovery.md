# Agent Execution Discovery Report

**Fecha:** 2026-02-17
**Branch:** feature/agent-execution
**Objetivo:** Determinar si los agentes del catalogo son ejecutables antes de crear el endpoint POST /execute

---

## 1A. Como funciona get_all_agents (main.py)

- `intelligent_discovery()` (linea 633) escanea `agents/**/*.py` recursivamente
- Parsea cada archivo con AST y puntua clases con `score_agent_class_v2_enhanced()`
- Guarda resultados en `ALL_AGENTS` (dict global, key = `{filename}__{classname}`)
- `file_path` es RUTA RELATIVA a `agents/` (ej: `marketing/abtestingia.py`), NO modulo Python
- El endpoint `GET /api/catalog` devuelve `ALL_AGENTS` con filtros

## 1B. Clasificacion de agentes marketing

| Categoria | Cantidad |
|-----------|----------|
| TOTAL marketing | 253 |
| Archived (`_archived/` en path) | 10 |
| Template (status=template, no archived) | 177 |
| **Reales (ni archived ni template)** | **66** |

### Agentes archived (10)
Todos en `marketing/_archived/content_generator_v3.py` y `marketing/_archived/leadscoringia_backup_*.py`

### Agentes template (177)
Clases auxiliares sin logica ejecutable real (CircuitBreaker, ComplianceStatus, configs, etc.)

### Agentes reales (66)
Agentes con status `production` o `development`, score >= 3.0, y generalmente con metodo `execute()`.

## 1C. Verificacion de metodos ejecutables (3 agentes reales)

### 1. ABTestingAgentOperative (`marketing/abtestingia.py`)
- **execute():** SI - Logica completa (circuit breaker, input normalization, tenant, hashing, trace)
- Patron: funcion `execute(input_data, context)` a nivel modulo + clase wrapper `ABTestingAgentOperative.execute(self, input_data, tenant_id)`

### 2. AudienceSegmenterAgentOperative (`marketing/audiencesegmenteria.py`)
- **execute():** SI - Mismo patron: funcion modulo + clase wrapper
- Logica: circuit breaker, normalizacion, tenant config, trace

### 3. CampaignOptimizerAgentOperative (`marketing/campaignoptimizeria.py`)
- **execute():** SI - Mismo patron consistente
- Logica: circuit breaker, normalizacion, tenant config, trace

## 1D. Necesidad de DemoAgent

**NO se necesita.** Hay 66 agentes reales con `execute()` implementado. El patron es consistente:
- Signature: `execute(input_data: Dict, context: Optional[Dict]) -> Dict`
- La clase tiene: `execute(self, input_data, tenant_id="default", **kwargs)`
- Todas usan `OperativeMixin.bind()`

---

## Patron de ejecucion detectado

```python
# Nivel modulo (logica real):
def execute(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ...

# Nivel clase (wrapper):
class XxxAgentOperative:
    def execute(self, input_data, tenant_id="default", **kwargs):
        context = {"tenant_id": tenant_id, **kwargs}
        return execute(input_data, context)
```

## Implicaciones para agent_runner.py

1. Usar `importlib.util.spec_from_file_location` para cargar el archivo
2. Buscar la clase con `class_name` del catalogo
3. Instanciarla y llamar `.execute(payload)`
4. El `file_path` del catalogo es relativo a `agents/` -> resolver como `agents/{file_path}`
5. Agentes archived (`_archived/` en path) o template (status=template) -> rechazar con 409
