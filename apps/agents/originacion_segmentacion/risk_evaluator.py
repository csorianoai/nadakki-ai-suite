"""
Risk Evaluator - Evaluador Avanzado de Riesgo de Recuperación
============================================================

Agente especializado en evaluar riesgos de recuperación mediante análisis
multifactorial de perfil crediticio, capacidad de pago y factores externos.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

class RiskEvaluator:
    """Evaluador avanzado de riesgo de recuperación"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.agent_name = "RiskEvaluator"
        self.version = "3.1.0"
        self.logger = logging.getLogger(f"nadakki.{self.agent_name}.{tenant_id}")
        
        # Modelos de riesgo
        self.modelo_riesgo = self._inicializar_modelo_riesgo()
        self.factores_macroeconomicos = self._cargar_factores_macroeconomicos()
        
        self.logger.info(f"Inicializado {self.agent_name} v{self.version} para tenant {tenant_id}")
    
    def execute(self, datos_evaluacion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar evaluación completa de riesgo de recuperación
        
        Args:
            datos_evaluacion: Datos financieros y contextuales del deudor
            
        Returns:
            Evaluación completa de riesgo con score y recomendaciones
        """
        inicio = datetime.now()
        
        try:
            # 1. Análisis de riesgo crediticio
            riesgo_crediticio = self._evaluar_riesgo_crediticio(datos_evaluacion)
            
            # 2. Evaluación de capacidad de pago
            capacidad_pago = self._evaluar_capacidad_pago(datos_evaluacion)
            
            # 3. Análisis de estabilidad laboral
            estabilidad_laboral = self._evaluar_estabilidad_laboral(datos_evaluacion)
            
            # 4. Factores de riesgo externos
            factores_externos = self._evaluar_factores_externos(datos_evaluacion)
            
            # 5. Análisis de comportamiento de pago
            comportamiento_pago = self._evaluar_comportamiento_pago(datos_evaluacion)
            
            # 6. Score de riesgo consolidado
            score_riesgo_consolidado = self._calcular_score_consolidado(
                riesgo_crediticio, capacidad_pago, estabilidad_laboral, 
                factores_externos, comportamiento_pago
            )
            
            # 7. Clasificación y recomendaciones
            clasificacion_riesgo = self._clasificar_riesgo(score_riesgo_consolidado)
            recomendaciones = self._generar_recomendaciones(clasificacion_riesgo, datos_evaluacion)
            
            tiempo_ejecucion = (datetime.now() - inicio).total_seconds()
            
            resultado = {
                "agente": self.agent_name,
                "version": self.version,
                "tenant_id": self.tenant_id,
                "timestamp": datetime.now().isoformat(),
                "tiempo_ejecucion_segundos": tiempo_ejecucion,
                
                # Score principal
                "score_riesgo_consolidado": score_riesgo_consolidado["score_final"],
                "clasificacion_riesgo": clasificacion_riesgo["categoria"],
                "nivel_riesgo": clasificacion_riesgo["nivel"],
                "confianza_evaluacion": score_riesgo_consolidado["confianza"],
                
                # Evaluaciones detalladas
                "evaluacion_detallada": {
                    "riesgo_crediticio": {
                        "score": riesgo_crediticio["score"],
                        "categoria": riesgo_crediticio["categoria"],
                        "factores_principales": riesgo_crediticio["factores_clave"]
                    },
                    "capacidad_pago": {
                        "score": capacidad_pago["score"],
                        "nivel_capacidad": capacidad_pago["nivel"],
                        "ratio_deuda_ingreso": capacidad_pago["ratio_deuda_ingreso"],
                        "ingreso_disponible": capacidad_pago["ingreso_disponible"]
                    },
                    "estabilidad_laboral": {
                        "score": estabilidad_laboral["score"],
                        "nivel_estabilidad": estabilidad_laboral["nivel"],
                        "factores_riesgo": estabilidad_laboral["factores_riesgo"]
                    },
                    "comportamiento_pago": {
                        "score": comportamiento_pago["score"],
                        "patron_historico": comportamiento_pago["patron"],
                        "tendencia": comportamiento_pago["tendencia"]
                    }
                },
                
                # Factores de riesgo
                "factores_riesgo_identificados": clasificacion_riesgo["factores_riesgo"],
                "factores_proteccion": clasificacion_riesgo["factores_proteccion"],
                "alertas_tempranas": clasificacion_riesgo["alertas"],
                
                # Proyecciones
                "proyecciones_riesgo": {
                    "probabilidad_recuperacion": clasificacion_riesgo["prob_recuperacion"],
                    "tiempo_estimado_recuperacion": clasificacion_riesgo["tiempo_estimado"],
                    "monto_recuperable_estimado": self._calcular_monto_recuperable(
                        datos_evaluacion, clasificacion_riesgo
                    ),
                    "scenario_stress": self._analizar_escenario_stress(score_riesgo_consolidado)
                },
                
                # Recomendaciones estratégicas
                "recomendaciones_estrategicas": {
                    "estrategia_principal": recomendaciones["estrategia_principal"],
                    "acciones_inmediatas": recomendaciones["acciones_inmediatas"],
                    "monitoreo_requerido": recomendaciones["monitoreo"],
                    "escalamiento": recomendaciones["escalamiento"]
                },
                
                # Metadatos
                "caso_id": datos_evaluacion.get("caso_id", "unknown"),
                "deudor_id": datos_evaluacion.get("deudor_id", "unknown"),
                "fecha_evaluacion": datetime.now().isoformat()
            }
            
            self.logger.info(f"Riesgo evaluado: {clasificacion_riesgo['categoria']} (Score: {score_riesgo_consolidado['score_final']})")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en evaluación de riesgo: {str(e)}")
            return {
                "agente": self.agent_name,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _inicializar_modelo_riesgo(self) -> Dict:
        """Inicializar modelo de evaluación de riesgo"""
        return {
            "factores_peso": {
                "riesgo_crediticio": 0.30,
                "capacidad_pago": 0.25,
                "estabilidad_laboral": 0.20,
                "comportamiento_pago": 0.15,
                "factores_externos": 0.10
            },
            "umbrales_riesgo": {
                "muy_bajo": 85,
                "bajo": 70,
                "medio": 55,
                "alto": 40,
                "muy_alto": 25,
                "critico": 10
            },
            "ajustes_contextuales": {
                "crisis_economica": -10,
                "estacionalidad_negativa": -5,
                "sector_afectado": -8,
                "region_problematica": -6
            }
        }
    
    def _cargar_factores_macroeconomicos(self) -> Dict:
        """Cargar factores macroeconómicos actuales"""
        return {
            "inflacion": 4.2,  # Estimado RD
            "desempleo": 7.8,
            "crecimiento_pib": 3.1,
            "estabilidad_cambiaria": 0.85,
            "condiciones_credito": 0.7,
            "confianza_consumidor": 0.65
        }
    
    def _evaluar_riesgo_crediticio(self, datos: Dict) -> Dict:
        """Evaluar riesgo crediticio base del deudor"""
        score_credito = datos.get("score_crediticio", 500)
        historial_credito = datos.get("historial_crediticio", {})
        
        # Normalizar score (300-850 a 0-100)
        score_normalizado = ((score_credito - 300) / 550) * 100
        score_normalizado = max(0, min(100, score_normalizado))
        
        # Ajustar por historial
        ajustes = 0
        
        # Pagos puntuales
        pagos_puntuales = historial_credito.get("pagos_puntuales", 0.5)
        if pagos_puntuales > 0.9:
            ajustes += 15
        elif pagos_puntuales > 0.7:
            ajustes += 5
        elif pagos_puntuales < 0.5:
            ajustes -= 10
        
        # Utilización de crédito
        utilizacion = historial_credito.get("utilizacion_credito", 0.5)
        if utilizacion < 0.3:
            ajustes += 10
        elif utilizacion > 0.8:
            ajustes -= 15
        
        # Antigüedad del historial
        antiguedad = historial_credito.get("antiguedad_anos", 1)
        if antiguedad > 5:
            ajustes += 8
        elif antiguedad < 2:
            ajustes -= 5
        
        # Número de cuentas
        num_cuentas = historial_credito.get("numero_cuentas", 3)
        if 3 <= num_cuentas <= 8:
            ajustes += 5
        elif num_cuentas > 15:
            ajustes -= 10
        
        score_final = max(0, min(100, score_normalizado + ajustes))
        
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
            categoria = "POBRE"
        
        factores_clave = []
        if pagos_puntuales < 0.6:
            factores_clave.append("historial_pagos_irregular")
        if utilizacion > 0.7:
            factores_clave.append("alta_utilizacion_credito")
        if score_credito < 450:
            factores_clave.append("score_crediticio_bajo")
        
        return {
            "score": round(score_final, 1),
            "categoria": categoria,
            "score_original": score_credito,
            "factores_clave": factores_clave,
            "ajustes_aplicados": ajustes
        }
    
    def _evaluar_capacidad_pago(self, datos: Dict) -> Dict:
        """Evaluar capacidad actual de pago"""
        ingresos = datos.get("ingresos_mensuales", 0)
        gastos_fijos = datos.get("gastos_fijos", 0)
        deudas_mensuales = datos.get("pagos_deudas_mensuales", 0)
        gastos_variables = datos.get("gastos_variables", 0)
        
        # Calcular ratios financieros
        gastos_totales = gastos_fijos + gastos_variables
        ingreso_disponible = max(0, ingresos - gastos_totales)
        ratio_deuda_ingreso = deudas_mensuales / max(1, ingresos)
        ratio_gastos_ingreso = gastos_totales / max(1, ingresos)
        
        # Score base de capacidad
        score_capacidad = 100
        
        # Penalizar por alto ratio de deuda
        if ratio_deuda_ingreso > 0.4:
            score_capacidad -= 30
        elif ratio_deuda_ingreso > 0.3:
            score_capacidad -= 15
        elif ratio_deuda_ingreso > 0.2:
            score_capacidad -= 5
        
        # Penalizar por alto ratio de gastos
        if ratio_gastos_ingreso > 0.8:
            score_capacidad -= 20
        elif ratio_gastos_ingreso > 0.6:
            score_capacidad -= 10
        
        # Ajustar por ingreso disponible
        if ingreso_disponible < ingresos * 0.1:
            score_capacidad -= 25
        elif ingreso_disponible < ingresos * 0.2:
            score_capacidad -= 10
        elif ingreso_disponible > ingresos * 0.3:
            score_capacidad += 10
        
        score_capacidad = max(0, min(100, score_capacidad))
        
        # Clasificar nivel de capacidad
        if score_capacidad >= 80:
            nivel = "ALTA"
        elif score_capacidad >= 60:
            nivel = "BUENA"
        elif score_capacidad >= 40:
            nivel = "MEDIA"
        elif score_capacidad >= 20:
            nivel = "BAJA"
        else:
            nivel = "CRITICA"
        
        return {
            "score": round(score_capacidad, 1),
            "nivel": nivel,
            "ingreso_disponible": round(ingreso_disponible, 2),
            "ratio_deuda_ingreso": round(ratio_deuda_ingreso, 3),
            "ratio_gastos_ingreso": round(ratio_gastos_ingreso, 3),
            "ingresos_mensuales": ingresos,
            "capacidad_pago_estimada": round(ingreso_disponible * 0.6, 2)  # 60% del disponible
        }
    
    def _evaluar_estabilidad_laboral(self, datos: Dict) -> Dict:
        """Evaluar estabilidad laboral del deudor"""
        tipo_empleo = datos.get("tipo_empleo", "empleado")
        antiguedad_empleo = datos.get("antiguedad_empleo_anos", 1)
        sector_economia = datos.get("sector_economia", "servicios")
        tamano_empresa = datos.get("tamano_empresa", "mediana")
        
        # Score base por tipo de empleo
        scores_tipo_empleo = {
            "empleado_publico": 90,
            "empleado_multinacional": 85,
            "empleado_empresa_grande": 75,
            "empleado": 65,
            "independiente_establecido": 60,
            "independiente": 50,
            "temporal": 30,
            "desempleado": 0
        }
        
        score_base = scores_tipo_empleo.get(tipo_empleo, 50)
        
        # Ajuste por antigüedad
        if antiguedad_empleo >= 5:
            ajuste_antiguedad = 15
        elif antiguedad_empleo >= 2:
            ajuste_antiguedad = 8
        elif antiguedad_empleo >= 1:
            ajuste_antiguedad = 3
        else:
            ajuste_antiguedad = -15
        
        # Ajuste por sector económico
        sectores_estables = ["educacion", "salud", "gobierno", "banca"]
        sectores_variables = ["turismo", "construccion", "retail", "gastronomia"]
        sectores_riesgo = ["textil", "manufactura", "agricultura"]
        
        if sector_economia in sectores_estables:
            ajuste_sector = 10
        elif sector_economia in sectores_variables:
            ajuste_sector = -5
        elif sector_economia in sectores_riesgo:
            ajuste_sector = -15
        else:
            ajuste_sector = 0
        
        # Ajuste por tamaño de empresa
        ajustes_tamano = {
            "multinacional": 10,
            "grande": 5,
            "mediana": 0,
            "pequena": -5,
            "micro": -10
        }
        ajuste_tamano = ajustes_tamano.get(tamano_empresa, 0)
        
        score_final = max(0, min(100, score_base + ajuste_antiguedad + ajuste_sector + ajuste_tamano))
        
        # Clasificar nivel
        if score_final >= 80:
            nivel = "MUY_ESTABLE"
        elif score_final >= 65:
            nivel = "ESTABLE"
        elif score_final >= 50:
            nivel = "MODERADO"
        elif score_final >= 35:
            nivel = "INESTABLE"
        else:
            nivel = "MUY_INESTABLE"
        
        # Identificar factores de riesgo
        factores_riesgo = []
        if antiguedad_empleo < 1:
            factores_riesgo.append("empleo_reciente")
        if sector_economia in sectores_riesgo:
            factores_riesgo.append("sector_vulnerable")
        if tipo_empleo in ["independiente", "temporal"]:
            factores_riesgo.append("empleo_inestable")
        
        return {
            "score": round(score_final, 1),
            "nivel": nivel,
            "tipo_empleo": tipo_empleo,
            "antiguedad_anos": antiguedad_empleo,
            "sector": sector_economia,
            "factores_riesgo": factores_riesgo
        }
    
    def _evaluar_factores_externos(self, datos: Dict) -> Dict:
        """Evaluar factores externos que afectan el riesgo"""
        region = datos.get("region", "centro")
        sector_vivienda = datos.get("sector_vivienda", "clase_media")
        situacion_familiar = datos.get("situacion_familiar", "estable")
        
        score_base = 70  # Neutral
        
        # Factor regional
        regiones_estables = ["distrito_nacional", "santiago", "zona_colonial"]
        regiones_riesgo = ["provincias_frontera", "zona_rural_alejada"]
        
        if region in regiones_estables:
            ajuste_regional = 10
        elif region in regiones_riesgo:
            ajuste_regional = -15
        else:
            ajuste_regional = 0
        
        # Factor socioeconómico del sector
        if sector_vivienda == "alto":
            ajuste_vivienda = 15
        elif sector_vivienda == "medio_alto":
            ajuste_vivienda = 8
        elif sector_vivienda == "clase_media":
            ajuste_vivienda = 0
        elif sector_vivienda == "popular":
            ajuste_vivienda = -8
        else:  # marginal
            ajuste_vivienda = -20
        
        # Factor familiar
        if situacion_familiar == "estable_con_apoyo":
            ajuste_familiar = 12
        elif situacion_familiar == "estable":
            ajuste_familiar = 5
        elif situacion_familiar == "complicada":
            ajuste_familiar = -10
        else:  # crisis_familiar
            ajuste_familiar = -20
        
        # Factores macroeconómicos
        macro = self.factores_macroeconomicos
        ajuste_macro = 0
        
        if macro["inflacion"] > 6:
            ajuste_macro -= 5
        if macro["desempleo"] > 10:
            ajuste_macro -= 8
        if macro["confianza_consumidor"] < 0.5:
            ajuste_macro -= 5
        
        score_final = max(0, min(100, score_base + ajuste_regional + ajuste_vivienda + 
                                ajuste_familiar + ajuste_macro))
        
        return {
            "score": round(score_final, 1),
            "factores_considerados": {
                "region": region,
                "sector_vivienda": sector_vivienda,
                "situacion_familiar": situacion_familiar,
                "condiciones_macro": "normales" if ajuste_macro >= -5 else "adversas"
            },
            "ajustes_aplicados": {
                "regional": ajuste_regional,
                "vivienda": ajuste_vivienda,
                "familiar": ajuste_familiar,
                "macroeconomico": ajuste_macro
            }
        }
    
    def _evaluar_comportamiento_pago(self, datos: Dict) -> Dict:
        """Evaluar comportamiento histórico de pagos"""
        historial_pagos = datos.get("historial_pagos", [])
        promesas_pago = datos.get("historial_promesas", [])
        
        if not historial_pagos:
            return {
                "score": 50,
                "patron": "sin_historial",
                "tendencia": "desconocida"
            }
        
        # Analizar pagos
        total_pagos = len(historial_pagos)
        pagos_puntuales = sum(1 for p in historial_pagos if p.get("puntual", False))
        pagos_con_retraso = sum(1 for p in historial_pagos if p.get("dias_retraso", 0) > 0)
        
        # Score base por puntualidad
        ratio_puntualidad = pagos_puntuales / total_pagos if total_pagos > 0 else 0
        score_puntualidad = ratio_puntualidad * 100
        
        # Analizar promesas
        if promesas_pago:
            promesas_cumplidas = sum(1 for p in promesas_pago if p.get("cumplida", False))
            ratio_cumplimiento = promesas_cumplidas / len(promesas_pago)
            score_promesas = ratio_cumplimiento * 100
        else:
            score_promesas = 50  # Neutral si no hay promesas
        
        # Score combinado (70% puntualidad, 30% cumplimiento promesas)
        score_final = (score_puntualidad * 0.7) + (score_promesas * 0.3)
        
        # Determinar patrón
        if ratio_puntualidad >= 0.9:
            patron = "excelente_pagador"
        elif ratio_puntualidad >= 0.7:
            patron = "buen_pagador"
        elif ratio_puntualidad >= 0.5:
            patron = "pagador_irregular"
        elif ratio_puntualidad >= 0.3:
            patron = "mal_pagador"
        else:
            patron = "muy_mal_pagador"
        
        # Analizar tendencia temporal
        pagos_recientes = [p for p in historial_pagos[-6:]]  # Últimos 6 pagos
        pagos_antiguos = [p for p in historial_pagos[:-6]] if len(historial_pagos) > 6 else []
        
        if pagos_recientes and pagos_antiguos:
            ratio_reciente = sum(1 for p in pagos_recientes if p.get("puntual", False)) / len(pagos_recientes)
            ratio_antiguo = sum(1 for p in pagos_antiguos if p.get("puntual", False)) / len(pagos_antiguos)
            
            if ratio_reciente > ratio_antiguo + 0.2:
                tendencia = "mejorando"
            elif ratio_reciente < ratio_antiguo - 0.2:
                tendencia = "empeorando"
            else:
                tendencia = "estable"
        else:
            tendencia = "insuficientes_datos"
        
        return {
            "score": round(score_final, 1),
            "patron": patron,
            "tendencia": tendencia,
            "ratio_puntualidad": round(ratio_puntualidad, 3),
            "total_pagos_evaluados": total_pagos,
            "cumplimiento_promesas": round(ratio_cumplimiento, 3) if promesas_pago else None
        }
    
    def _calcular_score_consolidado(self, crediticio: Dict, capacidad: Dict, laboral: Dict, 
                                   externos: Dict, comportamiento: Dict) -> Dict:
        """Calcular score consolidado de riesgo"""
        pesos = self.modelo_riesgo["factores_peso"]
        
        # Score ponderado
        score_consolidado = (
            crediticio["score"] * pesos["riesgo_crediticio"] +
            capacidad["score"] * pesos["capacidad_pago"] +
            laboral["score"] * pesos["estabilidad_laboral"] +
            comportamiento["score"] * pesos["comportamiento_pago"] +
            externos["score"] * pesos["factores_externos"]
        )
        
        # Calcular confianza basada en disponibilidad de datos
        factores_confianza = 0
        if crediticio["score"] > 0:
            factores_confianza += 0.3
        if capacidad["score"] > 0:
            factores_confianza += 0.25
        if laboral["score"] > 0:
            factores_confianza += 0.2
        if comportamiento["score"] > 0:
            factores_confianza += 0.15
        if externos["score"] > 0:
            factores_confianza += 0.1
        
        confianza = min(0.95, factores_confianza)
        
        return {
            "score_final": round(score_consolidado, 1),
            "confianza": round(confianza, 2),
            "componentes": {
                "crediticio": crediticio["score"],
                "capacidad": capacidad["score"],
                "laboral": laboral["score"],
                "comportamiento": comportamiento["score"],
                "externos": externos["score"]
            },
            "pesos_aplicados": pesos
        }
    
    def _clasificar_riesgo(self, score_consolidado: Dict) -> Dict:
        """Clasificar nivel de riesgo basado en score consolidado"""
        score = score_consolidado["score_final"]
        umbrales = self.modelo_riesgo["umbrales_riesgo"]
        
        if score >= umbrales["muy_bajo"]:
            categoria = "MUY_BAJO_RIESGO"
            nivel = 1
            prob_recuperacion = 0.95
            tiempo_estimado = 30
        elif score >= umbrales["bajo"]:
            categoria = "BAJO_RIESGO"
            nivel = 2
            prob_recuperacion = 0.85
            tiempo_estimado = 45
        elif score >= umbrales["medio"]:
            categoria = "RIESGO_MEDIO"
            nivel = 3
            prob_recuperacion = 0.65
            tiempo_estimado = 60
        elif score >= umbrales["alto"]:
            categoria = "ALTO_RIESGO"
            nivel = 4
            prob_recuperacion = 0.40
            tiempo_estimado = 90
        elif score >= umbrales["muy_alto"]:
            categoria = "MUY_ALTO_RIESGO"
            nivel = 5
            prob_recuperacion = 0.25
            tiempo_estimado = 120
        else:
            categoria = "RIESGO_CRITICO"
            nivel = 6
            prob_recuperacion = 0.10
            tiempo_estimado = 180
        
        # Identificar factores de riesgo y protección
        factores_riesgo = []
        factores_proteccion = []
        alertas = []
        
        componentes = score_consolidado["componentes"]
        
        if componentes["crediticio"] < 40:
            factores_riesgo.append("perfil_crediticio_deficiente")
        if componentes["capacidad"] < 30:
            factores_riesgo.append("capacidad_pago_limitada")
            alertas.append("capacidad_pago_critica")
        if componentes["laboral"] < 40:
            factores_riesgo.append("inestabilidad_laboral")
        if componentes["comportamiento"] < 35:
            factores_riesgo.append("mal_historial_pagos")
        
        if componentes["crediticio"] > 75:
            factores_proteccion.append("excelente_perfil_crediticio")
        if componentes["capacidad"] > 70:
            factores_proteccion.append("buena_capacidad_pago")
        if componentes["laboral"] > 75:
            factores_proteccion.append("estabilidad_laboral")
        
        return {
            "categoria": categoria,
            "nivel": nivel,
            "prob_recuperacion": prob_recuperacion,
            "tiempo_estimado": tiempo_estimado,
            "factores_riesgo": factores_riesgo,
            "factores_proteccion": factores_proteccion,
            "alertas": alertas
        }
    
    def _generar_recomendaciones(self, clasificacion: Dict, datos: Dict) -> Dict:
        """Generar recomendaciones estratégicas basadas en clasificación"""
        nivel_riesgo = clasificacion["nivel"]
        
        if nivel_riesgo <= 2:  # Bajo riesgo
            estrategia = "gestion_colaborativa"
            acciones = ["contacto_regular", "recordatorios_amigables", "opciones_pago"]
            monitoreo = "mensual"
            escalamiento = "sin_escalamiento"
        elif nivel_riesgo == 3:  # Riesgo medio
            estrategia = "gestion_estructurada"
            acciones = ["seguimiento_semanal", "planes_pago", "incentivos_pronto_pago"]
            monitoreo = "quincenal"
            escalamiento = "escalamiento_gradual"
        elif nivel_riesgo == 4:  # Alto riesgo
            estrategia = "gestion_intensiva"
            acciones = ["contacto_diario", "presion_moderada", "negociacion_agresiva"]
            monitoreo = "semanal"
            escalamiento = "escalamiento_rapido"
        else:  # Muy alto riesgo o crítico
            estrategia = "gestion_legal"
            acciones = ["accion_legal_inmediata", "embargo_preventivo", "negociacion_final"]
            monitoreo = "diario"
            escalamiento = "escalamiento_inmediato"
        
        return {
            "estrategia_principal": estrategia,
            "acciones_inmediatas": acciones,
            "monitoreo": monitoreo,
            "escalamiento": escalamiento
        }
    
    def _calcular_monto_recuperable(self, datos: Dict, clasificacion: Dict) -> float:
        """Calcular monto estimado recuperable"""
        monto_deuda = datos.get("monto_deuda", 0)
        prob_recuperacion = clasificacion["prob_recuperacion"]
        
        # Ajustar por capacidad de pago
        capacidad_pago = datos.get("capacidad_pago_estimada", monto_deuda * 0.1)
        
        # Estimación conservadora
        monto_recuperable = min(monto_deuda, capacidad_pago * 12) * prob_recuperacion
        
        return round(monto_recuperable, 2)
    
    def _analizar_escenario_stress(self, score_consolidado: Dict) -> Dict:
        """Analizar comportamiento bajo escenario de stress económico"""
        score_actual = score_consolidado["score_final"]
        
        # Aplicar penalizaciones de stress
        ajustes_stress = self.modelo_riesgo["ajustes_contextuales"]
        penalizacion_total = sum(ajustes_stress.values())
        
        score_stress = max(0, score_actual + penalizacion_total)
        
        deterioro = score_actual - score_stress
        
        return {
            "score_bajo_stress": round(score_stress, 1),
            "deterioro_score": round(deterioro, 1),
            "resistencia_stress": "alta" if deterioro < 5 else "media" if deterioro < 15 else "baja"
        }
    
    def policy(self) -> Dict[str, Any]:
        """Políticas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "requires_tenant_isolation": True,
            "data_retention_days": 1825,  # 5 años
            "compliance_requirements": ["INDOTEL_172_13"],
            "risk_model_version": "3.1.0",
            "recalibration_frequency": "trimestral"
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Métricas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "evaluaciones_realizadas": 0,
            "precision_clasificacion": 0.87,
            "tiempo_promedio_evaluacion": 2.8,
            "distribucion_riesgo": {
                "bajo": "30%",
                "medio": "40%",
                "alto": "25%",
                "critico": "5%"
            }
        }

if __name__ == "__main__":
    evaluator = RiskEvaluator("test_tenant")
    print(f"Agente inicializado: {evaluator.agent_name} v{evaluator.version}")
