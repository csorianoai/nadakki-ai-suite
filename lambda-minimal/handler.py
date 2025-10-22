# handler-minimal.py - Testing básico sin dependencias complejas
import json
import logging

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    '''Handler mínimo para testing 500 errors'''
    try:
        logger.info("=== LAMBDA HANDLER INICIADO ===")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Verificar estructura del evento
        http_method = event.get('httpMethod', 'UNKNOWN')
        path = event.get('path', '/')
        
        logger.info(f"HTTP Method: {http_method}")
        logger.info(f"Path: {path}")
        
        # Response básico
        response_body = {
            'message': 'Nadakki AI Suite - Handler Minimal Test',
            'status': 'working',
            'method': http_method,
            'path': path,
            'timestamp': '2025-07-27',
            'lambda_version': 'minimal-1.0'
        }
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Tenant-ID'
            },
            'body': json.dumps(response_body)
        }
        
        logger.info("=== RESPONSE GENERADO EXITOSAMENTE ===")
        logger.info(f"Response: {json.dumps(response, indent=2)}")
        
        return response
        
    except Exception as e:
        logger.error(f"ERROR EN HANDLER: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Response de error
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'type': type(e).__name__
            })
        }
        
        return error_response

# Para testing directo
if __name__ == '__main__':
    # Test event local
    test_event = {
        'httpMethod': 'GET',
        'path': '/',
        'headers': {},
        'body': None
    }
    
    result = lambda_handler(test_event, None)
    print("Local test result:", json.dumps(result, indent=2))
