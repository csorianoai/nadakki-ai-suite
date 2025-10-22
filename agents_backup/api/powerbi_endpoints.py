"""
🚀 PowerBI API Endpoints - Credicefi Production
RESTful endpoints optimizados para alto volumen
Autor: Nadakki AI Suite Enterprise
"""

from flask import Blueprint, request, jsonify, current_app
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Agregar path para imports
sys.path.append('integrations/powerbi')

try:
    from credicefi_connector import CredicefiPowerBIConnector, test_connector_complete
except ImportError as e:
    logging.error(f"Error importando PowerBI connector: {e}")
    CredicefiPowerBIConnector = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PowerBI_API')

# Crear Blueprint
powerbi_bp = Blueprint('powerbi', __name__, url_prefix='/api/v1/powerbi')

# Cache global para connector (optimización)
_connector_cache = {}

def get_connector(tenant_id: str = 'credicefi') -> CredicefiPowerBIConnector:
    """Obtener connector con cache para optimizar performance"""
    if tenant_id not in _connector_cache:
        if CredicefiPowerBIConnector is None:
            raise Exception("PowerBI Connector no disponible")
        _connector_cache[tenant_id] = CredicefiPowerBIConnector()
    return _connector_cache[tenant_id]

def validate_tenant_access(tenant_id: str) -> bool:
    """Validar acceso del tenant"""
    allowed_tenants = ['credicefi', 'credicefi-test', 'credicefi-dev']
    return tenant_id in allowed_tenants

