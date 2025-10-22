# FASE 1: BACKEND CRÍTICO - IMPLEMENTACIÓN INMEDIATA
# Archivo: enhanced_app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import uuid

app = Flask(__name__)
CORS(app)

# ===== CONFIGURACIÓN MULTI-TENANT =====
INSTITUTION_CONFIGS = {
    'credicefi': {
        'name': 'CREDICEFI',
        'tenant_id': 'credicefi_001',
        'risk_thresholds': {
            'auto_reject': 0.90,
            'high_risk': 0.80,
            'risky': 0.70,
            'medium_risk': 0.50
        },
        'agents_enabled': [
            'SentinelBot', 'DNAProfiler', 'IncomeOracle', 'BehaviorMiner',
            'QuantumDecision', 'RiskOracle', 'PolicyGuardian', 'TurboApprover'
        ],
        'branding': {
            'primary_color': '#1a237e',
            'logo_url': '/assets/credicefi_logo.png'
        }
    },
    'banco_popular': {
        'name': 'Banco Popular',
        'tenant_id': 'bp_001',
        'risk_thresholds': {
            'auto_reject': 0.85,
            'high_risk': 0.75,
            'risky': 0.65,
            'medium_risk': 0.45
        },
        'agents_enabled': [
            'SentinelBot', 'DNAProfiler', 'RiskOracle', 'EarlyWarning'
        ],
        'branding': {
            'primary_color': '#c41e3a',
            'logo_url': '/assets/bp_logo.png'
        }
    }
}

# ===== BASE DE DATOS SINTÉTICA DE MOROSOS =====
def generate_morosos_database():
    """Genera base de datos sintética de 1000 perfiles de morosos"""
    morosos_profiles = []
    
    for i in range(1000):
        profile = {
            'age': random.randint(22, 65),
            'income': random.randint(15000, 80000),
            'employment_type_encoded': random.choice([0, 1, 2, 3]),  # 0=employed, 1=self_employed, 2=business_owner, 3=unemployed
            'credit_score': random.randint(300, 650),  # Scores bajos típicos de morosos
            'debt_to_income': random.uniform(0.6, 1.5),  # Alto DTI
            'credit_utilization': random.uniform(0.8, 1.0),  # Alta utilización
            'defaults_count': random.randint(1, 5),
            'monthly_expenses': random.randint(20000, 60000),
            'existing_debts': random.randint(50000, 300000),
            'civil_status_encoded': random.choice([0, 1, 2, 3]),  # 0=single, 1=married, 2=divorced, 3=widowed
            'education_encoded': random.choice([0, 1, 2, 3]),  # 0=high_school, 1=college, 2=graduate, 3=postgraduate
            'payment_history_encoded': random.choice([0, 1])  # 0=poor, 1=very_poor
        }
        morosos_profiles.append(profile)
    
    return pd.DataFrame(morosos_profiles)

# Generar la base de datos al iniciar
MOROSOS_DB = generate_morosos_database()
scaler = StandardScaler()
MOROSOS_SCALED = scaler.fit_transform(MOROSOS_DB)

