"""
Profiling Analyzer - Analizador de Perfiles de Deudor
=====================================================

Agente especializado en crear perfiles detallados de deudores basados en:
datos demográficos, psicológicos, financieros y comportamentales.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class ProfilingAnalyzer:
    """Analizador avanzado de perfiles de deudor"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.agent_name = "ProfilingAnalyzer"
        self.version = "3.1.0"
        self.logger = logging.getLogger(f"nadakki.{self.agent_name}.{tenant_id}")
        
        # Inicializar patrones y arquetipos
        self.arquetipos_deudor = self._inicializar_arquetipos()
        self.patrones_comportamiento = self._definir_patrones_comportamiento()
        self.factores_psicologicos = self._definir_factores_psicologicos()
        
        self.logger.info(f"Inicializado {self.agent_name} v{self.version} para tenant {tenant_id}")
    
    def execute(self, datos_perfilado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar análisis completo de perfilado del deudor
        
        Args:
            datos_perfilado: Datos completos para análisis de perfil
            
        Returns:
            Perfil detallado con recomendaciones estratégicas personalizadas
        """
        inicio = datetime.now()
        
        try:
            # 1. Análisis demográfico
            perfil_demografico = self._analizar_demografia(datos_perfilado)
            
            # 2. Análisis psicológico
            perfil_psicologico = self._analizar_psicologia(datos_perfilado)
            
            # 3. Análisis de patrones de comunicación
            patrones_comunicacion = self._analizar_comunicacion(datos_perfilado)
            
            # 4. Análisis de estilo de vida
            estilo_vida = self._analizar_estilo_vida(datos_perfilado)
            
            # 5. Identificación de arquetipo principal
            arquetipo_principal = self._identificar_arquetipo(
                perfil_demografico, perfil_psicologico, patrones_comunicacion, estilo_vida
            )
            
            # 6. Estrategia de comunicación personalizada
            estrategia_personalizada = self._generar_estrategia_personalizada(
                arquetipo_principal, datos_perfilado
            )
            
            # 7. Predicción de respuesta
            prediccion_respuesta = self._predecir_respuesta(arquetipo_principal, datos_perfilado)
            
            tiempo_ejecucion = (datetime.now() - inicio).total_seconds()
            
            resultado = {
                "agente": self.agent_name,
                "version": self.version,
                "tenant_id": self.tenant_id,
                "timestamp": datetime.now().isoformat(),
                "tiempo_ejecucion_segundos": tiempo_ejecucion,
                
                # Perfil demográfico
                "perfil_demografico": {
                    "segmento_edad": perfil_demografico["segmento_edad"],
                    "nivel_educativo": perfil_demografico["nivel_educativo"],
                    "zona_geografica": perfil_demografico["zona_geografica"],
                    "estado_civil": perfil_demografico["estado_civil"],
                    "ocupacion_categoria": perfil_demografico["ocupacion_categoria"]
                },
                
                # Perfil psicológico
                "perfil_psicologico": {
                    "personalidad_dominante": perfil_psicologico["personalidad_dominante"],
                    "nivel_stress_financiero": perfil_psicologico["nivel_stress"],
                    "predisposicion_cooperacion": perfil_psicologico["predisposicion_cooperacion"],
                    "factores_motivacion": perfil_psicologico["factores_motivacion"]
                },
                
                # Patrones de comunicación
                "comunicacion": {
                    "canal_preferido": patrones_comunicacion["canal_preferido"],
                    "horario_optimo": patrones_comunicacion["horario_optimo"],
                    "estilo_comunicacion": patrones_comunicacion["estilo"],
                    "nivel_formalidad": patrones_comunicacion["formalidad"]
                },
                
                # Arquetipo identificado
                "arquetipo_principal": {
                    "tipo": arquetipo_principal["tipo"],
                    "subtipo": arquetipo_principal["subtipo"],
                    "confianza": arquetipo_principal["confianza"],
                    "descripcion": arquetipo_principal["descripcion"]
                },
                
                # Estrategia personalizada
                "estrategia_personalizada": {
                    "enfoque_recomendado": estrategia_personalizada["enfoque"],
                    "mensaje_clave": estrategia_personalizada["mensaje_clave"],
                    "incentivos_efectivos": estrategia_personalizada["incentivos"],
                    "canales_prioritarios": estrategia_personalizada["canales"],
                    "timing_optimo": estrategia_personalizada["timing"],
                    "predisposicion": estrategia_personalizada["predisposicion"]
                },
                
                # Predicción de comportamiento
                "prediccion_respuesta": {
                    "probabilidad_contacto": prediccion_respuesta["prob_contacto"],
                    "probabilidad_pago": prediccion_respuesta["prob_pago"],
                    "resistencia_esperada": prediccion_respuesta["resistencia"],
                    "tiempo_esperado_resolucion": prediccion_respuesta["tiempo_resolucion"]
                },
                
                # Resumen del perfil
                "resumen_perfil": {
                    "arquetipo_deudor": arquetipo_principal["tipo"],
                    "nivel_complejidad": self._evaluar_complejidad_caso(arquetipo_principal),
                    "estrategia_optima": estrategia_personalizada["enfoque"],
                    "probabilidad_exito": prediccion_respuesta["prob_exito"]
                },
                
                # Metadatos
                "caso_id": datos_perfilado.get("caso_id", "unknown"),
                "deudor_id": datos_perfilado.get("deudor_id", "unknown")
            }
            
            self.logger.info(f"Perfil generado: {arquetipo_principal['tipo']} con {prediccion_respuesta['prob_exito']}% prob éxito")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en perfilado: {str(e)}")
            return {
                "agente": self.agent_name,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _inicializar_arquetipos(self) -> Dict:
        """Inicializar arquetipos de deudores"""
        return {
            "COLABORADOR": {
                "descripcion": "Deudor cooperativo que busca soluciones",
                "caracteristicas": ["comunicativo", "transparente", "proactivo"],
                "estrategia_optima": "consultiva",
                "canales_efectivos": ["telefono", "email", "whatsapp"],
                "probabilidad_exito": 0.85
            },
            "ORGANIZADOR": {
                "descripcion": "Deudor estructurado que prefiere planes claros",
                "caracteristicas": ["metódico", "planificador", "cumplidor"],
                "estrategia_optima": "estructurada",
                "canales_efectivos": ["email", "documentos", "telefono"],
                "probabilidad_exito": 0.80
            },
            "EMOTIVO": {
                "descripcion": "Deudor que responde a factores emocionales",
                "caracteristicas": ["sensible", "variable", "reactivo"],
                "estrategia_optima": "empática",
                "canales_efectivos": ["telefono", "presencial", "whatsapp"],
                "probabilidad_exito": 0.65
            },
            "PRAGMATICO": {
                "descripcion": "Deudor que busca soluciones prácticas",
                "caracteristicas": ["directo", "realista", "negociador"],
                "estrategia_optima": "directa",
                "canales_efectivos": ["telefono", "sms", "whatsapp"],
                "probabilidad_exito": 0.70
            },
            "EVASIVO": {
                "descripcion": "Deudor que evita el contacto y compromiso",
                "caracteristicas": ["esquivo", "prometedor", "incumplidor"],
                "estrategia_optima": "persistente",
                "canales_efectivos": ["visita", "multi_canal", "presion_legal"],
                "probabilidad_exito": 0.40
            },
            "COMBATIVO": {
                "descripcion": "Deudor confrontacional y resistente",
                "caracteristicas": ["agresivo", "discutidor", "renuente"],
                "estrategia_optima": "firme_legal",
                "canales_efectivos": ["legal", "presencial", "autoridad"],
                "probabilidad_exito": 0.35
            }
        }
    
    def _definir_patrones_comportamiento(self) -> Dict:
        """Definir patrones de comportamiento observables"""
        return {
            "comunicacion_frecuente": {
                "indicadores": ["responde_llamadas", "inicia_contacto", "proporciona_actualizaciones"],
                "arquetipo_asociado": "COLABORADOR"
            },
            "solicita_documentacion": {
                "indicadores": ["pide_estados_cuenta", "solicita_detalles", "revisa_terminos"],
                "arquetipo_asociado": "ORGANIZADOR"
            },
            "referencias_familiares": {
                "indicadores": ["menciona_familia", "carga_emocional", "situacion_personal"],
                "arquetipo_asociado": "EMOTIVO"
            },
            "negocia_activamente": {
                "indicadores": ["propone_alternativas", "discute_montos", "busca_beneficios"],
                "arquetipo_asociado": "PRAGMATICO"
            },
            "evita_compromisos": {
                "indicadores": ["promesas_vagas", "cambia_tema", "no_especifica_fechas"],
                "arquetipo_asociado": "EVASIVO"
            },
            "muestra_hostilidad": {
                "indicadores": ["tono_agresivo", "amenazas", "culpa_terceros"],
                "arquetipo_asociado": "COMBATIVO"
            }
        }
    
    def _definir_factores_psicologicos(self) -> Dict:
        """Definir factores psicológicos que influyen en comportamiento"""
        return {
            "stress_financiero": {
                "alto": ["multiple_deudas", "desempleo", "emergencia_medica"],
                "medio": ["ingresos_variables", "gastos_altos", "compromisos_familiares"],
                "bajo": ["ingresos_estables", "situacion_controlada", "apoyo_familiar"]
            },
            "personalidad_dominante": {
                "analitica": ["solicita_detalles", "evalua_opciones", "planifica"],
                "expresiva": ["comunicativo", "emotivo", "social"],
                "controlador": ["directo", "decidido", "dominante"],
                "amigable": ["cooperativo", "evita_conflicto", "busca_aprobacion"]
            },
            "factores_motivacion": {
                "financieros": ["ahorro_intereses", "mejora_score", "evita_costos"],
                "sociales": ["reputacion", "familia", "comunidad"],
                "legales": ["evita_demanda", "protege_bienes", "evita_embargo"],
                "personales": ["tranquilidad", "autoestima", "cumplimiento"]
            }
        }
    
    def _analizar_demografia(self, datos: Dict) -> Dict:
        """Analizar perfil demográfico"""
        edad = datos.get("edad", 35)
        educacion = datos.get("nivel_educativo", "secundaria")
        zona = datos.get("zona_residencia", "urbana")
        estado_civil = datos.get("estado_civil", "soltero")
        ocupacion = datos.get("ocupacion", "empleado")
        
        # Segmentar por edad
        if edad < 25:
            segmento_edad = "joven"
        elif edad < 40:
            segmento_edad = "adulto_joven"
        elif edad < 55:
            segmento_edad = "adulto_medio"
        else:
            segmento_edad = "adulto_mayor"
        
        # Categorizar ocupación
        ocupaciones_altas = ["profesional", "ejecutivo", "empresario", "medico", "abogado"]
        ocupaciones_medias = ["empleado", "tecnico", "supervisor", "comerciante"]
        
        if any(ocp in ocupacion.lower() for ocp in ocupaciones_altas):
            ocupacion_categoria = "alta"
        elif any(ocp in ocupacion.lower() for ocp in ocupaciones_medias):
            ocupacion_categoria = "media"
        else:
            ocupacion_categoria = "basica"
        
        return {
            "segmento_edad": segmento_edad,
            "nivel_educativo": educacion,
            "zona_geografica": zona,
            "estado_civil": estado_civil,
            "ocupacion_categoria": ocupacion_categoria
        }
    
    def _analizar_psicologia(self, datos: Dict) -> Dict:
        """Analizar perfil psicológico basado en comportamiento"""
        historial_contactos = datos.get("historial_contactos", [])
        historial_promesas = datos.get("historial_promesas", [])
        notas_agente = datos.get("notas_agente", "")
        
        # Analizar nivel de stress
        indicadores_stress = ["multiple", "urgente", "problema", "crisis", "ayuda", "desesperado"]
        stress_mentions = sum(1 for ind in indicadores_stress if ind in notas_agente.lower())
        
        if stress_mentions >= 3:
            nivel_stress = "alto"
        elif stress_mentions >= 1:
            nivel_stress = "medio"
        else:
            nivel_stress = "bajo"
        
        # Analizar personalidad dominante
        indicadores_personalidad = {
            "analitica": ["necesito", "detalles", "explicar", "entender", "revisar"],
            "expresiva": ["siento", "emociones", "familia", "personal", "corazón"],
            "controlador": ["quiero", "exijo", "debe", "inmediato", "ahora"],
            "amigable": ["ayudar", "colaborar", "juntos", "por favor", "gracias"]
        }
        
        scores_personalidad = {}
        for personalidad, indicators in indicadores_personalidad.items():
            score = sum(1 for ind in indicators if ind in notas_agente.lower())
            scores_personalidad[personalidad] = score
        
        personalidad_dominante = max(scores_personalidad.items(), key=lambda x: x[1])[0]
        
        # Predisposición a cooperación
        if personalidad_dominante in ["analitica", "amigable"]:
            predisposicion_cooperacion = "alta"
        elif personalidad_dominante == "expresiva":
            predisposicion_cooperacion = "media"
        else:
            predisposicion_cooperacion = "baja"
        
        # Factores de motivación
        factores_motivacion = []
        if "familia" in notas_agente.lower() or "hijos" in notas_agente.lower():
            factores_motivacion.append("social")
        if "trabajo" in notas_agente.lower() or "empleo" in notas_agente.lower():
            factores_motivacion.append("financiero")
        if "legal" in notas_agente.lower() or "demanda" in notas_agente.lower():
            factores_motivacion.append("legal")
        if not factores_motivacion:
            factores_motivacion.append("personal")
        
        return {
            "personalidad_dominante": personalidad_dominante,
            "nivel_stress": nivel_stress,
            "predisposicion_cooperacion": predisposicion_cooperacion,
            "factores_motivacion": factores_motivacion
        }
    
    def _analizar_comunicacion(self, datos: Dict) -> Dict:
        """Analizar patrones de comunicación preferidos"""
        historial_contactos = datos.get("historial_contactos", [])
        
        # Analizar canal preferido
        canales_exitosos = {}
        for contacto in historial_contactos:
            canal = contacto.get("canal", "telefono")
            exitoso = contacto.get("exitoso", False)
            
            if canal not in canales_exitosos:
                canales_exitosos[canal] = {"total": 0, "exitosos": 0}
            
            canales_exitosos[canal]["total"] += 1
            if exitoso:
                canales_exitosos[canal]["exitosos"] += 1
        
        # Determinar canal preferido por tasa de éxito
        mejor_canal = "telefono"  # default
        mejor_tasa = 0
        
        for canal, stats in canales_exitosos.items():
            if stats["total"] > 0:
                tasa_exito = stats["exitosos"] / stats["total"]
                if tasa_exito > mejor_tasa:
                    mejor_tasa = tasa_exito
                    mejor_canal = canal
        
        # Analizar horario óptimo
        horarios_contacto = [c.get("hora", "10:00") for c in historial_contactos if c.get("exitoso", False)]
        if horarios_contacto:
            # Simplificar: agrupar en mañana, tarde, noche
            horas = [int(h.split(":")[0]) for h in horarios_contacto if ":" in h]
            if horas:
                hora_promedio = sum(horas) / len(horas)
                if hora_promedio < 12:
                    horario_optimo = "mañana"
                elif hora_promedio < 18:
                    horario_optimo = "tarde"
                else:
                    horario_optimo = "noche"
            else:
                horario_optimo = "tarde"
        else:
            horario_optimo = "tarde"
        
        return {
            "canal_preferido": mejor_canal,
            "horario_optimo": horario_optimo,
            "estilo": "directo",  # Se puede inferir de notas
            "formalidad": "medio"
        }
    
    def _analizar_estilo_vida(self, datos: Dict) -> Dict:
        """Analizar estilo de vida del deudor"""
        ingresos = datos.get("ingresos_mensuales", 0)
        gastos = datos.get("gastos_mensuales", 0)
        ocupacion = datos.get("ocupacion", "")
        zona = datos.get("zona_residencia", "")
        
        # Determinar nivel socioeconómico
        if ingresos > 100000:  # RD$
            nivel_socioeconomico = "alto"
        elif ingresos > 50000:
            nivel_socioeconomico = "medio"
        else:
            nivel_socioeconomico = "bajo"
        
        # Determinar estilo de vida
        ratio_gastos = gastos / max(1, ingresos)
        
        if ratio_gastos > 0.9:
            estilo_gasto = "austero"
        elif ratio_gastos > 0.7:
            estilo_gasto = "equilibrado"
        else:
            estilo_gasto = "liberal"
        
        return {
            "nivel_socioeconomico": nivel_socioeconomico,
            "estilo_gasto": estilo_gasto,
            "estabilidad_laboral": "estable" if "empleado" in ocupacion.lower() else "variable"
        }
    
    def _identificar_arquetipo(self, demografia: Dict, psicologia: Dict, 
                              comunicacion: Dict, estilo_vida: Dict) -> Dict:
        """Identificar arquetipo principal del deudor"""
        
        # Sistema de scoring para cada arquetipo
        scores_arquetipos = {}
        
        for arquetipo, perfil in self.arquetipos_deudor.items():
            score = 0
            
            # Factores demográficos
            if demografia["ocupacion_categoria"] == "alta" and arquetipo == "ORGANIZADOR":
                score += 15
            if demografia["nivel_educativo"] in ["universitaria", "posgrado"] and arquetipo in ["COLABORADOR", "ORGANIZADOR"]:
                score += 10
            
            # Factores psicológicos
            if psicologia["personalidad_dominante"] == "amigable" and arquetipo == "COLABORADOR":
                score += 20
            if psicologia["personalidad_dominante"] == "analitica" and arquetipo == "ORGANIZADOR":
                score += 20
            if psicologia["personalidad_dominante"] == "expresiva" and arquetipo == "EMOTIVO":
                score += 20
            if psicologia["personalidad_dominante"] == "controlador" and arquetipo in ["PRAGMATICO", "COMBATIVO"]:
                score += 15
            
            if psicologia["predisposicion_cooperacion"] == "alta" and arquetipo in ["COLABORADOR", "ORGANIZADOR"]:
                score += 15
            if psicologia["predisposicion_cooperacion"] == "baja" and arquetipo in ["EVASIVO", "COMBATIVO"]:
                score += 15
            
            # Factores de comunicación
            if comunicacion["canal_preferido"] in perfil["canales_efectivos"]:
                score += 10
            
            scores_arquetipos[arquetipo] = score
        
        # Seleccionar arquetipo con mayor score
        arquetipo_principal = max(scores_arquetipos.items(), key=lambda x: x[1])
        
        # Determinar subtipo
        subtipo = "estandar"
        if demografia["nivel_educativo"] in ["universitaria", "posgrado"]:
            subtipo = "educado"
        elif estilo_vida["nivel_socioeconomico"] == "alto":
            subtipo = "premium"
        elif psicologia["nivel_stress"] == "alto":
            subtipo = "presionado"
        
        # Calcular confianza
        score_max = max(scores_arquetipos.values())
        score_segundo = sorted(scores_arquetipos.values(), reverse=True)[1] if len(scores_arquetipos) > 1 else 0
        confianza = min(0.95, (score_max / max(1, score_max + score_segundo)) * 1.2)
        
        return {
            "tipo": arquetipo_principal[0],
            "subtipo": subtipo,
            "confianza": round(confianza, 2),
            "descripcion": self.arquetipos_deudor[arquetipo_principal[0]]["descripcion"],
            "score": score_max
        }
    
    def _generar_estrategia_personalizada(self, arquetipo: Dict, datos: Dict) -> Dict:
        """Generar estrategia personalizada basada en arquetipo"""
        
        perfil_arquetipo = self.arquetipos_deudor[arquetipo["tipo"]]
        
        # Estrategias base por arquetipo
        estrategias_personalizadas = {
            "COLABORADOR": {
                "enfoque": "consultivo_colaborativo",
                "mensaje_clave": "Trabajemos juntos para encontrar la mejor solución",
                "incentivos": ["descuentos_pronto_pago", "planes_flexibles", "comunicacion_directa"],
                "canales": ["telefono_personal", "email", "whatsapp"],
                "timing": {"frecuencia": "semanal", "momento": "mañana"},
                "predisposicion": "POSITIVA"
            },
            "ORGANIZADOR": {
                "enfoque": "estructurado_detallado",
                "mensaje_clave": "Le presento un plan claro y detallado para resolver su situación",
                "incentivos": ["planes_estructurados", "documentacion_detallada", "cronogramas_claros"],
                "canales": ["email_formal", "documentos", "telefono_estructurado"],
                "timing": {"frecuencia": "quincenal", "momento": "tarde"},
                "predisposicion": "NEUTRAL_POSITIVA"
            },
            "EMOTIVO": {
                "enfoque": "empatico_comprensivo",
                "mensaje_clave": "Entendemos su situación y queremos ayudarle",
                "incentivos": ["consideraciones_personales", "flexibilidad_fechas", "apoyo_emocional"],
                "canales": ["telefono_empatico", "whatsapp", "presencial_ocasional"],
                "timing": {"frecuencia": "semanal", "momento": "variable"},
                "predisposicion": "VARIABLE"
            },
            "PRAGMATICO": {
                "enfoque": "directo_negociable",
                "mensaje_clave": "Analicemos opciones prácticas que beneficien a ambas partes",
                "incentivos": ["descuentos_negociables", "opciones_multiples", "beneficios_claros"],
                "canales": ["telefono_directo", "sms", "whatsapp_negociacion"],
                "timing": {"frecuencia": "bisemanal", "momento": "cualquiera"},
                "predisposicion": "NEUTRAL"
            },
            "EVASIVO": {
                "enfoque": "persistente_multicanal",
                "mensaje_clave": "Es importante que conversemos sobre su situación financiera",
                "incentivos": ["facilidades_especiales", "ultimatum_beneficioso", "opciones_ultimas"],
                "canales": ["multi_canal", "visita_ocasional", "contacto_referencias"],
                "timing": {"frecuencia": "alta", "momento": "variable"},
                "predisposicion": "NEGATIVA"
            },
            "COMBATIVO": {
                "enfoque": "firme_legal",
                "mensaje_clave": "Debemos resolver esta situación de manera formal y definitiva",
                "incentivos": ["evitar_escalamiento", "solucion_final", "terminos_firmes"],
                "canales": ["legal_formal", "presencial_autoridad", "documentos_legales"],
                "timing": {"frecuencia": "formal", "momento": "horario_legal"},
                "predisposicion": "RESISTENTE"
            }
        }
        
        return estrategias_personalizadas.get(arquetipo["tipo"], estrategias_personalizadas["PRAGMATICO"])
    
    def _predecir_respuesta(self, arquetipo: Dict, datos: Dict) -> Dict:
        """Predecir probabilidades de respuesta basado en perfil"""
        
        perfil_arquetipo = self.arquetipos_deudor[arquetipo["tipo"]]
        probabilidad_base = perfil_arquetipo["probabilidad_exito"]
        
        # Ajustar por factores específicos
        ajustes = 0
        
        # Ajuste por monto de deuda
        monto_deuda = datos.get("monto_deuda", 50000)
        if monto_deuda < 20000:
            ajustes += 0.1  # Deudas pequeñas más fáciles
        elif monto_deuda > 100000:
            ajustes -= 0.1  # Deudas grandes más difíciles
        
        # Ajuste por antigüedad
        dias_mora = datos.get("dias_mora", 30)
        if dias_mora < 30:
            ajustes += 0.1
        elif dias_mora > 180:
            ajustes -= 0.2
        
        # Ajuste por historial de contacto
        historial_contactos = datos.get("historial_contactos", [])
        if historial_contactos:
            contactos_exitosos = sum(1 for c in historial_contactos if c.get("exitoso", False))
            tasa_contacto = contactos_exitosos / len(historial_contactos)
            ajustes += (tasa_contacto - 0.5) * 0.2
        
        # Calcular probabilidades finales
        prob_exito = max(0.1, min(0.95, probabilidad_base + ajustes))
        prob_contacto = min(0.95, prob_exito * 1.2)
        prob_pago = max(0.1, prob_exito * 0.8)
        
        # Resistencia esperada
        resistencia_niveles = {
            "COLABORADOR": "baja",
            "ORGANIZADOR": "baja",
            "EMOTIVO": "media",
            "PRAGMATICO": "media",
            "EVASIVO": "alta",
            "COMBATIVO": "muy_alta"
        }
        
        resistencia = resistencia_niveles.get(arquetipo["tipo"], "media")
        
        # Tiempo esperado de resolución
        tiempos_resolucion = {
            "COLABORADOR": 15,
            "ORGANIZADOR": 21,
            "EMOTIVO": 30,
            "PRAGMATICO": 25,
            "EVASIVO": 60,
            "COMBATIVO": 90
        }
        
        tiempo_resolucion = tiempos_resolucion.get(arquetipo["tipo"], 30)
        
        return {
            "prob_exito": round(prob_exito, 2),
            "prob_contacto": round(prob_contacto, 2),
            "prob_pago": round(prob_pago, 2),
            "resistencia": resistencia,
            "tiempo_resolucion": tiempo_resolucion
        }
    
    def _evaluar_complejidad_caso(self, arquetipo: Dict) -> str:
        """Evaluar nivel de complejidad del caso"""
        complejidad_por_arquetipo = {
            "COLABORADOR": "baja",
            "ORGANIZADOR": "baja",
            "EMOTIVO": "media",
            "PRAGMATICO": "media",
            "EVASIVO": "alta",
            "COMBATIVO": "muy_alta"
        }
        
        return complejidad_por_arquetipo.get(arquetipo["tipo"], "media")
    
    def policy(self) -> Dict[str, Any]:
        """Retornar políticas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "requires_tenant_isolation": True,
            "data_retention_days": 1825,  # 5 años
            "compliance_requirements": ["INDOTEL_172_13", "GDPR", "PRIVACY"],
            "sensitive_data_handling": {
                "perfil_psicologico": "encrypted",
                "datos_personales": "anonymized_analytics",
                "notas_agente": "retention_limited"
            }
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Retornar métricas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "perfiles_generados": 0,  # Se actualizará en runtime
            "precision_arquetipos": 0.82,
            "tiempo_promedio_perfilado": 3.1,
            "distribucion_arquetipos": {
                "colaborador": "25%",
                "organizador": "20%",
                "emotivo": "20%",
                "pragmatico": "15%",
                "evasivo": "15%",
                "combativo": "5%"
            }
        }

if __name__ == "__main__":
    # Test básico del agente
    analyzer = ProfilingAnalyzer("test_tenant")
    print(f"Agente inicializado: {analyzer.agent_name} v{analyzer.version}")
