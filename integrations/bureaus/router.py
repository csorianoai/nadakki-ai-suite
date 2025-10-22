"""
Router Inteligente de Bureau - Lógica de Gating para Optimización de Costos
Solo consulta bureau cuando el score interno está en rango borderline (0.4-0.7)
Esto reduce las consultas en ~60% manteniendo precisión en casos críticos
"""
import logging
from typing import Dict, Any, Optional
from .datacredito_rd import ClienteDataCreditoRD
from .transunion_rd import ClienteTransUnionRD

# Configurar logger
logger = logging.getLogger(__name__)

class RouterBureauInteligente:
    """Router inteligente que optimiza consultas bureau con gating por costo"""
    
    def __init__(self, id_inquilino: str):
        self.id_inquilino = id_inquilino
        self.cliente_datacredito = ClienteDataCreditoRD(id_inquilino)
        self.cliente_transunion = ClienteTransUnionRD(id_inquilino)
        
        # Umbrales de gating - solo consultar bureau para scores borderline
        self.umbral_minimo = 0.4  # Por debajo: auto-rechazo, no necesita bureau
        self.umbral_maximo = 0.7  # Por encima: auto-aprobación, no necesita bureau
        
        # Métricas de costo
        self.consultas_evitadas = 0
        self.consultas_realizadas = 0
        
        logger.info(f"RouterBureauInteligente inicializado para inquilino {id_inquilino} con gating [{self.umbral_minimo}-{self.umbral_maximo}]")
    
    def debe_consultar_bureau(self, score_interno: float) -> Dict[str, Any]:
        """
        Lógica de gating: Solo consultar bureau para scores borderline
        Reduce consultas en ~60% mientras mantiene precisión en casos críticos
        """
        debe_consultar = self.umbral_minimo < score_interno < self.umbral_maximo
        
        if debe_consultar:
            logger.info(f"Consulta bureau aprobada - score borderline {score_interno}")
            return {
                'debe_consultar': True,
                'motivo': 'score_borderline',
                'score_interno': score_interno,
                'costo_estimado': 0.50
            }
        else:
            self.consultas_evitadas += 1
            motivo = "score_bajo_auto_rechazo" if score_interno <= self.umbral_minimo else "score_alto_auto_aprobacion"
            
            logger.info(f"Consulta bureau omitida - score {score_interno} ({motivo})")
            
            return {
                'debe_consultar': False,
                'motivo': motivo,
                'score_interno': score_interno,
                'ahorro_costo': 0.50,
                'total_consultas_evitadas': self.consultas_evitadas
            }
    
    async def obtener_datos_bureau(self, cedula: str, contexto_perfil: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtener datos bureau con lógica de fallback:
        1. Intentar DataCrédito RD (principal)
        2. Fallback a TransUnion RD si DataCrédito falla
        3. Retornar respuesta con tracking de costos
        """
        try:
            self.consultas_realizadas += 1
            
            # Principal: DataCrédito RD
            logger.info(f"Intentando consulta DataCrédito RD para inquilino {self.id_inquilino}")
            respuesta_datacredito = await self.cliente_datacredito.consultar_reporte_crediticio(
                cedula=cedula,
                contexto_perfil=contexto_perfil
            )
            
            if respuesta_datacredito.get('exito'):
                logger.info(f"Datos bureau obtenidos vía DataCrédito para inquilino {self.id_inquilino}")
                respuesta_datacredito['proveedor_usado'] = 'datacredito_rd'
                respuesta_datacredito['fallback_usado'] = False
                return respuesta_datacredito
                
            # Fallback: TransUnion RD
            logger.warning(f"DataCrédito falló para inquilino {self.id_inquilino}, intentando fallback TransUnion")
            respuesta_transunion = await self.cliente_transunion.consultar_reporte_crediticio(
                cedula=cedula,
                contexto_perfil=contexto_perfil
            )
            
            respuesta_transunion['proveedor_usado'] = 'transunion_rd'
            respuesta_transunion['fallback_usado'] = True
            
            return respuesta_transunion
            
        except Exception as e:
            logger.error(f"Error en router bureau para inquilino {self.id_inquilino}: {e}")
            return {
                'exito': False,
                'error': 'error_router',
                'mensaje': str(e),
                'costo_consulta': 0.0,
                'fallback_agotado': True
            }
    
    def obtener_metricas_eficiencia(self) -> Dict[str, Any]:
        """Obtener métricas de eficiencia del router para optimización de costos"""
        total_decisiones = self.consultas_realizadas + self.consultas_evitadas
        porcentaje_reduccion = (self.consultas_evitadas / max(total_decisiones, 1)) * 100
        
        return {
            'id_inquilino': self.id_inquilino,
            'consultas_realizadas': self.consultas_realizadas,
            'consultas_evitadas': self.consultas_evitadas,
            'porcentaje_reduccion': round(porcentaje_reduccion, 2),
            'ahorro_estimado_usd': round(self.consultas_evitadas * 0.50, 2)
        }