# ===== MOTOR DE SIMILITUD HÍBRIDO =====
class EnhancedSimilarityEngine:
    def __init__(self):
        self.employment_mapping = {
            'employed': 0, 'self_employed': 1, 'business_owner': 2, 'unemployed': 3
        }
        self.civil_status_mapping = {
            'single': 0, 'married': 1, 'divorced': 2, 'widowed': 3
        }
        self.education_mapping = {
            'high_school': 0, 'college': 1, 'graduate': 2, 'postgraduate': 3
        }
        self.payment_history_mapping = {
            'excellent': 0, 'good': 1, 'fair': 2, 'poor': 3, 'very_poor': 4
        }
    
    def encode_profile(self, profile):
        """Convierte el perfil a formato numérico"""
        encoded = {
            'age': float(profile.get('age', 30)),
            'income': float(profile.get('income', 30000)),
            'employment_type_encoded': self.employment_mapping.get(profile.get('employment_type', 'employed'), 0),
            'credit_score': float(profile.get('credit_score', 500)),
            'debt_to_income': self.calculate_dti(profile),
            'credit_utilization': float(profile.get('credit_utilization', 0.5)),
            'defaults_count': float(profile.get('defaults_count', 0)),
            'monthly_expenses': float(profile.get('monthly_expenses', 25000)),
            'existing_debts': float(profile.get('existing_debts', 0)),
            'civil_status_encoded': self.civil_status_mapping.get(profile.get('civil_status', 'single'), 0),
            'education_encoded': self.education_mapping.get(profile.get('education', 'high_school'), 0),
            'payment_history_encoded': self.payment_history_mapping.get(profile.get('payment_history', 'good'), 1)
        }
        return encoded
    
    def calculate_dti(self, profile):
        """Calcula debt-to-income ratio"""
        income = float(profile.get('income', 30000))
        expenses = float(profile.get('monthly_expenses', 20000))
        debts = float(profile.get('existing_debts', 0))
        
        if income == 0:
            return 1.0
        
        monthly_debt_payment = debts / 60  # Asumiendo 5 años para pagar deudas
        total_obligations = expenses + monthly_debt_payment
        
        return min(total_obligations / income, 2.0)  # Cap at 200%
    
    def calculate_similarity(self, new_profile):
        """Calcula similitud híbrida con base de morosos"""
        encoded_profile = self.encode_profile(new_profile)
        profile_vector = np.array(list(encoded_profile.values())).reshape(1, -1)
        
        # Normalizar el perfil nuevo con el mismo scaler
        profile_scaled = scaler.transform(profile_vector)
        
        # 1. Similitud Coseno (40%)
        cosine_scores = cosine_similarity(profile_scaled, MOROSOS_SCALED)[0]
        cosine_max = np.max(cosine_scores)
        
        # 2. Distancia Euclidiana normalizada (30%)
        euclidean_distances = np.linalg.norm(MOROSOS_SCALED - profile_scaled, axis=1)
        euclidean_similarities = 1 / (1 + euclidean_distances)
        euclidean_max = np.max(euclidean_similarities)
        
        # 3. Similitud Jaccard para categóricas (30%)
        categorical_features = [2, 9, 10, 11]  # employment, civil_status, education, payment_history
        jaccard_scores = []
        
        for moroso_row in MOROSOS_DB.values:
            intersection = sum(1 for i in categorical_features 
                             if moroso_row[i] == encoded_profile[list(encoded_profile.keys())[i]])
            union = len(categorical_features)
            jaccard_scores.append(intersection / union if union > 0 else 0)
        
        jaccard_max = np.max(jaccard_scores)
        
        # 4. Weighted Ensemble
        final_score = (0.4 * cosine_max + 0.3 * euclidean_max + 0.3 * jaccard_max)
        
        return min(final_score, 0.99)  # Cap at 99%
    
    def classify_risk(self, similarity_score, tenant_config):
        """Clasifica el riesgo basado en umbrales del tenant"""
        thresholds = tenant_config['risk_thresholds']
        
        if similarity_score >= thresholds['auto_reject']:
            return "RECHAZO_AUTOMATICO"
        elif similarity_score >= thresholds['high_risk']:
            return "ALTO_RIESGO"
        elif similarity_score >= thresholds['risky']:
            return "RIESGOSO"
        elif similarity_score >= thresholds['medium_risk']:
            return "RIESGO_MEDIO"
        else:
            return "RIESGO_BAJO"
    
    def generate_decision(self, risk_level):
        """Genera decisión automática basada en nivel de riesgo"""
        decisions = {
            "RECHAZO_AUTOMATICO": "RECHAZAR - Sin intervención humana requerida",
            "ALTO_RIESGO": "RECHAZAR - Requiere supervisión de riesgo",
            "RIESGOSO": "REVISAR - Análisis adicional requerido",
            "RIESGO_MEDIO": "ESCALAMIENTO - Evaluación de segundo nivel",
            "RIESGO_BAJO": "APROBAR - Procesar normalmente"
        }
        return decisions.get(risk_level, "REVISAR")
    
    def calculate_confidence(self, similarity_score, variables_count):
        """Calcula confianza basada en score y variables disponibles"""
        base_confidence = 0.7  # Base del 70%
        score_factor = 0.2 * (1 - abs(similarity_score - 0.5) * 2)  # Más confianza en extremos
        variables_factor = min(0.1 * (variables_count / 10), 0.1)  # Más variables = más confianza
        
        return min(base_confidence + score_factor + variables_factor, 0.95)

# Inicializar el motor
similarity_engine = EnhancedSimilarityEngine()

