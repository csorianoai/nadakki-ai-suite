from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])  # Permitir TODOS los dominios

@app.route('/api/health')
def health_check():
    response = jsonify({
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Nadakki AI Suite',
        'version': '1.0.0'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-Tenant-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/api/evaluate-credit', methods=['POST', 'OPTIONS'])
def evaluate_credit():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-Tenant-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID', 'credicefi')
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    # Algoritmo de evaluación
    income = float(data.get('income', 0))
    credit_score = int(data.get('credit_score', 500))
    debt_ratio = float(data.get('debt_ratio', 0.5))
    
    risk_score = 0
    if income < 25000: risk_score += 30
    elif income < 50000: risk_score += 15
    else: risk_score += 5
    
    if credit_score < 500: risk_score += 40
    elif credit_score < 650: risk_score += 25
    elif credit_score < 750: risk_score += 10
    
    if debt_ratio > 0.8: risk_score += 30
    elif debt_ratio > 0.5: risk_score += 20
    elif debt_ratio > 0.3: risk_score += 10
    
    if risk_score <= 20:
        risk_level, recommendation = 'BAJO', 'APROBADO'
    elif risk_score <= 40:
        risk_level, recommendation = 'MEDIO', 'REVISAR'
    elif risk_score <= 60:
        risk_level, recommendation = 'ALTO', 'CONDICIONAL'
    else:
        risk_level, recommendation = 'MUY ALTO', 'RECHAZADO'
    
    response = jsonify({
        'status': 'success',
        'customer_id': data.get('customer_id', 'N/A'),
        'tenant_id': tenant_id,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'recommendation': recommendation,
        'score': 100 - risk_score,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-Tenant-ID')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    
    return response

if __name__ == '__main__':
    print("Nadakki AI Suite con CORS FIJO iniciando...")
    print("Puerto: 5000")
    print("Health: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=5000, debug=False)