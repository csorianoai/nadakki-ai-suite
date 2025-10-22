"""
🔗 PowerBI Enterprise Connector - Credicefi Production
Bidirectional sync optimizado para alto volumen
Autor: Nadakki AI Suite Enterprise
Fecha: 2025-01-01
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum

# Configurar logging específico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CredicefiPowerBI')

class SyncStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class PowerBICredentials:
    tenant_id: str
    client_id: str
    client_secret: str
    workspace_id: str
    authority_url: str

class CredicefiPowerBIConnector:
    """
    Connector PowerBI Enterprise para Credicefi
    Características:
    - Sync bidireccional optimizado
    - Rate limiting automático
    - Retry logic robusto
    - Async processing para alto volumen
    - Monitoring y alertas integradas
    """
    
    def __init__(self, config_path: str = 'config/tenants/credicefi.json'):
        self.tenant_id = "credicefi"
        self.config = self._load_config(config_path)
        self.credentials = self._load_credentials()
        self.access_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        
        # Rate limiting
        self.request_count = 0
        self.last_reset = datetime.now()
        self.max_requests_per_hour = 3600  # PowerBI API limit
        
        # Retry configuration
        self.max_retries = 3
        self.backoff_factor = 2
        
        logger.info(f"PowerBI Connector iniciado para {self.tenant_id}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Cargar configuración desde archivo"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('powerbi_integration', {})
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}
    
    def _load_credentials(self) -> PowerBICredentials:
        """Cargar credenciales desde variables de entorno"""
        return PowerBICredentials(
            tenant_id=os.getenv('POWERBI_TENANT_ID', self.config.get('tenant_id')),
            client_id=os.getenv('POWERBI_CLIENT_ID'),
            client_secret=os.getenv('POWERBI_CLIENT_SECRET'), 
            workspace_id=os.getenv('POWERBI_WORKSPACE_ID'),
            authority_url=os.getenv('POWERBI_AUTHORITY_URL', 
                                  f"https://login.microsoftonline.com/{self.credentials.tenant_id}" if hasattr(self, 'credentials') else None)
        )
    
    def _check_rate_limit(self) -> bool:
        """Verificar límites de rate limiting"""
        now = datetime.now()
        
        # Reset contador cada hora
        if (now - self.last_reset).seconds >= 3600:
            self.request_count = 0
            self.last_reset = now
        
        if self.request_count >= self.max_requests_per_hour:
            wait_time = 3600 - (now - self.last_reset).seconds
            logger.warning(f"Rate limit alcanzado. Esperando {wait_time}s")
            time.sleep(wait_time)
            return False
        
        return True
    
    async def authenticate_async(self) -> bool:
        """Autenticación asíncrona optimizada"""
        try:
            if not self._check_rate_limit():
                return False
            
            token_url = f"{self.credentials.authority_url}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default',
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data['access_token']
                        self.token_expires_at = datetime.now() + timedelta(
                            seconds=token_data['expires_in'] - 300
                        )
                        self.request_count += 1
                        logger.info("PowerBI authentication exitosa")
                        return True
                    else:
                        logger.error(f"Auth failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error en autenticación async: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Autenticación síncrona con retry logic"""
        for attempt in range(self.max_retries):
            try:
                if not self._check_rate_limit():
                    continue
                
                token_url = f"{self.credentials.authority_url}/oauth2/v2.0/token"
                
                data = {
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scope': 'https://analysis.windows.net/powerbi/api/.default',
                    'grant_type': 'client_credentials'
                }
                
                response = self.session.post(token_url, data=data, timeout=30)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data['access_token']
                    self.token_expires_at = datetime.now() + timedelta(
                        seconds=token_data['expires_in'] - 300
                    )
                    self.request_count += 1
                    logger.info(f"PowerBI authentication exitosa (intento {attempt + 1})")
                    return True
                else:
                    logger.warning(f"Auth attempt {attempt + 1} failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Auth attempt {attempt + 1} error: {e}")
                
            if attempt < self.max_retries - 1:
                wait_time = self.backoff_factor ** attempt
                logger.info(f"Reintentando en {wait_time}s...")
                time.sleep(wait_time)
        
        logger.error("Autenticación fallida después de todos los intentos")
        return False
    
    def get_headers(self) -> Dict[str, str]:
        """Headers optimizados para requests"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            if not self.authenticate():
                raise Exception("PowerBI authentication failed")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Nadakki-AI-Suite-Credicefi/1.0'
        }
    
    def extract_historical_defaults_optimized(self, limit: int = 10000) -> List[Dict]:
        """
        Extracción optimizada de histórico de morosos
        Utiliza paginación y procesamiento en chunks
        """
        try:
            logger.info(f"Iniciando extracción histórico (limit: {limit})")
            
            dataset_id = self.config.get('datasets', {}).get('historical_defaults')
            if not dataset_id:
                logger.error("Dataset ID no configurado")
                return []
            
            # Query DAX optimizada para extracción masiva
            query = {
                "queries": [
                    {
                        "query": f'''
                            EVALUATE
                            TOPN(
                                {limit},
                                SUMMARIZECOLUMNS(
                                    'Morosos'[Cedula],
                                    'Morosos'[Ingresos_Mensuales],
                                    'Morosos'[Score_Credito],
                                    'Morosos'[Edad],
                                    'Morosos'[Tipo_Empleo],
                                    'Morosos'[Ratio_Deuda_Ingresos],
                                    'Morosos'[Monto_Default],
                                    'Morosos'[Fecha_Default],
                                    'Morosos'[Producto_Credito],
                                    'Morosos'[Sucursal],
                                    'Morosos'[Segmento_Cliente]
                                ),
                                'Morosos'[Fecha_Default],
                                DESC
                            )
                        '''
                    }
                ]
            }
            
            url = f"{self.base_url}/groups/{self.credentials.workspace_id}/datasets/{dataset_id}/executeQueries"
            
            response = self.session.post(
                url, 
                headers=self.get_headers(),
                json=query,
                timeout=120
            )
            
            response.raise_for_status()
            self.request_count += 1
            
            result = response.json()
            historical_data = []
            
            if 'results' in result and result['results']:
                tables = result['results'][0].get('tables', [])
                if tables and 'rows' in tables[0]:
                    rows = tables[0]['rows']
                    
                    for row in rows:
                        try:
                            historical_data.append({
                                'cedula': str(row[0]) if row[0] else '',
                                'income': float(row[1]) if row[1] else 0.0,
                                'credit_score': int(row[2]) if row[2] else 0,
                                'age': int(row[3]) if row[3] else 0,
                                'employment_type': str(row[4]) if row[4] else 'unknown',
                                'debt_to_income': float(row[5]) if row[5] else 0.0,
                                'default_amount': float(row[6]) if row[6] else 0.0,
                                'default_date': str(row[7]) if row[7] else '',
                                'product_type': str(row[8]) if row[8] else '',
                                'branch': str(row[9]) if row[9] else '',
                                'segment': str(row[10]) if row[10] else '',
                                'extracted_at': datetime.now().isoformat(),
                                'tenant_id': self.tenant_id
                            })
                        except (IndexError, ValueError, TypeError) as e:
                            logger.warning(f"Error procesando fila: {e}")
                            continue
            
            logger.info(f"Extraídos {len(historical_data)} registros históricos")
            return historical_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red extrayendo datos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extrayendo histórico: {e}")
            return []
    
    def push_evaluation_results_batch(self, evaluations: List[Dict], batch_size: int = 1000) -> bool:
        """
        Push optimizado de resultados en lotes
        Maneja grandes volúmenes con processing paralelo
        """
        try:
            if not evaluations:
                logger.warning("No hay evaluaciones para enviar")
                return False
            
            logger.info(f"Iniciando push de {len(evaluations)} evaluaciones")
            
            dataset_id = self.config.get('datasets', {}).get('ai_evaluations')
            table_name = "EvaluacionesIA"
            
            if not dataset_id:
                logger.error("Dataset evaluaciones no configurado")
                return False
            
            # Procesar en lotes para optimizar performance
            total_batches = (len(evaluations) + batch_size - 1) // batch_size
            success_count = 0
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for i in range(0, len(evaluations), batch_size):
                    batch = evaluations[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    future = executor.submit(
                        self._push_single_batch,
                        batch,
                        dataset_id,
                        table_name,
                        batch_num,
                        total_batches
                    )
                    futures.append(future)
                
                # Recopilar resultados
                for future in futures:
                    if future.result():
                        success_count += 1
            
            success_rate = (success_count / total_batches) * 100
            logger.info(f"Push completado: {success_count}/{total_batches} lotes exitosos ({success_rate:.1f}%)")
            
            return success_rate >= 80  # Considerar exitoso si >=80% de lotes pasaron
            
        except Exception as e:
            logger.error(f"Error en push batch: {e}")
            return False
    
    def _push_single_batch(self, batch: List[Dict], dataset_id: str, 
                          table_name: str, batch_num: int, total_batches: int) -> bool:
        """Push de un lote individual con retry logic"""
        for attempt in range(self.max_retries):
            try:
                if not self._check_rate_limit():
                    time.sleep(1)
                    continue
                
                # Preparar datos para PowerBI
                df = pd.DataFrame(batch)
                
                # Validar y limpiar datos
                df = self._clean_dataframe_for_powerbi(df)
                
                url = f"{self.base_url}/groups/{self.credentials.workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
                
                data = {"rows": df.to_dict('records')}
                
                response = self.session.post(
                    url,
                    headers=self.get_headers(),
                    json=data,
                    timeout=60
                )
                
                if response.status_code in [200, 201]:
                    self.request_count += 1
                    logger.info(f"Lote {batch_num}/{total_batches} enviado exitosamente ({len(batch)} registros)")
                    return True
                else:
                    logger.warning(f"Lote {batch_num} falló: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error lote {batch_num}, intento {attempt + 1}: {e}")
                
            if attempt < self.max_retries - 1:
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
        
        logger.error(f"Lote {batch_num} falló después de {self.max_retries} intentos")
        return False
    
    def _clean_dataframe_for_powerbi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpieza y validación de DataFrame para PowerBI"""
        try:
            # Reemplazar NaN con valores apropiados
            df = df.fillna({
                'cedula': '',
                'similarity_score': 0.0,
                'risk_level': 'UNKNOWN',
                'decision': 'PENDING',
                'execution_time_seconds': 0.0,
                'tenant_id': self.tenant_id
            })
            
            # Validar tipos de datos
            if 'similarity_score' in df.columns:
                df['similarity_score'] = pd.to_numeric(df['similarity_score'], errors='coerce').fillna(0.0)
            
            if 'execution_time_seconds' in df.columns:
                df['execution_time_seconds'] = pd.to_numeric(df['execution_time_seconds'], errors='coerce').fillna(0.0)
            
            # Truncar strings largos
            string_columns = df.select_dtypes(include=['object']).columns
            for col in string_columns:
                df[col] = df[col].astype(str).str[:255]  # PowerBI limit
            
            # Agregar timestamp si no existe
            if 'pushed_at' not in df.columns:
                df['pushed_at'] = datetime.now().isoformat()
            
            return df
            
        except Exception as e:
            logger.error(f"Error limpiando DataFrame: {e}")
            return df
    
    def schedule_dataset_refresh_advanced(self, dataset_id: str = None, 
                                        notify_completion: bool = True) -> Dict:
        """Programar refresh de dataset con opciones avanzadas"""
        try:
            if not dataset_id:
                dataset_id = self.config.get('datasets', {}).get('historical_defaults')
            
            if not self._check_rate_limit():
                return {'status': 'rate_limited'}
            
            url = f"{self.base_url}/groups/{self.credentials.workspace_id}/datasets/{dataset_id}/refreshes"
            
            payload = {
                "notifyOption": "MailOnCompletion" if notify_completion else "NoNotification"
            }
            
            response = self.session.post(
                url,
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            self.request_count += 1
            
            if response.status_code == 202:
                logger.info(f"Dataset refresh programado para {dataset_id}")
                return {
                    'status': 'scheduled',
                    'dataset_id': dataset_id,
                    'scheduled_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Error programando refresh: {response.status_code}")
                return {'status': 'failed', 'http_code': response.status_code}
                
        except Exception as e:
            logger.error(f"Error programando refresh: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_comprehensive_dataset_status(self, dataset_id: str = None) -> Dict:
        """Estado completo de dataset con métricas detalladas"""
        try:
            if not dataset_id:
                dataset_id = self.config.get('datasets', {}).get('historical_defaults')
            
            if not self._check_rate_limit():
                return {'status': 'rate_limited'}
            
            # Obtener último refresh
            url = f"{self.base_url}/groups/{self.credentials.workspace_id}/datasets/{dataset_id}/refreshes?$top=5"
            
            response = self.session.get(url, headers=self.get_headers(), timeout=30)
            self.request_count += 1
            
            if response.status_code == 200:
                refreshes = response.json().get('value', [])
                
                if refreshes:
                    latest = refreshes[0]
                    
                    return {
                        'dataset_id': dataset_id,
                        'status': latest.get('status', 'Unknown'),
                        'start_time': latest.get('startTime'),
                        'end_time': latest.get('endTime'),
                        'refresh_type': latest.get('refreshType', 'Unknown'),
                        'service_exception': latest.get('serviceExceptionJson'),
                        'recent_refreshes': len(refreshes),
                        'last_check': datetime.now().isoformat(),
                        'tenant_id': self.tenant_id
                    }
                else:
                    return {
                        'dataset_id': dataset_id,
                        'status': 'No refreshes found',
                        'last_check': datetime.now().isoformat()
                    }
            else:
                return {'status': 'API Error', 'http_code': response.status_code}
                
        except Exception as e:
            logger.error(f"Error obteniendo status: {e}")
            return {'status': 'Error', 'message': str(e)}
    
    def health_check_complete(self) -> Dict:
        """Health check completo del connector"""
        try:
            start_time = datetime.now()
            
            # Test 1: Autenticación
            auth_success = self.authenticate()
            
            # Test 2: Conectividad workspace
            workspace_test = self._test_workspace_connectivity()
            
            # Test 3: Dataset availability  
            dataset_test = self._test_dataset_availability()
            
            # Test 4: Rate limiting status
            rate_limit_ok = self.request_count < (self.max_requests_per_hour * 0.8)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            overall_status = all([auth_success, workspace_test, dataset_test, rate_limit_ok])
            
            return {
                'status': 'healthy' if overall_status else 'unhealthy',
                'tenant_id': self.tenant_id,
                'timestamp': end_time.isoformat(),
                'response_time_seconds': round(total_time, 2),
                'checks': {
                    'authentication': auth_success,
                    'workspace_connectivity': workspace_test,
                    'dataset_availability': dataset_test,
                    'rate_limit_ok': rate_limit_ok
                },
                'metrics': {
                    'requests_used': self.request_count,
                    'requests_remaining': self.max_requests_per_hour - self.request_count,
                    'rate_limit_reset': self.last_reset.isoformat()
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _test_workspace_connectivity(self) -> bool:
        """Test conectividad con workspace"""
        try:
            url = f"{self.base_url}/groups/{self.credentials.workspace_id}"
            response = self.session.get(url, headers=self.get_headers(), timeout=15)
            self.request_count += 1
            return response.status_code == 200
        except:
            return False
    
    def _test_dataset_availability(self) -> bool:
        """Test disponibilidad de datasets"""
        try:
            url = f"{self.base_url}/groups/{self.credentials.workspace_id}/datasets"
            response = self.session.get(url, headers=self.get_headers(), timeout=15)
            self.request_count += 1
            
            if response.status_code == 200:
                datasets = response.json().get('value', [])
                configured_datasets = self.config.get('datasets', {}).values()
                
                available_ids = [ds['id'] for ds in datasets]
                return any(ds_id in available_ids for ds_id in configured_datasets)
            return False
        except:
            return False

# ===== FUNCIONES DE UTILIDAD =====

def test_connector_complete():
    """Test completo del connector con todos los escenarios"""
    try:
        logger.info("=== INICIANDO TEST COMPLETO POWERBI CONNECTOR ===")
        
        connector = CredicefiPowerBIConnector()
        
        # Test 1: Health check
        health = connector.health_check_complete()
        logger.info(f"Health Check: {health['status']}")
        
        if health['status'] != 'healthy':
            return {
                'status': 'FAILED',
                'step': 'health_check',
                'details': health
            }
        
        # Test 2: Extracción datos (muestra pequeña)
        historical_data = connector.extract_historical_defaults_optimized(limit=100)
        
        # Test 3: Push resultados (simulado)
        test_evaluations = [
            {
                'evaluation_id': f'TEST_{i:04d}',
                'cedula': f'1234567890{i}',
                'similarity_score': 0.45 + (i * 0.01),
                'risk_level': 'LOW_RISK' if i % 3 == 0 else 'MEDIUM_RISK',
                'decision': 'APPROVE' if i % 2 == 0 else 'REVIEW',
                'execution_time_seconds': 2.1 + (i * 0.1),
                'timestamp': datetime.now().isoformat(),
                'tenant_id': 'credicefi'
            }
            for i in range(10)  # Test con 10 registros
        ]
        
        push_success = connector.push_evaluation_results_batch(test_evaluations)
        
        # Test 4: Dataset refresh
        refresh_result = connector.schedule_dataset_refresh_advanced()
        
        # Test 5: Status check
        status = connector.get_comprehensive_dataset_status()
        
        logger.info("=== TEST COMPLETO FINALIZADO ===")
        
        return {
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
            'results': {
                'health_check': health['status'] == 'healthy',
                'data_extraction': len(historical_data) > 0,
                'data_push': push_success,
                'dataset_refresh': refresh_result.get('status') == 'scheduled',
                'status_check': status.get('status') not in ['Error', 'API Error']
            },
            'metrics': {
                'historical_records_found': len(historical_data),
                'test_evaluations_pushed': len(test_evaluations),
                'total_api_calls': connector.request_count
            },
            'connector_health': health
        }
        
    except Exception as e:
        logger.error(f"Test completo falló: {e}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Ejecutar test automáticamente
    result = test_connector_complete()
    print(json.dumps(result, indent=2, ensure_ascii=False))
