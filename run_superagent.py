"""
🚀 SERVIDOR SUPER-AGENT v5.0 ENTERPRISE
Script para ejecutar el servidor FastAPI
"""

import uvicorn
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 INICIANDO SUPER-AGENT v5.0 ENTERPRISE SERVER")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🩺 Health: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "agents.marketing.contentperformance_superagent_v5:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )