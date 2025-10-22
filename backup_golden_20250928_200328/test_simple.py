import requests
import time

def test_nadakki():
    base_url = 'http://localhost:5000'
    
    print("Probando Health Check...")
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health Check OK")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("Probando Evaluación Crediticia...")
    test_data = {
        'customer_id': 'TEST001',
        'income': 50000,
        'credit_score': 750,
        'debt_ratio': 0.3
    }
    
    try:
        response = requests.post(f'{base_url}/api/evaluate-credit', 
                               json=test_data, 
                               headers={'X-Tenant-ID': 'credicefi'}, 
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Evaluación OK - Riesgo: {result.get('risk_level')}")
            print(f"   Recomendación: {result.get('recommendation')}")
            return True
        else:
            print(f"❌ Evaluación failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing Nadakki AI Suite...")
    success = test_nadakki()
    if success:
        print("🎉 TODOS LOS TESTS PASARON")
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
