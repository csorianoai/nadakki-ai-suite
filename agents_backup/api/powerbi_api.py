from flask import Blueprint, request, jsonify
from integrations.powerbi_enterprise import create_powerbi_connector
from core.tenant.tenant_manager import TenantManager
from core.auth.auth_middleware import require_tenant_auth
from utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

powerbi_bp = Blueprint('powerbi', __name__)
tenant_manager = TenantManager()

@powerbi_bp.route('/sync/historical', methods=['POST'])
@require_tenant_auth
def sync_historical_data():
    """Sincronizar datos históricos con PowerBI"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        if not tenant_config:
            return error_response("Tenant no encontrado", 404)
        
        # Crear conector PowerBI
        connector = create_powerbi_connector(tenant_config)
        if not connector:
            return error_response("PowerBI no habilitado para este tenant", 400)
        
        # Obtener datos del request
        historical_data = request.json.get('historical_data', [])
        
        if not historical_data:
            return error_response("No se proporcionaron datos históricos", 400)
        
        # Sincronizar con PowerBI
        success = connector.sync_historical_defaults(tenant_id, historical_data)
        
        if success:
            return success_response({
                'message': 'Datos históricos sincronizados exitosamente',
                'records_synced': len(historical_data),
                'tenant_id': tenant_id
            })
        else:
            return error_response("Error sincronizando con PowerBI", 500)
            
    except Exception as e:
        logger.error(f"Error en sync histórico: {str(e)}")
        return error_response("Error interno del servidor", 500)

@powerbi_bp.route('/sync/evaluations', methods=['POST']) 
@require_tenant_auth
def sync_evaluations():
    """Sincronizar evaluaciones IA con PowerBI"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        connector = create_powerbi_connector(tenant_config)
        if not connector:
            return error_response("PowerBI no habilitado", 400)
        
        evaluations = request.json.get('evaluations', [])
        
        success = connector.push_evaluation_results(tenant_id, evaluations)
        
        if success:
            return success_response({
                'message': 'Evaluaciones sincronizadas',
                'evaluations_count': len(evaluations)
            })
        else:
            return error_response("Error enviando evaluaciones", 500)
            
    except Exception as e:
        logger.error(f"Error sync evaluaciones: {str(e)}")
        return error_response("Error interno", 500)

@powerbi_bp.route('/refresh/<dataset_type>', methods=['POST'])
@require_tenant_auth
def refresh_dataset(dataset_type):
    """Refrescar dataset específico"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID') 
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        connector = create_powerbi_connector(tenant_config)
        if not connector:
            return error_response("PowerBI no habilitado", 400)
        
        success = connector.refresh_dataset(dataset_type)
        
        if success:
            return success_response({
                'message': f'Refresh iniciado para {dataset_type}',
                'dataset_type': dataset_type
            })
        else:
            return error_response("Error iniciando refresh", 500)
            
    except Exception as e:
        logger.error(f"Error refresh dataset: {str(e)}")
        return error_response("Error interno", 500)

@powerbi_bp.route('/status/<dataset_type>', methods=['GET'])
@require_tenant_auth  
def get_refresh_status(dataset_type):
    """Obtener estado de refresh de dataset"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        connector = create_powerbi_connector(tenant_config)
        if not connector:
            return error_response("PowerBI no habilitado", 400)
        
        status = connector.get_dataset_refresh_status(dataset_type)
        
        if status:
            return success_response({
                'dataset_type': dataset_type,
                'refresh_status': status
            })
        else:
            return error_response("No se pudo obtener estado", 500)
            
    except Exception as e:
        logger.error(f"Error obteniendo status: {str(e)}")
        return error_response("Error interno", 500)

@powerbi_bp.route('/validate', methods=['GET'])
@require_tenant_auth
def validate_powerbi_connection():
    """Validar conexión completa PowerBI"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        connector = create_powerbi_connector(tenant_config)
        if not connector:
            return error_response("PowerBI no habilitado", 400)
        
        validation_results = connector.validate_connection()
        
        all_valid = all(validation_results.values())
        
        return success_response({
            'tenant_id': tenant_id,
            'powerbi_status': 'healthy' if all_valid else 'issues_detected',
            'validation_results': validation_results,
            'workspace_name': tenant_config['powerbi_integration']['workspace_name']
        })
            
    except Exception as e:
        logger.error(f"Error validando PowerBI: {str(e)}")
        return error_response("Error interno", 500)

@powerbi_bp.route('/datasets', methods=['GET'])
@require_tenant_auth
def list_datasets():
    """Listar datasets configurados para el tenant"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        tenant_config = tenant_manager.get_tenant_config(tenant_id)
        
        powerbi_config = tenant_config.get('powerbi_integration', {})
        
        if not powerbi_config.get('enabled', False):
            return error_response("PowerBI no habilitado", 400)
        
        return success_response({
            'tenant_id': tenant_id,
            'workspace_name': powerbi_config['workspace_name'],
            'datasets': powerbi_config['datasets'],
            'refresh_schedule': powerbi_config.get('refresh_schedule', {}),
            'auto_sync': powerbi_config.get('auto_sync', False)
        })
        
    except Exception as e:
        logger.error(f"Error listando datasets: {str(e)}")
        return error_response("Error interno", 500)
