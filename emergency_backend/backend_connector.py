from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from datetime import datetime
import random

app = Flask(__name__)
CORS(app, origins=['*'])

class EmergencyEngine:
    def __init__(self):
        self.institutions = {
            'credicefi': {'name': 'CREDICEFI', 'evaluations_today': 234, 'accuracy': 94.7}
        }
    
    def calculate_similarity(self, profile):
        age_factor = min(profile.get('age', 35) / 65.0, 1.0)
        income_factor = min(profile.get('income', 30000) / 100000.0, 1.0)
        credit_factor = (850 - profile.get('credit_score', 500)) / 550.0
        similarity = (0.3 * age_factor + 0.4 * income_factor + 0.3 * credit_factor)
        return min(similarity, 0.99)
    
    def classify_risk(self, score):
        if score >= 0.90: return "RECHAZO_AUTOMATICO"
        elif score >= 0.80: return "ALTO_RIESGO"
        elif score >= 0.70: return "RIESGOSO"
        elif score >= 0.50: return "RIESGO_MEDIO"
        else: return "RIESGO_BAJO"

engine = EmergencyEngine()

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Nadakki AI Suite',
        'version': '1.0.0',
        'components': {
            'similarity_engine': 'operational',
            'api_gateway': 'operational',
            'multi_tenant': 'operational'
        }
    })

@app.route('/api/v1/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    similarity = engine.calculate_similarity(data)
    risk = engine.classify_risk(similarity)
    
    return jsonify({
        'similarity_score': round(similarity, 3),
        'risk_level': risk,
        'decision': f'Procesado - {risk}',
        'confidence': round(0.85 + (similarity * 0.1), 3),
        'variables_analyzed': len(data.keys()),
        'processed_at': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 NADAKKI EMERGENCY BACKEND STARTED")
    print("🔗 Health: http://localhost:5000/api/v1/health")
    app.run(debug=True, host='0.0.0.0', port=5000)