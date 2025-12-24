# test_marketing_agents.py
import requests
import json
import time

class MarketingAgentsTester:
    def __init__(self, base_url: str, tenant_id: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "X-Tenant-ID": tenant_id,
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def test_agent(self, agent_name: str, test_data: dict) -> dict:
        """Prueba un agente específico"""
        url = f"{self.base_url}/agents/marketing/{agent_name}/execute"
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=self.headers, json=test_data, timeout=30)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "agent": agent_name,
                    "status": "success",
                    "result": response.json(),
                    "latency_ms": round(latency_ms, 1)
                }
            else:
                return {
                    "agent": agent_name,
                    "status": "error",
                    "http_status": response.status_code,
                    "error": response.text[:200],
                    "latency_ms": round(latency_ms, 1)
                }
        except Exception as e:
            return {
                "agent": agent_name,
                "status": "exception",
                "error": str(e),
                "latency_ms": 0
            }

# Configuración
BASE_URL = "https://nadakki-ai-suite.onrender.com"
TENANT_ID = "credicefi"
API_KEY = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"

tester = MarketingAgentsTester(BASE_URL, TENANT_ID, API_KEY)

# Datos de prueba para cada agente
test_cases = {
    "emailautomationia": {
        "input_data": {
            "lead_id": f"lead_test_{int(time.time())}",
            "email_template": "welcome_email",
            "recipient_data": {
                "name": "Carlos Ruiz",
                "email": "test@example.com",
                "company": "Test Corp"
            },
            "variables": {
                "offer": "Consulta gratuita",
                "contact": "asesor@credicefi.com"
            }
        }
    },
    
    "customersegmentatonia": {
        "input_data": {
            "customer_data": [
                {
                    "customer_id": "test_001",
                    "age": 30,
                    "income": 40000,
                    "last_purchase": "2024-01-20"
                }
            ]
        }
    },
    
    "abtestingia": {
        "input_data": {
            "control_group": {"visitors": 500, "conversions": 25},
            "variant_group": {"visitors": 500, "conversions": 30},
            "confidence_level": 0.95
        }
    },
    
    "productaffinityia": {
        "input_data": {
            "customer_id": "test_001",
            "purchase_history": [
                {"product": "loan", "date": "2024-01-01", "amount": 10000}
            ]
        }
    }
}

print("🧪 PROBANDO AGENTES DE MARKETING")
print("=" * 60)

for agent_name, test_data in test_cases.items():
    print(f"\n📋 Probando {agent_name}...")
    result = tester.test_agent(agent_name, test_data)
    
    if result["status"] == "success":
        print(f"   ✅ ÉXITO - Latencia: {result['latency_ms']}ms")
        if "result" in result and result["result"]:
            print(f"   📊 Resultado: {json.dumps(result['result'], indent=2)[:300]}...")
    elif result["status"] == "error":
        print(f"   ❌ ERROR {result.get('http_status', '')}: {result.get('error', '')}")
    else:
        print(f"   🔥 EXCEPCIÓN: {result.get('error', '')}")
