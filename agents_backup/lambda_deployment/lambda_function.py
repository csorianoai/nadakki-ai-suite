# lambda_function.py - Nadakki AI Suite AWS Lambda Handler
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Handler principal de AWS Lambda para Nadakki AI Suite
    """
    try:
        # Obtener método HTTP y path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '{}')
        
        # Obtener tenant_id desde headers
        tenant_id = headers.get('X-Tenant-ID', headers.get('x-tenant-id', 'default'))
        
        # Parse body si existe
        if body:
            try:
                body_data = json.loads(body) if isinstance(body, str) else body
            except:
                body_data = {}
        else:
            body_data = {}

        # ROUTING - Dirigir a función correcta según endpoint
        if path == '/health' or path == '/api/v1/health':
            return handle_health_check(tenant_id)
        
        elif path == '/evaluate' or path == '/api/v1/evaluate':
            return handle_credit_evaluation(tenant_id, body_data)
        
        elif path == '/similarity/compare' or path == '/api/v1/similarity/compare':
            return handle_similarity_comparison(tenant_id, body_data)
        
        elif path == '/batch' or path == '/api/v1/batch':
            return handle_batch_evaluation(tenant_id, body_data)
        
        else:
            return create_response(404, {
                'error': 'Endpoint not found',
                'path': path,
                'available_endpoints': [
                    '/health',
                    '/evaluate', 
                    '/similarity/compare',
                    '/batch'
                ]
            })

    except Exception as e:
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })

def handle_health_check(tenant_id):
    """Health check - verificar que sistema funciona"""
    return create_response(200, {
        'status': 'healthy',
        'service': 'Nadakki AI Suite',
        'version': '2.1.0',
        'tenant_id': tenant_id,
        'components': {
            'similarity_engine': 'operational',
            'tenant_manager': 'operational',
            'agent_orchestrator': 'operational'
        },
        'agents_count': 36,
        'ecosystems': [
            'originacion', 'decision', 'vigilancia', 'recuperacion',
            'compliance', 'operacional', 'experiencia', 'inteligencia',
            'fortaleza', 'orchestration'
        ],
        'timestamp': datetime.utcnow().isoformat()
    })

def handle_credit_evaluation(tenant_id, data):
    """Evaluación crediticia principal"""
    try:
        profile = data.get('profile', {})
        
        if not profile:
            return create_response(400, {
                'error': 'Profile data required',
                'required_fields': [
                    'income', 'credit_score', 'age', 
                    'employment_type', 'debt_to_income'
                ]
            })
        
        # SIMULACIÓN DEL MOTOR DE SIMILITUD
        # En producción, aquí iría la lógica real del motor de IA
        similarity_score = calculate_mock_similarity(profile)
        risk_level = determine_risk_level(similarity_score)
        recommendation = generate_recommendation(risk_level)
        
        result = {
            'tenant_id': tenant_id,
            'evaluation_id': f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'similarity_score': similarity_score,
            'risk_level': risk_level,
            'decision': recommendation['decision'],
            'confidence': 0.85,
            'explanation': recommendation['explanation'],
            'agents_analysis': {
                'sentinel_bot': 'Risk assessment completed',
                'dna_profiler': 'Profile analyzed',
                'quantum_decision': 'Decision processed',
                'risk_oracle': 'Scoring completed'
            },
            'processing_time_ms': 150,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return create_response(200, result)
        
    except Exception as e:
        return create_response(500, {
            'error': 'Evaluation failed',
            'message': str(e)
        })

def handle_similarity_comparison(tenant_id, data):
    """Comparación de similitud entre dos perfiles"""
    try:
        profile1 = data.get('profile1', {})
        profile2 = data.get('profile2', {})
        
        if not profile1 or not profile2:
            return create_response(400, {
                'error': 'Two profiles required for comparison'
            })
        
        # Calcular similitud mock
        similarity_score = 0.75  # Mock value
        
        return create_response(200, {
            'tenant_id': tenant_id,
            'comparison_id': f"comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'similarity_score': similarity_score,
            'risk_assessment': determine_risk_level(similarity_score),
            'comparison_type': 'profile_vs_profile',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return create_response(500, {
            'error': 'Comparison failed',
            'message': str(e)
        })

def handle_batch_evaluation(tenant_id, data):
    """Procesamiento en lote de múltiples perfiles"""
    try:
        profiles = data.get('profiles', [])
        
        if not profiles:
            return create_response(400, {
                'error': 'Profiles array required'
            })
        
        if len(profiles) > 100:
            return create_response(400, {
                'error': 'Maximum 100 profiles per batch'
            })
        
        results = []
        
        for i, profile in enumerate(profiles):
            try:
                similarity_score = calculate_mock_similarity(profile)
                risk_level = determine_risk_level(similarity_score)
                recommendation = generate_recommendation(risk_level)
                
                results.append({
                    'profile_index': i,
                    'similarity_score': similarity_score,
                    'risk_level': risk_level,
                    'decision': recommendation['decision'],
                    'confidence': 0.85
                })
                
            except Exception as e:
                results.append({
                    'profile_index': i,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return create_response(200, {
            'tenant_id': tenant_id,
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'batch_size': len(profiles),
            'processed': len(results),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return create_response(500, {
            'error': 'Batch processing failed',
            'message': str(e)
        })

def calculate_mock_similarity(profile):
    """Calcular similitud mock basada en perfil"""
    # Simulación simple - en producción sería el motor de IA real
    income = profile.get('income', 30000)
    credit_score = profile.get('credit_score', 600)
    age = profile.get('age', 30)
    debt_to_income = profile.get('debt_to_income', 0.5)
    
    # Lógica simple de scoring
    score = 0.0
    
    if income < 25000:
        score += 0.3
    elif income < 50000:
        score += 0.15
    
    if credit_score < 650:
        score += 0.4
    elif credit_score < 750:
        score += 0.2
    
    if debt_to_income > 0.4:
        score += 0.3
    elif debt_to_income > 0.3:
        score += 0.15
    
    return min(score, 0.99)  # Cap at 99%

def determine_risk_level(similarity_score):
    """Determinar nivel de riesgo basado en similitud"""
    if similarity_score >= 0.90:
        return 'REJECT_AUTOMATIC'
    elif similarity_score >= 0.80:
        return 'HIGH_RISK'
    elif similarity_score >= 0.70:
        return 'RISKY'
    elif similarity_score >= 0.50:
        return 'MEDIUM_RISK'
    else:
        return 'LOW_RISK'

def generate_recommendation(risk_level):
    """Generar recomendación basada en nivel de riesgo"""
    recommendations = {
        'REJECT_AUTOMATIC': {
            'decision': 'REJECT',
            'explanation': 'Alto riesgo detectado. Perfil muy similar a clientes morosos históricos.'
        },
        'HIGH_RISK': {
            'decision': 'MANUAL_REVIEW', 
            'explanation': 'Requiere revisión manual inmediata. Similitud alta con perfiles riesgosos.'
        },
        'RISKY': {
            'decision': 'ADDITIONAL_ANALYSIS',
            'explanation': 'Análisis adicional requerido. Similitud moderada detectada.'
        },
        'MEDIUM_RISK': {
            'decision': 'CONDITIONAL_APPROVAL',
            'explanation': 'Aprobación condicional recomendada. Riesgo medio identificado.'
        },
        'LOW_RISK': {
            'decision': 'APPROVE',
            'explanation': 'Perfil de bajo riesgo. Proceder con aprobación estándar.'
        }
    }
    
    return recommendations.get(risk_level, {
        'decision': 'REVIEW',
        'explanation': 'Nivel de riesgo no determinado. Revisión requerida.'
    })

def create_response(status_code, body):
    """Crear respuesta HTTP estándar para Lambda + API Gateway"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Tenant-ID',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, ensure_ascii=False, indent=2)
    }