import requests
import json

def test_apis():
    base = 'http://localhost:5000'
    
    print("1. Probando Health Check...")
    try:
        r = requests.get(f'{base}/api/health')
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Probando Evaluación Crediticia...")
    data = {
        'customer_id': 'CLI001',
        'income': 75000,
        'credit_score': 720,
        'debt_ratio': 0.25
    }
    try:
        r = requests.post(f'{base}/api/evaluate-credit', 
                         json=data, 
                         headers={'X-Tenant-ID': 'credicefi'})
        print(f"   Status: {r.status_code}")
        result = r.json()
        print(f"   Cliente: {result['customer_id']}")
        print(f"   Riesgo: {result['risk_level']}")
        print(f"   Recomendación: {result['recommendation']}")
        print(f"   Score: {result['score']}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == '__main__':
    test_apis()
