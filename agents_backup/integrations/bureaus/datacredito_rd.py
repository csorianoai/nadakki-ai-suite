"""
Cliente DataCrédito RD - Integración Bureau República Dominicana
Maneja conexión con bureau crediticio dominicano con reintentos y manejo de errores
"""
import os
import httpx
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

class ClienteDataCreditoRD:
    """Cliente para integración con API de DataCrédito República Dominicana"""
    
    def __init__(self, id_inquilino: str):
        self.id_inquilino = id_inquilino
        self.clave_api = os.getenv('DATACREDITO_RD_KEY')
        self.url_base = os.getenv('DATACREDITO_RD_URL', 'https://api.datacredito.com.do/v2')
        self.timeout = 30.0
        
        if not self.clave_api:
            raise ValueError("Variable de entorno DATACREDITO_RD_KEY requerida")
            
        logger.info(f"Cliente DataCrédito RD inicializado para inquilino {id_inquilino}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def consultar_reporte_crediticio(self, cedula: str, contexto_perfil: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consultar reporte crediticio en DataCrédito RD
        
        Args:
            cedula: Cédula de identidad dominicana
            contexto_perfil: Contexto adicional del perfil para consultas mejoradas
            
        Returns:
            Datos del bureau crediticio o información de error
        """
        async with httpx.AsyncClient(timeout=self.timeout) as cliente:
            try:
                payload = {
                    'cedula': cedula,
                    'id_inquilino': self.id_inquilino,
                    'tipo_consulta': 'reporte_crediticio_basico',
                    'incluir_historial': contexto_perfil.get('incluir_historial', False),
                    'timestamp_solicitud': self._obtener_timestamp()
                }
                
                headers = {
                    'Authorization': f'Bearer {self.clave_api}',
                    'Content-Type': 'application/json',
                    'X-Tenant-ID': self.id_inquilino,
                    'User-Agent': 'Nadakki-AI-Suite/1.0'
                }
                
                logger.info(f"Consultando DataCrédito RD para inquilino {self.id_inquilino}")
                
                response = await cliente.post(
                    f"{self.url_base}/reportes",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    datos_bureau = response.json()
                    logger.info(f"Consulta bureau exitosa para inquilino {self.id_inquilino}")
                    
                    # Estructurar respuesta para uso interno
                    return {
                        'exito': True,
                        'fuente': 'datacredito_rd',
                        'score_crediticio': datos_bureau.get('score_crediticio'),
                        'historial_pagos': datos_bureau.get('historial_pagos', []),
                        'cuentas_abiertas': datos_bureau.get('cuentas_abiertas', []),
                        'consultas_recientes': datos_bureau.get('consultas', []),
                        'alertas': datos_bureau.get('alertas', []),
                        'costo_consulta': 0.50,  # Peso dominicano
                        'timestamp_consulta': self._obtener_timestamp(),
                        'id_transaccion': datos_bureau.get('id_transaccion')
                    }
                    
                elif response.status_code == 404:
                    logger.warning(f"No se encontró registro bureau para cédula en inquilino {self.id_inquilino}")
                    return {
                        'exito': False,
                        'error': 'no_encontrado',
                        'mensaje': 'No se encontró historial crediticio',
                        'costo_consulta': 0.50,
                        'timestamp_consulta': self._obtener_timestamp()
                    }
                    
                else:
                    response.raise_for_status()
                    
            except Exception as e:
                logger.error(f"Error bureau para inquilino {self.id_inquilino}: {e}")
                return {
                    'exito': False,
                    'error': 'error_inesperado',
                    'mensaje': str(e),
                    'costo_consulta': 0.0
                }
    
    def _obtener_timestamp(self) -> str:
        """Generar timestamp ISO para auditoría"""
        return datetime.utcnow().isoformat() + 'Z'
