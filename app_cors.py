from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])  # Permitir todos los orígenes

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat(), 'service': 'Nadakki AI Suite'}

@app.route('/api/evaluate-credit', methods=['POST'])
def evaluate_credit():
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID', 'credicefi')
    
    # Tu lógica de evaluación aquí...
    risk_score = 15  # Simplificado para test
    
    return {
        'status': 'success',
        'customer_id': data['customer_id'],
        'tenant_id': tenant_id,
        'risk_level': 'BAJO',
        'recommendation': 'APROBADO',
        'score': 85,
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == '__main__':
    print('Servidor con CORS iniciando...')
    app.run(host='0.0.0.0', port=5000, debug=False)
