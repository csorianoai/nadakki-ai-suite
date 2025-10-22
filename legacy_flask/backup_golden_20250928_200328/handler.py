# AWS Lambda Handler usando Mangum
from mangum import Mangum
import sys
import os

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    
    # Crear aplicación Flask
    app = create_app()
    
    # Configurar Mangum para Lambda
    handler = Mangum(app, lifespan="off")
    
    print("✅ Nadakki AI Suite Lambda Handler configurado exitosamente")
    
except Exception as e:
    print(f"❌ Error configurando handler: {e}")
    raise e

# Handler function para AWS Lambda
def lambda_handler(event, context):
    return handler(event, context)
