from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
from datetime import datetime
import asyncio

# Importar componentes
try:
    from core.similarity.engine import CreditSimilarityEngine
    from core.tenant.manager import TenantManager
    from agents.orchestration.coordinator import AgentOrchestrator
    COMPONENTS_LOADED = True
except ImportError as e:
    print(f"Error importing components: {e}")
    COMPONENTS_LOADED = False

app = Flask(__name__)
app.config["SECRET_KEY"] = "nadakki-ai-suite-secret-key-2024"
app.config["DEBUG"] = True

CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Inicializar componentes
if COMPONENTS_LOADED:
    app.similarity_engine = CreditSimilarityEngine()
    app.tenant_manager = TenantManager()
    app.agent_orchestrator = AgentOrchestrator()
    print("✅ Todos los componentes cargados exitosamente")
    print("🤖 36 agentes especializados registrados")
else:
    print("❌ Error cargando componentes")

@app.before_request
def load_tenant():
    if request.method == "OPTIONS":
        return
    tenant_id = request.headers.get("X-Tenant-ID", "demo")
    g.tenant_id = tenant_id

@app.route("/")
def home():
    return jsonify({
        "system": "Nadakki AI Suite - CrediFace Enterprise",
        "version": "2.1.0",
        "description": "Sistema de Evaluación Crediticia con 36 Agentes Especializados",
        "status": "operational",
        "components_loaded": COMPONENTS_LOADED,
        "total_agents": 36 if COMPONENTS_LOADED else 0,
        "ecosystems": 9 if COMPONENTS_LOADED else 0,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "basic_evaluation": "/api/v1/evaluate",
            "full_evaluation": "/api/v1/evaluate/full",
            "agent_status": "/api/v1/agents/status",
            "health_check": "/api/v1/health"
        }
    })

@app.route("/api/v1/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "components_loaded": COMPONENTS_LOADED,
        "timestamp": datetime.utcnow().isoformat(),
        "agent_orchestrator": COMPONENTS_LOADED,
        "total_agents_registered": 36 if COMPONENTS_LOADED else 0
    })

@app.route("/api/v1/evaluate", methods=["POST"])
def evaluate_profile_basic():
    """Evaluación básica usando motor de similitud"""
    try:
        profile_data = request.get_json()
        tenant_id = g.get("tenant_id", "demo")
        
        if not profile_data:
            return jsonify({"error": "No profile data provided"}), 400
        
        if COMPONENTS_LOADED:
            result = app.similarity_engine.evaluate_profile(profile_data, tenant_id=tenant_id)
            result["evaluation_type"] = "basic"
        else:
            result = {"error": "Components not loaded"}
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/evaluate/full", methods=["POST"])
def evaluate_profile_full():
    """Evaluación completa usando todos los 36 agentes"""
    try:
        profile_data = request.get_json()
        tenant_id = g.get("tenant_id", "demo")
        
        if not profile_data:
            return jsonify({"error": "No profile data provided"}), 400
        
        if not COMPONENTS_LOADED:
            return jsonify({"error": "Agent orchestrator not loaded"}), 500
        
        # Ejecutar evaluación completa con todos los agentes
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            app.agent_orchestrator.coordinate_full_evaluation(profile_data, tenant_id)
        )
        loop.close()
        
        result["evaluation_type"] = "full_agent_orchestration"
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/agents/status", methods=["GET"])
def agent_status():
    """Status de todos los agentes registrados"""
    try:
        if not COMPONENTS_LOADED:
            return jsonify({"error": "Agent orchestrator not loaded"}), 500
        
        agent_registry = app.agent_orchestrator.agent_registry
        
        status = {
            "total_ecosystems": len(agent_registry),
            "total_agents": sum(len(agents) for agents in agent_registry.values()),
            "ecosystems": {}
        }
        
        for ecosystem, agents in agent_registry.items():
            status["ecosystems"][ecosystem] = {
                "agent_count": len(agents),
                "agents": agents,
                "status": "operational"
            }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"🚀 Nadakki AI Suite - CrediFace Enterprise v2.1.0")
    print(f"🤖 Components loaded: {COMPONENTS_LOADED}")
    if COMPONENTS_LOADED:
        print(f"🎯 36 Specialized Agents Registered")
        print(f"🏗️ 9 Ecosystems Active")
    print(f"🌐 Starting server on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
