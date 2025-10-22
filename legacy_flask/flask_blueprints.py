# flask_blueprints.py - Integración con Flask Existente
from flask import Blueprint, request, jsonify
import sys
import os
from datetime import datetime, timedelta
import sqlite3

# Añadir el directorio de extensiones al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Crear blueprint para cobranza
collections_bp = Blueprint('collections', __name__, url_prefix='/api/v1/collections')

def get_tenant_id():
    tenant_id = request.headers.get('X-Tenant-ID')
    if not tenant_id:
        return None
    return tenant_id

def validate_tenant():
    tenant_id = get_tenant_id()
    if not tenant_id:
        return jsonify({'error': 'Header X-Tenant-ID requerido'}), 400
    
    valid_tenants = ['credicefi']
    if tenant_id not in valid_tenants:
        return jsonify({'error': 'Tenant no válido'}), 403
    
    return None

@collections_bp.before_request
def before_request():
    validation_error = validate_tenant()
    if validation_error:
        return validation_error

@collections_bp.route('/health', methods=['GET'])
def health_check():
    try:
        tenant_id = get_tenant_id()
        
        conn = sqlite3.connect('nadakki.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'module': 'collections',
            'tenant_id': tenant_id,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@collections_bp.route('/cases', methods=['POST'])
def create_case():
    try:
        from collections.collections_engine import CollectionsEngine
        
        tenant_id = get_tenant_id()
        data = request.get_json()
        
        if not data or not data.get('debtor_id'):
            return jsonify({'error': 'debtor_id es requerido'}), 400
        
        engine = CollectionsEngine(tenant_id)
        case = engine.create_case(
            debtor_id=data['debtor_id'],
            debt_amount=data.get('debt_amount', 0)
        )
        
        return jsonify({
            'success': True,
            'case': case,
            'message': 'Caso creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/cases/<int:case_id>', methods=['GET'])
def get_case(case_id):
    try:
        from collections.collections_engine import CollectionsEngine
        
        tenant_id = get_tenant_id()
        engine = CollectionsEngine(tenant_id)
        case = engine.get_case(case_id)
        
        if not case:
            return jsonify({'error': 'Caso no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'case': case
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/calls/queue', methods=['POST'])
def enqueue_call():
    try:
        from voice.voice_orchestrator import VoiceOrchestrator
        
        tenant_id = get_tenant_id()
        data = request.get_json()
        
        required_fields = ['debtor_id', 'phone_number']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        orchestrator = VoiceOrchestrator(tenant_id)
        queue_id = orchestrator.enqueue_call(
            debtor_id=data['debtor_id'],
            phone_number=data['phone_number'],
            case_id=data.get('case_id'),
            priority=data.get('priority', 2)
        )
        
        if queue_id > 0:
            return jsonify({
                'success': True,
                'queue_id': queue_id,
                'message': 'Llamada encolada exitosamente'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo encolar la llamada'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/calls/metrics', methods=['GET'])
def get_call_metrics():
    try:
        from voice.voice_orchestrator import VoiceOrchestrator
        
        tenant_id = get_tenant_id()
        hours_back = request.args.get('hours', 24, type=int)
        
        orchestrator = VoiceOrchestrator(tenant_id)
        metrics = orchestrator.get_call_metrics(hours_back)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/compliance/validate', methods=['POST'])
def validate_compliance():
    try:
        from compliance.indotel_enforcer import INDOTELEnforcer
        
        tenant_id = get_tenant_id()
        data = request.get_json()
        
        if not data or not data.get('debtor_id') or not data.get('phone_number'):
            return jsonify({'error': 'debtor_id y phone_number son requeridos'}), 400
        
        enforcer = INDOTELEnforcer(tenant_id)
        can_call, reason = enforcer.validate_call_permission(
            data['debtor_id'], 
            data['phone_number']
        )
        
        return jsonify({
            'success': True,
            'can_call': can_call,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/compliance/report', methods=['GET'])
def get_compliance_report():
    try:
        from compliance.indotel_enforcer import INDOTELEnforcer
        
        tenant_id = get_tenant_id()
        days_back = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        enforcer = INDOTELEnforcer(tenant_id)
        report = enforcer.get_compliance_report(start_date, end_date)
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/costs/status', methods=['GET'])
def get_cost_status():
    try:
        from voice.cost_governor import CostGovernor
        
        tenant_id = get_tenant_id()
        governor = CostGovernor(tenant_id)
        status = governor.get_current_spending_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collections_bp.route('/costs/recommendations', methods=['GET'])
def get_cost_recommendations():
    try:
        from voice.cost_governor import CostGovernor
        
        tenant_id = get_tenant_id()
        governor = CostGovernor(tenant_id)
        recommendations = governor.get_cost_optimization_recommendations()
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_collections_blueprint(app):
    app.register_blueprint(collections_bp)
    print("Blueprint de cobranza CrediFace registrado exitosamente")

print("Flask blueprints para cobranza creados correctamente")