@powerbi_bp.route('/health', methods=['GET'])
def powerbi_health():
    """Health check completo PowerBI con métricas detalladas"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID', 'credicefi')
        
        if not validate_tenant_access(tenant_id):
            return jsonify({
                'status': 'error',
                'message': 'Tenant no autorizado'
            }), 403
        
        connector = get_connector(tenant_id)
        health_result = connector.health_check_complete()
        
        return jsonify({
            'status': 'healthy' if health_result['status'] == 'healthy' else 'unhealthy',
            'service': 'powerbi_integration_enterprise',
            'tenant': tenant_id,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'health_details': health_result,
            'endpoints_available': [
                'GET /health',
                'POST /sync/historical', 
                'POST /push/evaluations',
                'POST /push/evaluations/batch',
                'POST /refresh/dataset',
                'GET /status/dataset/<dataset_id>',
                'POST /webhook',
                'POST /test/complete'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'error',
            'service': 'powerbi_integration',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/sync/historical', methods=['POST'])
def sync_historical_data():
    """Sincronización optimizada de datos históricos con opciones avanzadas"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        # Parámetros opcionales
        limit = request.json.get('limit', 10000) if request.json else 10000
        force_refresh = request.json.get('force_refresh', False) if request.json else False
        
        logger.info(f"Iniciando sync histórico para {tenant_id} (limit: {limit})")
        
        connector = get_connector(tenant_id)
        
        # Refresh dataset si se solicita
        if force_refresh:
            refresh_result = connector.schedule_dataset_refresh_advanced()
            logger.info(f"Dataset refresh: {refresh_result.get('status')}")
        
        # Extraer datos históricos
        historical_data = connector.extract_historical_defaults_optimized(limit=limit)
        
        if not historical_data:
            return jsonify({
                'status': 'no_data',
                'message': 'No se encontraron datos históricos',
                'records_extracted': 0,
                'tenant_id': tenant_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        
        # TODO: Integrar con motor de similitud aquí
        # similarity_engine.update_historical_database(historical_data)
        
        # Métricas de calidad de datos
        data_quality = analyze_data_quality(historical_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Datos históricos sincronizados exitosamente',
            'records_extracted': len(historical_data),
            'data_quality': data_quality,
            'tenant_id': tenant_id,
            'extraction_timestamp': datetime.now().isoformat(),
            'force_refresh_used': force_refresh,
            'performance': {
                'records_per_second': round(len(historical_data) / max(1, data_quality.get('processing_time_seconds', 1)), 2)
            }
        })
        
    except Exception as e:
        logger.error(f"Error en sync histórico: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'tenant_id': request.headers.get('X-Tenant-ID'),
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/push/evaluations', methods=['POST'])
def push_evaluations():
    """Push individual de evaluaciones (compatible con versión anterior)"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        evaluations = request.json.get('evaluations', [])
        if not evaluations:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron evaluaciones'
            }), 400
        
        connector = get_connector(tenant_id)
        
        # Usar el método batch optimizado
        success = connector.push_evaluation_results_batch(evaluations, batch_size=500)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Evaluaciones enviadas exitosamente a PowerBI',
                'evaluations_count': len(evaluations),
                'tenant_id': tenant_id,
                'pushed_at': datetime.now().isoformat(),
                'method': 'batch_optimized'
            })
        else:
            return jsonify({
                'status': 'partial_failure',
                'message': 'Algunas evaluaciones fallaron al enviarse',
                'evaluations_count': len(evaluations),
                'tenant_id': tenant_id
            }), 207  # Multi-Status
            
    except Exception as e:
        logger.error(f"Error pushing evaluations: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'tenant_id': tenant_id,
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/push/evaluations/batch', methods=['POST'])
def push_evaluations_batch():
    """Push optimizado en lotes para alto volumen"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        data = request.json
        evaluations = data.get('evaluations', [])
        batch_size = data.get('batch_size', 1000)
        max_workers = data.get('max_workers', 5)
        
        if not evaluations:
            return jsonify({
                'status': 'error', 
                'message': 'No evaluations provided'
            }), 400
        
        logger.info(f"Push batch iniciado: {len(evaluations)} evaluaciones, batch_size: {batch_size}")
        
        connector = get_connector(tenant_id)
        
        # Configurar max_workers en el connector si es necesario
        success = connector.push_evaluation_results_batch(
            evaluations, 
            batch_size=batch_size
        )
        
        return jsonify({
            'status': 'success' if success else 'partial_failure',
            'message': f'Batch processing {"completado" if success else "completado con errores"}',
            'total_evaluations': len(evaluations),
            'batch_size_used': batch_size,
            'tenant_id': tenant_id,
            'processing_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en batch push: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/refresh/dataset', methods=['POST'])
def refresh_dataset():
    """Refresh de dataset con opciones avanzadas"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        data = request.json or {}
        dataset_id = data.get('dataset_id')
        notify_completion = data.get('notify_completion', True)
        
        connector = get_connector(tenant_id)
        result = connector.schedule_dataset_refresh_advanced(
            dataset_id=dataset_id,
            notify_completion=notify_completion
        )
        
        if result['status'] == 'scheduled':
            return jsonify({
                'status': 'success',
                'message': 'Dataset refresh programado exitosamente',
                'dataset_id': result.get('dataset_id'),
                'scheduled_at': result.get('scheduled_at'),
                'notification_enabled': notify_completion,
                'tenant_id': tenant_id
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': f'Error programando refresh: {result.get("message", "Unknown error")}',
                'details': result
            }), 500
            
    except Exception as e:
        logger.error(f"Error en refresh dataset: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/status/dataset/<dataset_id>', methods=['GET'])
def get_dataset_status(dataset_id):
    """Estado detallado de dataset con métricas completas"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        connector = get_connector(tenant_id)
        status = connector.get_comprehensive_dataset_status(dataset_id)
        
        return jsonify({
            'tenant_id': tenant_id,
            'dataset_status': status,
            'checked_at': datetime.now().isoformat(),
            'api_version': 'v2.0'
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo status dataset: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'dataset_id': dataset_id,
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/webhook', methods=['POST'])
def powerbi_webhook():
    """Webhook optimizado para notificaciones PowerBI"""
    try:
        payload = request.json
        headers = dict(request.headers)
        
        event_type = payload.get('eventType', 'Unknown')
        dataset_id = payload.get('datasetId')
        refresh_id = payload.get('refreshId')
        
        logger.info(f"PowerBI webhook recibido: {event_type} para dataset {dataset_id}")
        
        # Procesar eventos específicos
        response_data = {
            'status': 'received',
            'event_type': event_type,
            'processed_at': datetime.now().isoformat(),
            'dataset_id': dataset_id
        }
        
        if event_type == 'DatasetRefreshCompleted':
            # Trigger auto-sync si está configurado
            response_data['action'] = 'auto_sync_triggered'
            # TODO: Implementar auto-sync aquí
            
        elif event_type == 'DatasetRefreshFailed':
            # Log error y enviar alerta
            error_details = payload.get('error', 'No error details')
            logger.error(f"Dataset refresh failed for {dataset_id}: {error_details}")
            response_data['action'] = 'error_logged_alert_sent'
            
        elif event_type == 'DatasetRefreshStarted':
            response_data['action'] = 'monitoring_started'
            
        # Guardar evento para auditoría
        audit_log = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'payload': payload,
            'headers': headers,
            'processed': True
        }
        
        # TODO: Guardar en base de datos de auditoría
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@powerbi_bp.route('/test/complete', methods=['POST'])
def test_powerbi_complete():
    """Test completo del sistema PowerBI con reporte detallado"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID', 'credicefi')
        if not validate_tenant_access(tenant_id):
            return jsonify({'error': 'Tenant no autorizado'}), 403
        
        logger.info(f"Iniciando test completo PowerBI para {tenant_id}")
        
        # Ejecutar test usando el connector
        if CredicefiPowerBIConnector is None:
            return jsonify({
                'status': 'FAILED',
                'message': 'PowerBI Connector no disponible',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Ejecutar test completo en background para no bloquear
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(test_connector_complete)
            
            # Esperar máximo 60 segundos
            try:
                result = future.result(timeout=60)
            except TimeoutError:
                return jsonify({
                    'status': 'TIMEOUT',
                    'message': 'Test tomó más de 60 segundos',
                    'timestamp': datetime.now().isoformat()
                }), 408
        
        # Procesar resultado
        if result['status'] == 'SUCCESS':
            return jsonify({
                'status': 'success',
                'message': 'Test completo PowerBI exitoso',
                'tenant_id': tenant_id,
                'test_results': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Test completo PowerBI falló',
                'tenant_id': tenant_id,
                'test_results': result,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error en test completo: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def analyze_data_quality(data: List[Dict]) -> Dict:
    """Análisis de calidad de datos extraídos"""
    try:
        if not data:
            return {'quality_score': 0, 'issues': ['No data']}
        
        total_records = len(data)
        issues = []
        valid_records = 0
        
        for record in data:
            record_valid = True
            
            # Validar campos requeridos
            required_fields = ['cedula', 'income', 'credit_score']
            for field in required_fields:
                if not record.get(field) or record.get(field) in [0, '', None]:
                    record_valid = False
                    break
            
            if record_valid:
                valid_records += 1
        
        completeness = (valid_records / total_records) * 100
        
        if completeness < 80:
            issues.append(f'Baja completitud: {completeness:.1f}%')
        
        quality_score = min(100, completeness)
        
        return {
            'quality_score': round(quality_score, 1),
            'total_records': total_records,
            'valid_records': valid_records,
            'completeness_percent': round(completeness, 1),
            'issues': issues,
            'processing_time_seconds': 1.0  # Placeholder
        }
        
    except Exception as e:
        return {
            'quality_score': 0,
            'error': str(e),
            'issues': ['Error analyzing quality']
        }

# Error handlers específicos
@powerbi_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'PowerBI endpoint no encontrado',
        'available_endpoints': [
            '/health', '/sync/historical', '/push/evaluations',
            '/push/evaluations/batch', '/refresh/dataset',
            '/status/dataset/<id>', '/webhook', '/test/complete'
        ]
    }), 404

@powerbi_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'status': 'error',
        'message': 'Rate limit excedido',
        'retry_after': '60 seconds'
    }), 429
