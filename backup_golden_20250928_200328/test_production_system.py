import requests
import time
import json
from datetime import datetime

class NadakkiTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.results = []
    
    def log_result(self, test, success, message=""):
        result = {'test': test, 'success': success, 'message': message}
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test}: {message}")
    
    def test_health(self):
        try:
            response = requests.get(f'{self.base_url}/api/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Status: {data.get('status')}")
                return True
        except Exception as e:
            self.log_result("Health Check", False, str(e))
        return False
    
    def test_evaluation(self):
        test_data = {
            'customer_id': 'TEST001',
            'income': 50000,
            'credit_score': 750,
            'debt_ratio': 0.3
        }
        try:
            response = requests.post(f'{self.base_url}/api/evaluate-credit', 
                                   json=test_data, 
                                   headers={'X-Tenant-ID': 'credicefi'}, 
                                   timeout=15)
            if response.status_code == 200:
                result = response.json()
                self.log_result("Credit Evaluation", True, f"Risk: {result.get('risk_level')}")
                return True
        except Exception as e:
            self.log_result("Credit Evaluation", False, str(e))
        return False
    
    def run_tests(self):
        print("🚀 Iniciando tests Nadakki AI...")
        passed = 0
        total = 2
        
        if self.test_health():
            passed += 1
        if self.test_evaluation():
            passed += 1
            
        print(f"\n📊 Resultado: {passed}/{total} tests pasaron")
        return passed == total

if __name__ == '__main__':
    tester = NadakkiTester()
    success = tester.run_tests()
    exit(0 if success else 1)
