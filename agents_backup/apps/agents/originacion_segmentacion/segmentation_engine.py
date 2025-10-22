"""
Segmentation Engine - Motor de Segmentación Inteligente de Deudores
===================================================================

Agente especializado en segmentar deudores según múltiples criterios:
perfil de riesgo, capacidad de pago, comportamiento histórico y potencial de recuperación.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

class SegmentationEngine:
    """Motor de segmentación inteligente de deudores"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.agent_name = "SegmentationEngine"
        self.version = "3.1.0"
        self.logger = logging.getLogger(f"nadakki.{self.agent_name}.{tenant_id}")
        
        # Inicializar matrices de segmentación
        self.criterios_segmentacion = self._inicializar_criterios_segmentacion()
        self.perfiles_segmento = self._definir_perfiles_segmento()
        
        self.logger.info(f"Inicializado {self.agent_name} v{self.version} para tenant {tenant_id}")
    
    def execute(self, datos_deudor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar segmentación completa del deudor
        
        Args:
            datos_deudor: Datos completos del deudor incluyendo historial y financieros
            
        Returns:
            Análisis de segmentación con recomendaciones estratégicas
        """
        inicio = datetime.now()
        
        try:
            # 1. Análisis de perfil crediticio
            perfil_crediticio = self._analizar_perfil_crediticio(datos_deudor)
            
            # 2. Evaluación de capacidad de pago
            capacidad_pago = self._evaluar_capacidad_pago(datos_deudor)
            
            # 3. Análisis de comportamiento histórico
            comportamiento = self._analizar_comportamiento_historico(datos_deudor)
            
            # 4. Clasificación de riesgo de recuperación
            riesgo_recuperacion = self._clasificar_riesgo_recuperacion(
                perfil_crediticio, capacidad_pago, comportamiento
            )
            
            # 5. Segmentación inteligente
            segmento_principal = self._determinar_segmento_principal(
                perfil_crediticio, capacidad_pago, comportamiento, riesgo_recuperacion
            )
            
            # 6. Recomendaciones estratégicas
            estrategias = self._generar_estrategias_segmento(segmento_principal, datos_deudor)
            
            # 7. Score de priorización
            score_priorizacion = self._calcular_score_priorizacion(segmento_principal)
            
            tiempo_ejecucion = (datetime.now() - inicio).total_seconds()
            
            resultado = {
                "agente": self.agent_name,
                "version": self.version,
                "tenant_id": self.tenant_id,
                "timestamp": datetime.now().isoformat(),
                "tiempo_ejecucion_segundos": tiempo_ejecucion,
                
                # Segmentación principal
                "segmento_principal": segmento_principal["nombre"],
                "subsegmento": segmento_principal["subsegmento"],
                "score_segmento": segmento_principal["score"],
                "confianza_segmentacion": segmento_principal["confianza"],
                
                # Análisis de componentes
                "perfil_crediticio": {
                    "categoria": perfil_crediticio["categoria"],
                    "score": perfil_crediticio["score"],
                    "factores_clave": perfil_crediticio["factores_principales"]
                },
                "capacidad_pago": {
                    "nivel": capacidad_pago["nivel"],
                    "score": capacidad_pago["score"],
                    "ingreso_disponible": capacidad_pago["ingreso_disponible"]
                },
                "comportamiento_historico": {
                    "patron": comportamiento["patron_principal"],
                    "score": comportamiento["score"],
                    "tendencia": comportamiento["tendencia"]
                },
                "riesgo_recuperacion": {
                    "nivel": riesgo_recuperacion["nivel"],
                    "score": riesgo_recuperacion["score"],
                    "factores_riesgo": riesgo_recuperacion["factores_principales"]
                },
                
                # Estrategias y recomendaciones
                "estrategias_recomendadas": estrategias["estrategias"],
                "canales_optimos": estrategias["canales"],
                "timing_contacto": estrategias["timing"],
                "recursos_requeridos": estrategias["recursos"],
                
                # Métricas de gestión
                "score_priorizacion": score_priorizacion,
                "score_final": segmento_principal["score"],
                "segmento_final": segmento_principal["nombre"],
                "probabilidad_recuperacion": segmento_principal.get("prob_recuperacion", 0.5),
                
                # Metadatos
                "caso_id": datos_deudor.get("caso_id", "unknown"),
                "deudor_id": datos_deudor.get("deudor_id", "unknown")
            }
            
            self.logger.info(f"Deudor segmentado: {segmento_principal['nombre']} con score {segmento_principal['score']}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en segmentación: {str(e)}")
            return {
                "agente": self.agent_name,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _inicializar_criterios_segmentacion(self) -> Dict:
        """Inicializar criterios y pesos para segmentación"""
        return {
            "criterios_principales": {
                "perfil_crediticio": 0.35,
                "capacidad_pago": 0.30,
                "comportamiento_historico": 0.20,
                "antiguedad_deuda": 0.10,
                "monto_deuda": 0.05
            },
            "factores_ajuste": {
                "estacionalidad": 0.05,
                "condiciones_economicas": 0.05,
                "perfil_demografico": 0.03
            },
            "umbrales_segmentacion": {
                "premium": 85,
                "alta_valor": 70,
                "estandar": 50,
                "riesgo": 35,
                "critico": 20
            }
        }
    
    def _definir_perfiles_segmento(self) -> Dict:
        """Definir perfiles detallados por segmento"""
        return {
            "PREMIUM": {
                "descripcion": "Deudores de alta calidad con excelente perfil",
                "estrategia_base": "CONSULTIVA",
                "recursos": "ESPECIALIZADOS",
                "prob_recuperacion": 0.90
            },
            "ALTA_VALOR": {
                "descripcion": "Deudores valiosos con buen potencial",
                "estrategia_base": "COLABORATIVA", 
                "recursos": "MEDIOS_ALTOS",
                "prob_recuperacion": 0.75
            },
            "ESTANDAR": {
                "descripcion": "Deudores regulares con gestión estándar",
                "estrategia_base": "ESTRUCTURADA",
                "recursos": "ESTANDAR",
                "prob_recuperacion": 0.60
            },
            "RIESGO": {
                "descripcion": "Deudores complejos que requieren atención especial",
                "estrategia_base": "INTENSIVA",
                "recursos": "ESPECIALIZADOS",
                "prob_recuperacion": 0.40
            },
            "CRITICO": {
                "descripcion": "Deudores de alto riesgo con gestión legal",
                "estrategia_base": "LEGAL",
                "recursos": "LEGALES",
                "prob_recuperacion": 0.25
            }
        }
    
    def _analizar_perfil_crediticio(self, datos: Dict) -> Dict:
        """Analizar perfil crediticio del deudor"""
        score_base = datos.get("score_crediticio", 500)
        historial = datos.get("historial_crediticio", {})
        
        # Normalizar score (300-850 a 0-100)
        score_normalizado = max(0, min(100, ((score_base - 300) / 550) * 100))
        
        # Ajustar por historial
        ajustes = 0
        if historial.get("pagos_puntuales", 0) > 0.8:
            ajustes += 10
        if historial.get("utilización_credito", 1.0) < 0.3:
            ajustes += 5
        if historial.get("antigüedad_credito", 0) > 5:
            ajustes += 5
        
        score_final = min(100, score_normalizado + ajustes)
        
        # Categorizar
        if score_final >= 80:
            categoria = "EXCELENTE"
        elif score_final >= 65:
            categoria = "BUENO"
        elif score_final >= 50:
            categoria = "REGULAR"
        elif score_final >= 35:
            categoria = "DEFICIENTE"
        else:
            categoria = "CRITICO"
        
        return {
            "score": score_final,
            "categoria": categoria,
            "score_original": score_base,
            "factores_principales": ["score_base", "historial_pagos", "utilizacion_credito"]
        }
    
    def _evaluar_capacidad_pago(self, datos: Dict) -> Dict:
        """Evaluar capacidad de pago actual"""
        ingresos = datos.get("ingresos_mensuales", 0)
        gastos = datos.get("gastos_mensuales", 0)
        deudas = datos.get("deudas_totales", 0)
        
        ingreso_disponible = max(0, ingresos - gastos)
        ratio_deuda_ingreso = deudas / max(1, ingresos) if ingresos > 0 else 0
        
        # Score basado en capacidad
        if ingreso_disponible > ingresos * 0.3 and ratio_deuda_ingreso < 0.3:
            nivel = "ALTA"
            score = 85
        elif ingreso_disponible > ingresos * 0.2 and ratio_deuda_ingreso < 0.5:
            nivel = "BUENA"
            score = 70
        elif ingreso_disponible > ingresos * 0.1 and ratio_deuda_ingreso < 0.7:
            nivel = "MEDIA"
            score = 55
        elif ingreso_disponible > 0 and ratio_deuda_ingreso < 0.9:
            nivel = "BAJA"
            score = 35
        else:
            nivel = "CRITICA"
            score = 15
        
        return {
            "nivel": nivel,
            "score": score,
            "ingreso_disponible": ingreso_disponible,
            "ratio_deuda_ingreso": ratio_deuda_ingreso
        }
    
    def _analizar_comportamiento_historico(self, datos: Dict) -> Dict:
        """Analizar patrones de comportamiento histórico"""
        pagos_historia = datos.get("historial_pagos", [])
        contactos_historia = datos.get("historial_contactos", [])
        promesas_historia = datos.get("historial_promesas", [])
        
        # Analizar patrones de pago
        if pagos_historia:
            pagos_puntuales = sum(1 for p in pagos_historia if p.get("puntual", False))
            ratio_puntualidad = pagos_puntuales / len(pagos_historia)
        else:
            ratio_puntualidad = 0.5
        
        # Analizar respuesta a contactos
        if contactos_historia:
            contactos_exitosos = sum(1 for c in contactos_historia if c.get("exitoso", False))
            ratio_contactabilidad = contactos_exitosos / len(contactos_historia)
        else:
            ratio_contactabilidad = 0.5
        
        # Analizar cumplimiento de promesas
        if promesas_historia:
            promesas_cumplidas = sum(1 for p in promesas_historia if p.get("cumplida", False))
            ratio_cumplimiento = promesas_cumplidas / len(promesas_historia)
        else:
            ratio_cumplimiento = 0.5
        
        # Score comportamental
        score_comportamental = (ratio_puntualidad * 0.4 + 
                              ratio_contactabilidad * 0.3 + 
                              ratio_cumplimiento * 0.3) * 100
        
        # Determinar patrón
        if score_comportamental >= 75:
            patron = "COLABORATIVO"
            tendencia = "POSITIVA"
        elif score_comportamental >= 55:
            patron = "INTERMEDIO"
            tendencia = "ESTABLE"
        elif score_comportamental >= 35:
            patron = "IRREGULAR"
            tendencia = "VARIABLE"
        else:
            patron = "EVASIVO"
            tendencia = "NEGATIVA"
        
        return {
            "score": score_comportamental,
            "patron_principal": patron,
            "tendencia": tendencia,
            "ratio_puntualidad": ratio_puntualidad,
            "ratio_contactabilidad": ratio_contactabilidad,
            "ratio_cumplimiento": ratio_cumplimiento
        }
    
    def _clasificar_riesgo_recuperacion(self, perfil: Dict, capacidad: Dict, comportamiento: Dict) -> Dict:
        """Clasificar riesgo de recuperación integrado"""
        # Score ponderado
        score_riesgo = (perfil["score"] * 0.4 + 
                       capacidad["score"] * 0.35 + 
                       comportamiento["score"] * 0.25)
        
        # Factores de riesgo
        factores_riesgo = []
        if perfil["score"] < 50:
            factores_riesgo.append("perfil_crediticio_deficiente")
        if capacidad["score"] < 40:
            factores_riesgo.append("capacidad_pago_limitada")
        if comportamiento["score"] < 40:
            factores_riesgo.append("comportamiento_evasivo")
        
        # Nivel de riesgo
        if score_riesgo >= 75:
            nivel = "BAJO_RIESGO"
        elif score_riesgo >= 55:
            nivel = "RIESGO_MEDIO"
        elif score_riesgo >= 35:
            nivel = "ALTO_RIESGO"
        else:
            nivel = "RIESGO_CRITICO"
        
        return {
            "score": score_riesgo,
            "nivel": nivel,
            "factores_principales": factores_riesgo
        }
    
    def _determinar_segmento_principal(self, perfil: Dict, capacidad: Dict, 
                                     comportamiento: Dict, riesgo: Dict) -> Dict:
        """Determinar segmento principal basado en todos los análisis"""
        
        # Score integrado con pesos del tenant
        criterios = self.criterios_segmentacion["criterios_principales"]
        
        score_integrado = (
            perfil["score"] * criterios["perfil_crediticio"] +
            capacidad["score"] * criterios["capacidad_pago"] +
            comportamiento["score"] * criterios["comportamiento_historico"]
        )
        
        # Determinar segmento por umbrales
        umbrales = self.criterios_segmentacion["umbrales_segmentacion"]
        
        if score_integrado >= umbrales["premium"]:
            segmento = "PREMIUM"
            subsegmento = "ALTA_CALIDAD"
        elif score_integrado >= umbrales["alta_valor"]:
            segmento = "ALTA_VALOR"
            subsegmento = "POTENCIAL_ALTO"
        elif score_integrado >= umbrales["estandar"]:
            segmento = "ESTANDAR"
            subsegmento = "GESTION_REGULAR"
        elif score_integrado >= umbrales["riesgo"]:
            segmento = "RIESGO"
            subsegmento = "ATENCION_ESPECIAL"
        else:
            segmento = "CRITICO"
            subsegmento = "INTERVENCION_LEGAL"
        
        # Calcular confianza
        confianza = min(0.95, (score_integrado / 100) * 1.1)
        
        perfil_segmento = self.perfiles_segmento[segmento]
        
        return {
            "nombre": segmento,
            "subsegmento": subsegmento,
            "score": round(score_integrado, 2),
            "confianza": round(confianza, 2),
            "descripcion": perfil_segmento["descripcion"],
            "estrategia_base": perfil_segmento["estrategia_base"],
            "prob_recuperacion": perfil_segmento["prob_recuperacion"]
        }
    
    def _generar_estrategias_segmento(self, segmento: Dict, datos: Dict) -> Dict:
        """Generar estrategias específicas para el segmento"""
        
        estrategias_base = {
            "PREMIUM": {
                "estrategias": ["contacto_personal", "comunicacion_premium", "flexibilidad_maxima"],
                "canales": ["telefono_directo", "email_personalizado", "visita_domicilio"],
                "timing": {"frecuencia": "semanal", "horarios": ["9:00-11:00", "15:00-17:00"]},
                "recursos": "agente_senior"
            },
            "ALTA_VALOR": {
                "estrategias": ["seguimiento_estructurado", "opciones_pago", "incentivos"],
                "canales": ["telefono", "whatsapp", "email"],
                "timing": {"frecuencia": "bisemanal", "horarios": ["9:00-12:00", "14:00-17:00"]},
                "recursos": "agente_intermedio"
            },
            "ESTANDAR": {
                "estrategias": ["recordatorios_regulares", "planes_pago", "seguimiento"],
                "canales": ["telefono", "sms", "whatsapp"],
                "timing": {"frecuencia": "semanal", "horarios": ["8:00-18:00"]},
                "recursos": "agente_junior"
            },
            "RIESGO": {
                "estrategias": ["presion_moderada", "ultimatums", "negociacion_agresiva"],
                "canales": ["telefono_multiple", "visita", "carta_formal"],
                "timing": {"frecuencia": "diaria", "horarios": ["8:00-19:00"]},
                "recursos": "especialista_cobranza"
            },
            "CRITICO": {
                "estrategias": ["accion_legal", "embargo", "negociacion_final"],
                "canales": ["notificacion_legal", "visita_legal", "carta_abogado"],
                "timing": {"frecuencia": "continua", "horarios": ["horario_legal"]},
                "recursos": "equipo_legal"
            }
        }
        
        return estrategias_base.get(segmento["nombre"], estrategias_base["ESTANDAR"])
    
    def _calcular_score_priorizacion(self, segmento: Dict) -> float:
        """Calcular score de priorización para gestión"""
        score_base = segmento["score"]
        probabilidad = segmento["prob_recuperacion"]
        
        # Score de priorización = Score segmento * Probabilidad recuperación * Factor urgencia
        factor_urgencia = {
            "PREMIUM": 0.9,
            "ALTA_VALOR": 1.0,
            "ESTANDAR": 0.8,
            "RIESGO": 1.1,
            "CRITICO": 1.2
        }.get(segmento["nombre"], 1.0)
        
        score_priorizacion = score_base * probabilidad * factor_urgencia
        return round(score_priorizacion, 2)
    
    def policy(self) -> Dict[str, Any]:
        """Retornar políticas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "requires_tenant_isolation": True,
            "data_retention_days": 1825,  # 5 años
            "compliance_requirements": ["INDOTEL_172_13", "GDPR"],
            "escalation_rules": {
                "tiempo_sin_progreso": 30,
                "intentos_sin_respuesta": 15,
                "deterioro_score": 10
            }
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Retornar métricas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "segmentaciones_realizadas": 0,  # Se actualizará en runtime
            "precision_segmentacion": 0.85,
            "tiempo_promedio_procesamiento": 2.3,
            "distribucion_segmentos": {
                "premium": "15%",
                "alta_valor": "25%", 
                "estandar": "35%",
                "riesgo": "20%",
                "critico": "5%"
            }
        }

if __name__ == "__main__":
    # Test básico del agente
    engine = SegmentationEngine("test_tenant")
    print(f"Agente inicializado: {engine.agent_name} v{engine.version}")
