"""
Blueprint Collections para Nadakki Enterprise - Versión Corregida
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import logging
from datetime import datetime

# Blueprint con nombre único
collections_bp = Blueprint(
    'nadakki_collections',  # Nombre único para evitar conflictos
    __name__, 
    url_prefix='/api/v1/collections'
)

logger = logging.getLogger(__name__)

def get_tenant_id() -> str:
    return request.headers.get('X-Tenant-ID', 'credicefi')

def validate_indotel_window() -> bool:
    hora_actual = datetime.now().hour
    return 7 <= hora_actual < 19

class CollectionsManager:
    def __init__(self):
        self.agentes_activos = 36
        self.ecosistemas = [
            "originacion_segmentacion", "decision_inteligente", 
            "vigilancia_monitoreo", "recuperacion_avanzada",
            "compliance_normativo", "excelencia_operacional",
            "experiencia_deudor", "inteligencia_financiera",
            "fortaleza_digital"
        ]
    
    def clasificar_deudor(self, datos_deudor):
        monto = datos_deudor.get('monto_deuda', 0)
        dias_vencido = datos_deudor.get('dias_vencido', 0)
        
        if monto > 100000 and dias_vencido > 90:
            return {"segmento": "alto_riesgo", "prioridad": 1, "estrategia": "contacto_telefonico"}
        elif monto > 50000 or dias_vencido > 60:
            return {"segmento": "medio_riesgo", "prioridad": 3, "estrategia": "contacto_telefonico"}
        else:
            return {"segmento": "bajo_riesgo", "prioridad": 5, "estrategia": "email_sms"}

collections_manager = CollectionsManager()

@collections_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "nadakki-collections-enterprise",
        "version": "3.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agentes_activos": collections_manager.agentes_activos,
        "ecosistemas": len(collections_manager.ecosistemas)
    })

@collections_bp.route('/casos', methods=['POST'])
@cross_origin()
def crear_caso_cobranza():
    try:
        tenant_id = get_tenant_id()
        data = request.get_json()
        
        required_fields = ['deudor_id', 'monto_deuda', 'dias_vencido']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        clasificacion = collections_manager.clasificar_deudor(data)
        case_id = f"COL-{tenant_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            "case_id": case_id,
            "status": "creado",
            "tenant_id": tenant_id,
            "clasificacion": clasificacion,
            "created_at": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Error interno del sistema"}), 500

@collections_bp.route('/agentes', methods=['GET'])
@cross_origin()
def listar_agentes_collections():
    try:
        tenant_id = get_tenant_id()
        agentes_mock = [
            {"name": "segmentador_inteligente", "ecosistema": "originacion_segmentacion", "status": "active"},
            {"name": "motor_decisiones", "ecosistema": "decision_inteligente", "status": "active"},
            {"name": "validador_indotel", "ecosistema": "compliance_normativo", "status": "active"}
        ]
        
        return jsonify({
            "agentes": agentes_mock,
            "total_agentes": len(agentes_mock),
            "tenant_id": tenant_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error interno del sistema"}), 500

# Función de registro con verificación de duplicados
def register_collections_blueprint(app):
    try:
        # Verificar si ya está registrado
        if 'nadakki_collections' in [bp.name for bp in app.blueprints.values()]:
            app.logger.warning("Collections Blueprint ya registrado")
            return True
            
        app.register_blueprint(collections_bp)
        app.logger.info("Collections Blueprint registrado exitosamente")
        return True
    except Exception as e:
        app.logger.error(f"Error registrando Collections Blueprint: {e}")
        return False