# ===== SIMULADOR DE AGENTES =====
AGENT_CONFIGS = {
    'SentinelBot': {
        'name': 'SentinelBot Quantum',
        'description': 'Análisis predictivo de riesgo crediticio con ML',
        'icon': '🛡️',
        'accuracy': 94.7,
        'evaluations_count': 1234,
        'status': 'active'
    },
    'DNAProfiler': {
        'name': 'DNAProfiler Quantum',
        'description': 'Perfilado genómico crediticio avanzado',
        'icon': '🧬',
        'accuracy': 92.3,
        'evaluations_count': 987,
        'status': 'active'
    },
    'IncomeOracle': {
        'name': 'IncomeOracle',
        'description': 'Verificación automática de ingresos',
        'icon': '💰',
        'accuracy': 96.1,
        'evaluations_count': 756,
        'status': 'active'
    },
    'BehaviorMiner': {
        'name': 'BehaviorMiner',
        'description': 'Análisis de patrones transaccionales',
        'icon': '📊',
        'accuracy': 89.5,
        'evaluations_count': 654,
        'status': 'active'
    },
    'QuantumDecision': {
        'name': 'QuantumDecision Core',
        'description': 'Motor híbrido de decisiones principales',
        'icon': '⚛️',
        'accuracy': 97.2,
        'evaluations_count': 2156,
        'status': 'active'
    },
    'RiskOracle': {
        'name': 'RiskOracle',
        'description': 'Scoring multidimensional avanzado',
        'icon': '🔮',
        'accuracy': 93.8,
        'evaluations_count': 1789,
        'status': 'active'
    },
    'PolicyGuardian': {
        'name': 'PolicyGuardian',
        'description': 'Validación automática de políticas',
        'icon': '🛡️',
        'accuracy': 98.5,
        'evaluations_count': 543,
        'status': 'active'
    },
    'TurboApprover': {
        'name': 'TurboApprover',
        'description': 'Aprobación instantánea para bajo riesgo',
        'icon': '⚡',
        'accuracy': 99.1,
        'evaluations_count': 2344,
        'status': 'active'
    }
}

# ===== ENDPOINTS DE LA API =====

@app.route('/')
def home():
    return {
        'message': 'Nadakki AI Suite - Sistema de Evaluación Crediticia',
        'status': 'operational',
        'version': '2.0.0',
        'agents_available': len(AGENT_CONFIGS),
        'institutions_supported': len(INSTITUTION_CONFIGS),
        'endpoints': [
            'GET / - Información del sistema',
            'GET /api/v1/health - Health check',
            'POST /api/v1/evaluate - Evaluación crediticia principal',
            'GET /api/v1/institution/<id>/dashboard - Dashboard institucional',
            'POST /api/v1/agent/<id>/test - Test individual de agente',
            'GET /api/v1/agents/status - Estado de todos los agentes'
        ]
    }

@app.route('/api/v1/health')
def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'components': {
            'similarity_engine': 'operational',
            'api_gateway': 'operational',
            'multi_tenant': 'operational',
            'agent_registry': 'operational',
            'morosos_database': f'{len(MOROSOS_DB)} profiles loaded'
        }
    }

@app.route('/api/v1/evaluate', methods=['POST'])
def evaluate_credit():
    try:
        data = request.json
        tenant_id = request.headers.get('X-Tenant-ID', 'credicefi')
        
        # Obtener configuración del tenant
        if tenant_id not in INSTITUTION_CONFIGS:
            tenant_id = 'credicefi'  # Default fallback
        
        tenant_config = INSTITUTION_CONFIGS[tenant_id]
        
        # Calcular similitud
        similarity_score = similarity_engine.calculate_similarity(data)
        
        # Clasificar riesgo
        risk_level = similarity_engine.classify_risk(similarity_score, tenant_config)
        
        # Generar decisión
        decision = similarity_engine.generate_decision(risk_level)
        
        # Calcular confianza
        confidence = similarity_engine.calculate_confidence(similarity_score, len(data.keys()))
        
        result = {
            'evaluation_id': str(uuid.uuid4()),
            'institution': tenant_config['name'],
            'similarity_score': round(similarity_score, 4),
            'risk_level': risk_level,
            'decision': decision,
            'confidence': round(confidence, 3),
            'variables_analyzed': len(data.keys()),
            'processed_at': datetime.now().isoformat(),
            'processing_time_ms': random.randint(1200, 2800),  # Simular tiempo real
            'agents_used': tenant_config['agents_enabled'][:4],  # Primeros 4 agentes
            'recommendation': generate_recommendation(risk_level),
            'next_review_date': (datetime.now() + timedelta(days=30)).isoformat() if risk_level in ['RIESGO_MEDIO', 'RIESGOSO'] else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Error processing evaluation',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/institution/<institution_id>/dashboard')
