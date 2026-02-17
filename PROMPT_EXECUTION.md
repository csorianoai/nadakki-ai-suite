CONTEXTO:
Repo: nadakki-ai-suite | Branch: feature/agent-execution desde main
Stack: FastAPI + Python 3.9+ | Entry: main.py
Catalogo: GET /api/catalog -> 253 agentes con: id, file_path, class_name, status
file_path es RUTA A ARCHIVO (ej: marketing/_archived/content_generator_v3.py), NO modulo Python.

REGLAS:
1. git checkout -b feature/agent-execution ANTES de tocar algo
2. main.py: SOLO agregar lineas. NUNCA refactorear/borrar.
3. NO loguear tokens/keys. DRY_RUN por defecto.
4. python main.py y curl -s http://127.0.0.1:8000/health DESPUES de cada cambio

PASO 1: DESCUBRIMIENTO (NO CREAR NADA AUN - REPORTAR HALLAZGOS)
A) Abrir main.py, localizar get_all_agents y entender de donde salen los agentes
B) curl -s http://127.0.0.1:8000/api/catalog?module=marketing&limit=20 y clasificar cuales tienen _archived o status=template (NO ejecutables) vs cuales son reales
C) Para 3 archivos NO archived: verificar si tienen metodo execute(), run(), o __call__
D) SI no hay agentes ejecutables reales: crear agents/marketing/demo_agent.py con clase DemoMarketingAgent que tenga execute(self, payload)
E) Escribir reports/agent_execution_discovery.md con hallazgos
F) DETENTE y reporta hallazgos antes de continuar.

PASO 2: CREAR services/agent_runner.py con safe_load usando importlib.util.spec_from_file_location (NO importlib.import_module porque file_path es ruta de archivo). Validar path seguro.

PASO 3: CREAR routers/agent_execution_router.py - POST /api/v1/agents/{agent_id}/execute con body {payload, dry_run, auto_publish, auto_email}. Usar agent_runner. Archived/template -> 409. No encontrado -> 404.

PASO 4: Registrar router en main.py (solo 2 lineas de import + include_router)

PASO 5: Tests en tests/marketing/test_agent_execution.py (404 invalido, 409 archived, 200 demo)

PASO 6: Verificacion manual con curl

PASO 7: git commit y push a feature/agent-execution
