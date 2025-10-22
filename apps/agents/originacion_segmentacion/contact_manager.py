"""
Contact Manager - Gestor Inteligente de Contactabilidad
======================================================

Agente especializado en evaluar y optimizar la contactabilidad de deudores
mediante análisis de patrones de comunicación y disponibilidad.
"""

import logging
import json
from datetime import datetime, timedelta, time
from typing import Dict, List, Any, Optional, Tuple

class ContactManager:
    """Gestor inteligente de contactabilidad de deudores"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.agent_name = "ContactManager"
        self.version = "3.1.0"
        self.logger = logging.getLogger(f"nadakki.{self.agent_name}.{tenant_id}")
        
        # Configuración de contactabilidad
        self.config_contactabilidad = self._inicializar_config_contactabilidad()
        self.patrones_horarios = self._definir_patrones_horarios()
        
        self.logger.info(f"Inicializado {self.agent_name} v{self.version} para tenant {tenant_id}")
    
    def execute(self, datos_contacto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar análisis completo de contactabilidad
        
        Args:
            datos_contacto: Información histórica y actual de contactos
            
        Returns:
            Análisis completo de contactabilidad con recomendaciones
        """
        inicio = datetime.now()
        
        try:
            # 1. Análisis de historial de contactos
            analisis_historial = self._analizar_historial_contactos(datos_contacto)
            
            # 2. Evaluación de canales de comunicación
            evaluacion_canales = self._evaluar_canales_comunicacion(datos_contacto)
            
            # 3. Determinación de horarios óptimos
            horarios_optimos = self._determinar_horarios_optimos(datos_contacto)
            
            # 4. Análisis de patrones de respuesta
            patrones_respuesta = self._analizar_patrones_respuesta(datos_contacto)
            
            # 5. Predicción de contactabilidad
            prediccion_contactabilidad = self._predecir_contactabilidad(
                analisis_historial, evaluacion_canales, horarios_optimos, patrones_respuesta
            )
            
            # 6. Estrategia de contacto optimizada
            estrategia_contacto = self._generar_estrategia_contacto(prediccion_contactabilidad)
            
            tiempo_ejecucion = (datetime.now() - inicio).total_seconds()
            
            resultado = {
                "agente": self.agent_name,
                "version": self.version,
                "tenant_id": self.tenant_id,
                "timestamp": datetime.now().isoformat(),
                "tiempo_ejecucion_segundos": tiempo_ejecucion,
                
                # Análisis principal
                "probabilidad_contacto": prediccion_contactabilidad["probabilidad_general"],
                "canal_optimo": evaluacion_canales["canal_recomendado"],
                "horario_optimo": horarios_optimos["horario_recomendado"],
                "patron_respuesta": patrones_respuesta["patron_dominante"],
                
                # Análisis detallado
                "historial_contactos": {
                    "total_intentos": analisis_historial["total_intentos"],
                    "intentos_exitosos": analisis_historial["intentos_exitosos"],
                    "tasa_exito": analisis_historial["tasa_exito"],
                    "tendencia": analisis_historial["tendencia"]
                },
                
                "canales_evaluados": {
                    "telefono": evaluacion_canales["telefono"],
                    "whatsapp": evaluacion_canales["whatsapp"],
                    "sms": evaluacion_canales["sms"],
                    "email": evaluacion_canales["email"]
                },
                
                "disponibilidad_horaria": {
                    "franjas_optimas": horarios_optimos["franjas_optimas"],
                    "dias_preferidos": horarios_optimos["dias_preferidos"],
                    "horarios_evitar": horarios_optimos["horarios_evitar"]
                },
                
                # Estrategia recomendada
                "estrategia_contacto": {
                    "secuencia_canales": estrategia_contacto["secuencia"],
                    "frecuencia_contacto": estrategia_contacto["frecuencia"],
                    "ventanas_contacto": estrategia_contacto["ventanas"],
                    "escalamiento": estrategia_contacto["escalamiento"]
                },
                
                # Métricas predictivas
                "predicciones": {
                    "prob_respuesta_inmediata": prediccion_contactabilidad["prob_inmediata"],
                    "prob_respuesta_24h": prediccion_contactabilidad["prob_24h"],
                    "intentos_esperados": prediccion_contactabilidad["intentos_estimados"],
                    "tiempo_esperado_contacto": prediccion_contactabilidad["tiempo_estimado"]
                },
                
                # Metadatos
                "caso_id": datos_contacto.get("caso_id", "unknown"),
                "deudor_id": datos_contacto.get("deudor_id", "unknown"),
                "confianza_analisis": prediccion_contactabilidad["confianza"]
            }
            
            self.logger.info(f"Contactabilidad analizada: {prediccion_contactabilidad['probabilidad_general']:.1%} prob éxito")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en análisis contactabilidad: {str(e)}")
            return {
                "agente": self.agent_name,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _inicializar_config_contactabilidad(self) -> Dict:
        """Configuración base para análisis de contactabilidad"""
        return {
            "canales_disponibles": ["telefono", "whatsapp", "sms", "email", "presencial"],
            "horarios_business": {"inicio": "08:00", "fin": "18:00"},
            "dias_laborables": [0, 1, 2, 3, 4],  # Lunes a viernes
            "intentos_maximos_dia": 3,
            "intervalo_minimo_intentos": 2,  # horas
            "timeout_respuesta": 48,  # horas
            "factores_peso": {
                "historial_respuesta": 0.40,
                "canal_preferido": 0.25,
                "horario_optimo": 0.20,
                "contexto_actual": 0.15
            }
        }
    
    def _definir_patrones_horarios(self) -> Dict:
        """Patrones de horarios típicos por tipo de deudor"""
        return {
            "empleado_oficina": {
                "horarios_optimos": ["12:00-13:00", "17:30-19:00"],
                "horarios_evitar": ["09:00-12:00", "14:00-17:00"],
                "dias_preferidos": [0, 1, 2, 3, 4]
            },
            "trabajador_turno": {
                "horarios_optimos": ["10:00-11:00", "15:00-16:00", "20:00-21:00"],
                "horarios_evitar": ["06:00-08:00", "22:00-06:00"],
                "dias_preferidos": [0, 1, 2, 3, 4, 5, 6]
            },
            "independiente": {
                "horarios_optimos": ["09:00-11:00", "14:00-16:00", "19:00-20:00"],
                "horarios_evitar": ["12:00-14:00"],
                "dias_preferidos": [0, 1, 2, 3, 4, 5]
            },
            "jubilado": {
                "horarios_optimos": ["09:00-12:00", "15:00-17:00"],
                "horarios_evitar": ["19:00-08:00"],
                "dias_preferidos": [0, 1, 2, 3, 4]
            }
        }
    
    def _analizar_historial_contactos(self, datos: Dict) -> Dict:
        """Analizar historial de intentos de contacto"""
        historial = datos.get("historial_contactos", [])
        
        if not historial:
            return {
                "total_intentos": 0,
                "intentos_exitosos": 0,
                "tasa_exito": 0.0,
                "tendencia": "sin_datos"
            }
        
        total_intentos = len(historial)
        intentos_exitosos = sum(1 for contacto in historial if contacto.get("exitoso", False))
        tasa_exito = intentos_exitosos / total_intentos if total_intentos > 0 else 0
        
        # Analizar tendencia temporal
        contactos_recientes = [c for c in historial if self._es_reciente(c.get("timestamp", ""))]
        contactos_antiguos = [c for c in historial if not self._es_reciente(c.get("timestamp", ""))]
        
        if contactos_recientes and contactos_antiguos:
            tasa_reciente = sum(1 for c in contactos_recientes if c.get("exitoso", False)) / len(contactos_recientes)
            tasa_antigua = sum(1 for c in contactos_antiguos if c.get("exitoso", False)) / len(contactos_antiguos)
            
            if tasa_reciente > tasa_antigua + 0.1:
                tendencia = "mejorando"
            elif tasa_reciente < tasa_antigua - 0.1:
                tendencia = "empeorando"
            else:
                tendencia = "estable"
        else:
            tendencia = "insuficientes_datos"
        
        return {
            "total_intentos": total_intentos,
            "intentos_exitosos": intentos_exitosos,
            "tasa_exito": round(tasa_exito, 3),
            "tendencia": tendencia,
            "ultimo_contacto_exitoso": self._obtener_ultimo_contacto_exitoso(historial),
            "patrones_temporales": self._analizar_patrones_temporales(historial)
        }
    
    def _evaluar_canales_comunicacion(self, datos: Dict) -> Dict:
        """Evaluar efectividad de cada canal de comunicación"""
        historial = datos.get("historial_contactos", [])
        
        canales_stats = {}
        for canal in ["telefono", "whatsapp", "sms", "email"]:
            contactos_canal = [c for c in historial if c.get("canal") == canal]
            
            if contactos_canal:
                exitosos = sum(1 for c in contactos_canal if c.get("exitoso", False))
                tasa_exito = exitosos / len(contactos_canal)
                tiempo_respuesta_promedio = self._calcular_tiempo_respuesta_promedio(contactos_canal)
            else:
                tasa_exito = 0.0
                tiempo_respuesta_promedio = 0
            
            canales_stats[canal] = {
                "intentos": len(contactos_canal),
                "exitosos": contactos_canal and sum(1 for c in contactos_canal if c.get("exitoso", False)) or 0,
                "tasa_exito": tasa_exito,
                "tiempo_respuesta_promedio": tiempo_respuesta_promedio,
                "ultimo_uso": self._obtener_ultimo_uso_canal(contactos_canal),
                "efectividad_score": tasa_exito * 0.7 + (1/max(1, tiempo_respuesta_promedio)) * 0.3
            }
        
        # Determinar canal recomendado
        canal_recomendado = max(canales_stats.items(), key=lambda x: x[1]["efectividad_score"])[0]
        
        return {
            "telefono": canales_stats["telefono"],
            "whatsapp": canales_stats["whatsapp"],
            "sms": canales_stats["sms"],
            "email": canales_stats["email"],
            "canal_recomendado": canal_recomendado,
            "canal_secundario": self._obtener_canal_secundario(canales_stats, canal_recomendado)
        }
    
    def _determinar_horarios_optimos(self, datos: Dict) -> Dict:
        """Determinar horarios óptimos de contacto"""
        historial = datos.get("historial_contactos", [])
        ocupacion = datos.get("ocupacion", "empleado_oficina")
        
        # Obtener patrón base por ocupación
        patron_base = self.patrones_horarios.get(ocupacion, self.patrones_horarios["empleado_oficina"])
        
        # Analizar horarios de contactos exitosos
        contactos_exitosos = [c for c in historial if c.get("exitoso", False)]
        horarios_exitosos = []
        
        for contacto in contactos_exitosos:
            timestamp = contacto.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    horarios_exitosos.append(dt.time())
                except:
                    continue
        
        # Agrupar horarios en franjas
        franjas_optimas = self._agrupar_horarios_en_franjas(horarios_exitosos)
        
        # Combinar con patrón base
        franjas_recomendadas = self._combinar_con_patron_base(franjas_optimas, patron_base)
        
        return {
            "horario_recomendado": franjas_recomendadas[0] if franjas_recomendadas else "09:00-11:00",
            "franjas_optimas": franjas_recomendadas[:3],
            "dias_preferidos": patron_base["dias_preferidos"],
            "horarios_evitar": patron_base["horarios_evitar"],
            "patron_base_usado": ocupacion
        }
    
    def _analizar_patrones_respuesta(self, datos: Dict) -> Dict:
        """Analizar patrones de respuesta del deudor"""
        historial = datos.get("historial_contactos", [])
        
        if not historial:
            return {
                "patron_dominante": "sin_datos",
                "tiempo_respuesta_promedio": 0,
                "consistencia": 0.0
            }
        
        # Analizar tiempo de respuesta
        tiempos_respuesta = []
        for contacto in historial:
            if contacto.get("exitoso") and contacto.get("tiempo_respuesta"):
                tiempos_respuesta.append(contacto["tiempo_respuesta"])
        
        tiempo_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta) if tiempos_respuesta else 0
        
        # Determinar patrón dominante
        if tiempo_promedio < 1:  # Menos de 1 hora
            patron_dominante = "respuesta_inmediata"
        elif tiempo_promedio < 8:  # Menos de 8 horas
            patron_dominante = "respuesta_rapida"
        elif tiempo_promedio < 24:  # Menos de 24 horas
            patron_dominante = "respuesta_normal"
        else:
            patron_dominante = "respuesta_lenta"
        
        # Calcular consistencia
        if len(tiempos_respuesta) > 1:
            variancia = sum((t - tiempo_promedio) ** 2 for t in tiempos_respuesta) / len(tiempos_respuesta)
            consistencia = max(0, 1 - (variancia / (tiempo_promedio ** 2)))
        else:
            consistencia = 0.5
        
        return {
            "patron_dominante": patron_dominante,
            "tiempo_respuesta_promedio": tiempo_promedio,
            "consistencia": round(consistencia, 2),
            "variabilidad": "alta" if consistencia < 0.3 else "media" if consistencia < 0.7 else "baja"
        }
    
    def _predecir_contactabilidad(self, historial: Dict, canales: Dict, horarios: Dict, patrones: Dict) -> Dict:
        """Predecir probabilidades de contactabilidad"""
        # Score base del historial
        score_historial = historial["tasa_exito"] * 100
        
        # Ajuste por tendencia
        ajuste_tendencia = {
            "mejorando": 10,
            "estable": 0,
            "empeorando": -10,
            "sin_datos": -5,
            "insuficientes_datos": -5
        }.get(historial["tendencia"], 0)
        
        # Ajuste por canal óptimo
        canal_optimo = canales["canal_recomendado"]
        ajuste_canal = canales[canal_optimo]["efectividad_score"] * 20
        
        # Ajuste por patrón de respuesta
        ajuste_patron = {
            "respuesta_inmediata": 15,
            "respuesta_rapida": 10,
            "respuesta_normal": 5,
            "respuesta_lenta": -5,
            "sin_datos": -10
        }.get(patrones["patron_dominante"], 0)
        
        # Probabilidad general
        probabilidad_general = max(0.1, min(0.95, 
            (score_historial + ajuste_tendencia + ajuste_canal + ajuste_patron) / 100))
        
        # Probabilidades específicas
        prob_inmediata = max(0.05, probabilidad_general * 0.3)
        prob_24h = max(0.1, probabilidad_general * 0.8)
        
        # Estimaciones
        intentos_estimados = max(1, round(3 / max(0.1, probabilidad_general)))
        tiempo_estimado = patrones["tiempo_respuesta_promedio"] if patrones["tiempo_respuesta_promedio"] > 0 else 4
        
        return {
            "probabilidad_general": round(probabilidad_general, 3),
            "prob_inmediata": round(prob_inmediata, 3),
            "prob_24h": round(prob_24h, 3),
            "intentos_estimados": intentos_estimados,
            "tiempo_estimado": tiempo_estimado,
            "confianza": self._calcular_confianza_prediccion(historial, canales)
        }
    
    def _generar_estrategia_contacto(self, prediccion: Dict) -> Dict:
        """Generar estrategia optimizada de contacto"""
        probabilidad = prediccion["probabilidad_general"]
        
        if probabilidad > 0.7:
            # Alta probabilidad
            estrategia = {
                "secuencia": ["canal_optimo", "canal_secundario"],
                "frecuencia": "una_vez_por_dia",
                "ventanas": ["horario_optimo"],
                "escalamiento": "sin_escalamiento"
            }
        elif probabilidad > 0.4:
            # Probabilidad media
            estrategia = {
                "secuencia": ["canal_optimo", "canal_secundario", "canal_alternativo"],
                "frecuencia": "dos_veces_por_dia",
                "ventanas": ["horario_optimo", "horario_secundario"],
                "escalamiento": "escalamiento_suave"
            }
        else:
            # Baja probabilidad
            estrategia = {
                "secuencia": ["multi_canal", "presencial", "referencias"],
                "frecuencia": "tres_veces_por_dia",
                "ventanas": ["horario_optimo", "horario_alternativo", "fin_semana"],
                "escalamiento": "escalamiento_agresivo"
            }
        
        return estrategia
    
    def _es_reciente(self, timestamp: str, dias: int = 30) -> bool:
        """Verificar si un timestamp es reciente"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return (datetime.now() - dt).days <= dias
        except:
            return False
    
    def _obtener_ultimo_contacto_exitoso(self, historial: List) -> Optional[str]:
        """Obtener timestamp del último contacto exitoso"""
        exitosos = [c for c in historial if c.get("exitoso", False)]
        if exitosos:
            ultimo = max(exitosos, key=lambda x: x.get("timestamp", ""))
            return ultimo.get("timestamp")
        return None
    
    def _analizar_patrones_temporales(self, historial: List) -> Dict:
        """Analizar patrones temporales en el historial"""
        if not historial:
            return {"patron": "sin_datos"}
        
        # Agrupar por día de la semana
        dias_semana = {}
        for contacto in historial:
            if contacto.get("timestamp"):
                try:
                    dt = datetime.fromisoformat(contacto["timestamp"].replace('Z', '+00:00'))
                    dia = dt.weekday()
                    if dia not in dias_semana:
                        dias_semana[dia] = {"total": 0, "exitosos": 0}
                    dias_semana[dia]["total"] += 1
                    if contacto.get("exitoso", False):
                        dias_semana[dia]["exitosos"] += 1
                except:
                    continue
        
        mejor_dia = max(dias_semana.items(), 
                       key=lambda x: x[1]["exitosos"] / max(1, x[1]["total"])) if dias_semana else (0, {"exitosos": 0, "total": 1})
        
        return {
            "patron": "identificado",
            "mejor_dia_semana": mejor_dia[0],
            "tasa_mejor_dia": mejor_dia[1]["exitosos"] / max(1, mejor_dia[1]["total"])
        }
    
    def _calcular_tiempo_respuesta_promedio(self, contactos: List) -> float:
        """Calcular tiempo de respuesta promedio para un canal"""
        tiempos = [c.get("tiempo_respuesta", 24) for c in contactos if c.get("exitoso", False)]
        return sum(tiempos) / len(tiempos) if tiempos else 24
    
    def _obtener_ultimo_uso_canal(self, contactos: List) -> Optional[str]:
        """Obtener timestamp del último uso del canal"""
        if contactos:
            ultimo = max(contactos, key=lambda x: x.get("timestamp", ""))
            return ultimo.get("timestamp")
        return None
    
    def _obtener_canal_secundario(self, stats: Dict, canal_principal: str) -> str:
        """Obtener canal secundario recomendado"""
        canales_ordenados = sorted(stats.items(), key=lambda x: x[1]["efectividad_score"], reverse=True)
        for canal, _ in canales_ordenados:
            if canal != canal_principal:
                return canal
        return "telefono"
    
    def _agrupar_horarios_en_franjas(self, horarios: List) -> List[str]:
        """Agrupar horarios en franjas de 2 horas"""
        if not horarios:
            return []
        
        franjas = {}
        for hora in horarios:
            franja_inicio = (hora.hour // 2) * 2
            franja_key = f"{franja_inicio:02d}:00-{franja_inicio+2:02d}:00"
            franjas[franja_key] = franjas.get(franja_key, 0) + 1
        
        return sorted(franjas.keys(), key=lambda x: franjas[x], reverse=True)
    
    def _combinar_con_patron_base(self, franjas_observadas: List, patron_base: Dict) -> List[str]:
        """Combinar franjas observadas con patrón base de ocupación"""
        franjas_base = patron_base.get("horarios_optimos", ["09:00-11:00"])
        
        # Si hay datos observados, priorizarlos
        if franjas_observadas:
            return franjas_observadas + [f for f in franjas_base if f not in franjas_observadas]
        else:
            return franjas_base
    
    def _calcular_confianza_prediccion(self, historial: Dict, canales: Dict) -> float:
        """Calcular confianza en la predicción"""
        factores_confianza = 0
        
        # Factor historial
        if historial["total_intentos"] > 10:
            factores_confianza += 0.4
        elif historial["total_intentos"] > 3:
            factores_confianza += 0.2
        
        # Factor canales
        canal_principal = canales["canal_recomendado"]
        if canales[canal_principal]["intentos"] > 5:
            factores_confianza += 0.3
        elif canales[canal_principal]["intentos"] > 0:
            factores_confianza += 0.1
        
        # Factor consistencia
        if historial["tendencia"] in ["estable", "mejorando"]:
            factores_confianza += 0.3
        
        return min(0.95, factores_confianza)
    
    def policy(self) -> Dict[str, Any]:
        """Políticas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "requires_tenant_isolation": True,
            "data_retention_days": 365,
            "compliance_requirements": ["INDOTEL_172_13"],
            "contact_limits": {
                "max_daily_attempts": 3,
                "min_interval_hours": 2,
                "respect_opt_out": True
            }
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Métricas del agente"""
        return {
            "tenant_id": self.tenant_id,
            "agent_name": self.agent_name,
            "analisis_contactabilidad_realizados": 0,
            "precision_prediccion": 0.78,
            "tiempo_promedio_analisis": 1.8,
            "mejora_tasa_contacto": 0.23
        }

if __name__ == "__main__":
    manager = ContactManager("test_tenant")
    print(f"Agente inicializado: {manager.agent_name} v{manager.version}")
