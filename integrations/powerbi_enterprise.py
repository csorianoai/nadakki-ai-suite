import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from msal import ConfidentialClientApplication
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class PowerBIConfig:
    client_id: str
    client_secret: str
    tenant_id: str
    workspace_name: str
    datasets: Dict[str, str]
    
class PowerBIEnterpriseConnector:
    """
    Conector Enterprise para PowerBI con funcionalidades avanzadas
    para múltiples tenants y sincronización bidireccional
    """
    
    def __init__(self, config: PowerBIConfig):
        self.config = config
        self.access_token = None
        self.token_expires = None
        self.authority = f"https://login.microsoftonline.com/{config.tenant_id}"
        self.scope = ['https://analysis.windows.net/powerbi/api/.default']
        
        # Cliente MSAL para autenticación
        self.app = ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=self.authority
        )
        
    def authenticate(self) -> bool:
        """Autenticar con PowerBI usando OAuth2"""
        try:
            result = self.app.acquire_token_for_client(scopes=self.scope)
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # Token válido por 1 hora, renovar 5 min antes
                self.token_expires = datetime.now() + timedelta(seconds=result['expires_in'] - 300)
                logger.info("Autenticación PowerBI exitosa")
                return True
            else:
                logger.error(f"Error autenticación PowerBI: {result.get('error_description')}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción en autenticación PowerBI: {str(e)}")
            return False
    
    def _ensure_token(self) -> bool:
        """Verificar token válido, renovar si es necesario"""
        if not self.access_token or datetime.now() >= self.token_expires:
            return self.authenticate()
        return True
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Realizar request a PowerBI API con manejo de errores"""
        if not self._ensure_token():
            return None
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"https://api.powerbi.com/v1.0/myorg{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {'success': True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error PowerBI API: {str(e)}")
            return None
    
    def get_workspace_id(self) -> Optional[str]:
        """Obtener ID del workspace por nombre"""
        workspaces = self._make_request('GET', '/groups')
        if not workspaces:
            return None
            
        for workspace in workspaces.get('value', []):
            if workspace['name'] == self.config.workspace_name:
                return workspace['id']
        
        logger.warning(f"Workspace '{self.config.workspace_name}' no encontrado")
        return None
    
    def sync_historical_defaults(self, tenant_id: str, data: List[Dict]) -> bool:
        """Sincronizar datos históricos de morosos"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return False
        
        dataset_name = self.config.datasets.get('historical_defaults')
        if not dataset_name:
            logger.error("Dataset historical_defaults no configurado")
            return False
        
        # Convertir datos a formato PowerBI
        df = pd.DataFrame(data)
        
        # Agregar metadata del tenant
        df['tenant_id'] = tenant_id
        df['sync_timestamp'] = datetime.now().isoformat()
        
        # Push data a PowerBI
        endpoint = f"/groups/{workspace_id}/datasets/{dataset_name}/tables/HistoricalDefaults/rows"
        
        # Enviar en lotes de 10k registros
        batch_size = 10000
        total_batches = len(df) // batch_size + (1 if len(df) % batch_size > 0 else 0)
        
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(df))
            batch_data = df.iloc[start_idx:end_idx].to_dict('records')
            
            result = self._make_request('POST', endpoint, {'rows': batch_data})
            if not result:
                logger.error(f"Error enviando lote {i+1}/{total_batches}")
                return False
            
            logger.info(f"Lote {i+1}/{total_batches} sincronizado exitosamente")
        
        logger.info(f"Sincronización completa: {len(df)} registros para {tenant_id}")
        return True
    
    def push_evaluation_results(self, tenant_id: str, evaluations: List[Dict]) -> bool:
        """Enviar resultados de evaluaciones IA a PowerBI"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return False
        
        dataset_name = self.config.datasets.get('ai_evaluations')
        if not dataset_name:
            logger.error("Dataset ai_evaluations no configurado")
            return False
        
        # Preparar datos con metadata
        processed_data = []
        for evaluation in evaluations:
            processed_data.append({
                'tenant_id': tenant_id,
                'evaluation_id': evaluation.get('evaluation_id'),
                'similarity_score': evaluation.get('similarity_score'),
                'risk_level': evaluation.get('risk_level'),
                'decision': evaluation.get('decision'),
                'timestamp': evaluation.get('timestamp'),
                'processing_time_ms': evaluation.get('processing_time_ms'),
                'bureau_score': evaluation.get('bureau_score'),
                'income': evaluation.get('profile', {}).get('income'),
                'age': evaluation.get('profile', {}).get('age'),
                'employment_type': evaluation.get('profile', {}).get('employment_type')
            })
        
        endpoint = f"/groups/{workspace_id}/datasets/{dataset_name}/tables/AIEvaluations/rows"
        
        result = self._make_request('POST', endpoint, {'rows': processed_data})
        
        if result:
            logger.info(f"Enviadas {len(processed_data)} evaluaciones a PowerBI")
            return True
        
        return False
    
    def refresh_dataset(self, dataset_type: str) -> bool:
        """Refrescar dataset específico"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return False
        
        dataset_name = self.config.datasets.get(dataset_type)
        if not dataset_name:
            logger.error(f"Dataset {dataset_type} no configurado")
            return False
        
        endpoint = f"/groups/{workspace_id}/datasets/{dataset_name}/refreshes"
        
        result = self._make_request('POST', endpoint, {
            'type': 'full',
            'commitMode': 'transactional'
        })
        
        if result:
            logger.info(f"Refresh iniciado para dataset {dataset_type}")
            return True
        
        return False
    
    def get_dataset_refresh_status(self, dataset_type: str) -> Optional[Dict]:
        """Obtener estado del refresh de dataset"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return None
        
        dataset_name = self.config.datasets.get(dataset_type)
        endpoint = f"/groups/{workspace_id}/datasets/{dataset_name}/refreshes"
        
        result = self._make_request('GET', endpoint)
        
        if result and 'value' in result:
            # Retornar el refresh más reciente
            refreshes = result['value']
            if refreshes:
                return refreshes[0]
        
        return None
    
    def create_webhook(self, webhook_url: str) -> bool:
        """Crear webhook para notificaciones PowerBI"""
        # Implementar webhook creation
        # Esta funcionalidad requiere PowerBI Premium
        pass
    
    def validate_connection(self) -> Dict[str, bool]:
        """Validar conexión completa con PowerBI"""
        validation_results = {
            'authentication': False,
            'workspace_access': False,
            'datasets_exist': False,
            'refresh_permissions': False
        }
        
        # Test autenticación
        validation_results['authentication'] = self.authenticate()
        
        if validation_results['authentication']:
            # Test acceso workspace
            workspace_id = self.get_workspace_id()
            validation_results['workspace_access'] = workspace_id is not None
            
            if validation_results['workspace_access']:
                # Test existencia datasets
                all_datasets_exist = True
                for dataset_type, dataset_name in self.config.datasets.items():
                    endpoint = f"/groups/{workspace_id}/datasets/{dataset_name}"
                    result = self._make_request('GET', endpoint)
                    if not result:
                        all_datasets_exist = False
                        break
                
                validation_results['datasets_exist'] = all_datasets_exist
                
                # Test permisos refresh
                if all_datasets_exist:
                    test_dataset = list(self.config.datasets.keys())[0]
                    refresh_status = self.get_dataset_refresh_status(test_dataset)
                    validation_results['refresh_permissions'] = refresh_status is not None
        
        return validation_results

# Factory para crear conectores por tenant
def create_powerbi_connector(tenant_config: Dict) -> Optional[PowerBIEnterpriseConnector]:
    """Factory para crear conector PowerBI según configuración tenant"""
    
    powerbi_config = tenant_config.get('powerbi_integration', {})
    
    if not powerbi_config.get('enabled', False):
        logger.info(f"PowerBI deshabilitado para tenant {tenant_config['tenant_id']}")
        return None
    
    config = PowerBIConfig(
        client_id=os.getenv('POWERBI_CLIENT_ID'),
        client_secret=os.getenv('POWERBI_CLIENT_SECRET'), 
        tenant_id=powerbi_config['tenant_id'],
        workspace_name=powerbi_config['workspace_name'],
        datasets=powerbi_config['datasets']
    )
    
    return PowerBIEnterpriseConnector(config)