def institution_dashboard(institution_id):
    if institution_id not in INSTITUTION_CONFIGS:
        return jsonify({'error': 'Institution not found'}), 404
    
    config = INSTITUTION_CONFIGS[institution_id]
    
    # Simular métricas en tiempo real
    base_time = datetime.now()
    
    dashboard_data = {
        'institution_name': config['name'],
        'tenant_id': config['tenant_id'],
        'last_updated': base_time.isoformat(),
        
        # Métricas principales
        'evaluations_today': random.randint(200, 300),
        'evaluations_week': random.randint(1400, 2000),
        'evaluations_month': random.randint(6000, 8500),
        
        # Performance
        'accuracy': round(random.uniform(93.5, 97.8), 1),
        'processing_time_avg': round(random.uniform(1.8, 2.9), 1),
        'uptime_percentage': round(random.uniform(99.2, 99.9), 2),
        
        # Distribución de riesgo
        'risk_distribution': {
            'RIESGO_BAJO': random.randint(45, 65),
            'RIESGO_MEDIO': random.randint(20, 30),
            'RIESGOSO': random.randint(8, 15),
            'ALTO_RIESGO': random.randint(3, 8),
            'RECHAZO_AUTOMATICO': random.randint(1, 5)
        },
        
        # Agentes activos
        'agents_active': len(config['agents_enabled']),
        'agents': [
            {
                'id': agent_id,
                **AGENT_CONFIGS[agent_id]
            }
            for agent_id in config['agents_enabled']
            if agent_id in AGENT_CONFIGS
        ],
        
        # Configuración
        'risk_thresholds': config['risk_thresholds'],
        'branding': config['branding']
    }
    
    return jsonify(dashboard_data)

@app.route('/api/v1/agent/<agent_id>/test', methods=['POST'])
def test_agent(agent_id):
    if agent_id not in AGENT_CONFIGS:
        return jsonify({'error': 'Agent not found'}), 404
    
    data = request.json or {}
    agent_config = AGENT_CONFIGS[agent_id]
    
    # Simular procesamiento del agente específico
    test_result = {
        'agent_id': agent_id,
        'agent_name': agent_config['name'],
        'test_id': str(uuid.uuid4()),
        'input_data': data,
        'timestamp': datetime.now().isoformat(),
        'processing_time_ms': random.randint(300, 800),
        'status': 'success',
        'confidence': round(random.uniform(0.85, 0.98), 3),
        'output': generate_agent_specific_output(agent_id, data)
    }
    
    return jsonify(test_result)

@app.route('/api/v1/agents/status')
def agents_status():
    return jsonify({
        'total_agents': len(AGENT_CONFIGS),
        'active_agents': len([a for a in AGENT_CONFIGS.values() if a['status'] == 'active']),
        'agents': AGENT_CONFIGS,
        'last_updated': datetime.now().isoformat()
    })

# ===== FUNCIONES AUXILIARES =====

def generate_recommendation(risk_level):
    recommendations = {
        "RECHAZO_AUTOMATICO": "Rechazar solicitud inmediatamente. Perfil de muy alto riesgo.",
        "ALTO_RIESGO": "Rechazar o solicitar garantías adicionales significativas.",
        "RIESGOSO": "Revisar manualmente. Considerar condiciones especiales o garantías.",
        "RIESGO_MEDIO": "Aprobación condicional. Monitoreo estrecho recomendado.",
        "RIESGO_BAJO": "Aprobar con condiciones estándar. Cliente de bajo riesgo."
    }
    return recommendations.get(risk_level, "Revisar caso particular.")

def generate_agent_specific_output(agent_id, input_data):
    """Genera output específico por agente"""
    outputs = {
        'SentinelBot': {
            'risk_score': round(random.uniform(0.1, 0.9), 3),
            'threat_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'patterns_detected': random.randint(2, 8),
            'recommendation': 'Proceder con evaluación estándar'
        },
        'DNAProfiler': {
            'personality_score': round(random.uniform(0.3, 0.8), 3),
            'behavioral_pattern': random.choice(['Conservative', 'Moderate', 'Aggressive']),
            'stability_index': round(random.uniform(0.6, 0.95), 3),
            'profile_summary': 'Perfil financiero estable con tendencias conservadoras'
        },
        'IncomeOracle': {
            'income_verified': random.choice([True, False]),
            'verification_score': round(random.uniform(0.7, 0.98), 3),
            'sources_checked': random.randint(2, 5),
            'consistency_rating': random.choice(['HIGH', 'MEDIUM', 'LOW'])
        },
        'BehaviorMiner': {
            'transaction_patterns': random.randint(5, 12),
            'anomaly_score': round(random.uniform(0.05, 0.3), 3),
            'spending_behavior': random.choice(['Regular', 'Irregular', 'Seasonal']),
            'risk_indicators': random.randint(0, 3)
        }
    }
    
    return outputs.get(agent_id, {
        'status': 'processed',
        'score': round(random.uniform(0.5, 0.9), 3),
        'message': f'Procesado por {agent_id}'
    })

if __name__ == '__main__':
    print("🚀 Iniciando Nadakki AI Suite - Sistema de Evaluación Crediticia")
    print("📊 Base de datos de morosos cargada:", len(MOROSOS_DB), "perfiles")
    print("🏢 Instituciones configuradas:", list(INSTITUTION_CONFIGS.keys()))
    print("🤖 Agentes disponibles:", len(AGENT_CONFIGS))
    print("🌐 Servidor corriendo en: http://localhost:5000")
    print("📋 Health check: http://localhost:5000/api/v1/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)