import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseConfig:
    def __init__(self):
        self.configs = {
            'development': {
                'url': 'sqlite:///nadakki_dev.db',
                'pool_size': 5
            },
            'production': {
                'url': os.getenv('DATABASE_URL', 'postgresql://nadakki:password@localhost:5432/nadakki_prod'),
                'pool_size': 20,
                'max_overflow': 30,
                'pool_timeout': 30,
                'pool_recycle': 3600
            }
        }
    
    def get_engine(self, env='production'):
        config = self.configs[env]
        return create_engine(
            config['url'],
            poolclass=QueuePool,
            pool_size=config.get('pool_size', 20),
            max_overflow=config.get('max_overflow', 30),
            pool_timeout=config.get('pool_timeout', 30),
            pool_recycle=config.get('pool_recycle', 3600),
            echo=False
        )

# Middleware Multi-Tenant
class TenantMiddleware:
    def __init__(self, app):
        self.app = app
        self.tenant_configs = self.load_tenant_configs()
    
    def load_tenant_configs(self):
        import json
        import glob
        configs = {}
        for config_file in glob.glob('public/config/tenants/*.json'):
            with open(config_file, 'r') as f:
                tenant_data = json.load(f)
                tenant_id = os.path.basename(config_file).replace('.json', '')
                configs[tenant_id] = tenant_data
        return configs
    
    def __call__(self, environ, start_response):
        tenant_id = environ.get('HTTP_X_TENANT_ID', 'default')
        if tenant_id not in self.tenant_configs:
            tenant_id = 'credicefi'  # Default fallback
        
        environ['TENANT_ID'] = tenant_id
        environ['TENANT_CONFIG'] = self.tenant_configs[tenant_id]
        return self.app(environ, start_response)

# Aplicar middleware al app principal
if __name__ == '__main__':
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    app = TenantMiddleware(app)
