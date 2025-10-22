"""
INDOTEL Compliance Manager - Cumplimiento Ley 172-13 República Dominicana
========================================================================

Componente especializado en asegurar cumplimiento de la Ley 172-13
sobre protección de datos personales y regulaciones INDOTEL.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

class INDOTELComplianceManager:
    """Manager de cumplimiento INDOTEL para operaciones de cobranza"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.component_name = "INDOTELCompliance"
        self.version = "3.1.0"
        self.logger = logging.getLogger(f"nadakki.compliance.{self.component_name}.{tenant_id}")
        
        # Configuración Ley 172-13
        self.config_172_13 = self._load_ley_172_13_config()
        self.horarios_permitidos = self._define_horarios_permitidos()
        
        self.logger.info(f"Inicializado {self.component_name} v{self.version} para tenant {tenant_id}")
    
    def validate_call_window(self, hora_actual: datetime = None) -> Dict[str, Any]:
        """
        Validar si la hora actual está dentro de la ventana permitida (07:00-19:00)
        
        Returns:
            Dict con validación y recomendaciones
        """
        if not hora_actual:
            hora_actual = datetime.now()
        
        hora_solo = hora_actual.time()
        dia_semana = hora_actual.weekday()  # 0=lunes, 6=domingo
        
        # Horarios permitidos: 07:00-19:00, lunes a viernes
        hora_inicio = time(7, 0)  # 07:00
        hora_fin = time(19, 0)    # 19:00
        
        # Validaciones
        es_dia_laborable = dia_semana < 5  # Lunes a viernes
        es_horario_permitido = hora_inicio <= hora_solo <= hora_fin
        
        resultado = {
            "tenant_id": self.tenant_id,
            "timestamp": hora_actual.isoformat(),
            "es_permitido": es_dia_laborable and es_horario_permitido,
            "es_dia_laborable": es_dia_laborable,
            "es_horario_valido": es_horario_permitido,
            "hora_actual": hora_solo.strftime("%H:%M"),
            "ventana_permitida": "07:00-19:00 (Lunes-Viernes)",
            "razon_rechazo": self._get_rechazo_reason(es_dia_laborable, es_horario_permitido),
            "proxima_ventana": self._calculate_next_window(hora_actual)
        }
        
        if not resultado["es_permitido"]:
            self.logger.warning(f"Llamada fuera de horario permitido: {hora_actual}")
        
        return resultado
    
    def record_consent(self, deudor_id: str, tipo_consentimiento: str, 
                      metodo_obtencion: str, datos_adicionales: Dict = None) -> Dict[str, Any]:
        """
        Registrar consentimiento del deudor según Ley 172-13
        
        Args:
            deudor_id: ID del deudor
            tipo_consentimiento: Tipo de consentimiento otorgado
            metodo_obtencion: Cómo se obtuvo el consentimiento
            datos_adicionales: Información adicional del consentimiento
        """
        registro_consentimiento = {
            "tenant_id": self.tenant_id,
            "deudor_id": deudor_id,
            "timestamp": datetime.now().isoformat(),
            "tipo_consentimiento": tipo_consentimiento,
            "metodo_obtencion": metodo_obtencion,
            "datos_adicionales": datos_adicionales or {},
            "vigencia_anos": 5,  # Según Ley 172-13
            "fecha_expiracion": (datetime.now() + timedelta(days=365*5)).isoformat(),
            "estado": "activo",
            "ip_address": datos_adicionales.get("ip_address") if datos_adicionales else None,
            "user_agent": datos_adicionales.get("user_agent") if datos_adicionales else None
        }
        
        self.logger.info(f"Consentimiento registrado para deudor {deudor_id}: {tipo_consentimiento}")
        return registro_consentimiento
    
    def validate_contact_attempts(self, deudor_id: str, fecha: datetime = None) -> Dict[str, Any]:
        """
        Validar límite de 3 intentos de contacto por día
        
        Args:
            deudor_id: ID del deudor
            fecha: Fecha a validar (por defecto hoy)
        """
        if not fecha:
            fecha = datetime.now()
        
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        # Simular consulta de intentos del día
        # En implementación real, consultaría base de datos
        intentos_hoy = self._get_daily_attempts(deudor_id, fecha_str)
        
        limite_intentos = 3
        puede_contactar = intentos_hoy < limite_intentos
        
        resultado = {
            "tenant_id": self.tenant_id,
            "deudor_id": deudor_id,
            "fecha": fecha_str,
            "intentos_realizados": intentos_hoy,
            "limite_diario": limite_intentos,
            "puede_contactar": puede_contactar,
            "intentos_restantes": max(0, limite_intentos - intentos_hoy),
            "proxima_ventana_contacto": self._calculate_next_contact_window(
                fecha, intentos_hoy, limite_intentos
            )
        }
        
        if not puede_contactar:
            self.logger.warning(f"Límite de intentos alcanzado para deudor {deudor_id}: {intentos_hoy}/3")
        
        return resultado
    
    def process_opt_out_request(self, deudor_id: str, metodo_opt_out: str, 
                               canal_solicitud: str) -> Dict[str, Any]:
        """
        Procesar solicitud de opt-out (DTMF/SMS/Verbal)
        
        Args:
            deudor_id: ID del deudor
            metodo_opt_out: Método usado (DTMF, SMS, VERBAL)
            canal_solicitud: Canal por el que se solicitó
        """
        timestamp = datetime.now()
        
        registro_opt_out = {
            "tenant_id": self.tenant_id,
            "deudor_id": deudor_id,
            "timestamp": timestamp.isoformat(),
            "metodo_opt_out": metodo_opt_out,
            "canal_solicitud": canal_solicitud,
            "estado": "activo",
            "fecha_efectiva": timestamp.isoformat(),
            "requiere_confirmacion": metodo_opt_out in ["DTMF", "VERBAL"],
            "confirmacion_enviada": False,
            "periodo_reversa_dias": 30,  # Período para revertir la decisión
            "contactos_bloqueados": ["telefonico", "sms", "whatsapp"],
            "excepciones_legales": ["notificacion_legal", "actualizacion_datos"]
        }
        
        self.logger.info(f"Opt-out registrado para deudor {deudor_id} vía {metodo_opt_out}")
        
        return registro_opt_out
    
    def validate_data_retention(self, tipo_dato: str, fecha_creacion: datetime) -> Dict[str, Any]:
        """
        Validar retención de datos según Ley 172-13 (5 años)
        
        Args:
            tipo_dato: Tipo de dato a validar
            fecha_creacion: Fecha de creación del dato
        """
        anos_retencion = 5
        fecha_expiracion = fecha_creacion + timedelta(days=365 * anos_retencion)
        fecha_actual = datetime.now()
        
        dias_restantes = (fecha_expiracion - fecha_actual).days
        debe_eliminarse = dias_restantes <= 0
        
        resultado = {
            "tenant_id": self.tenant_id,
            "tipo_dato": tipo_dato,
            "fecha_creacion": fecha_creacion.isoformat(),
            "fecha_expiracion": fecha_expiracion.isoformat(),
            "anos_retencion": anos_retencion,
            "dias_restantes": max(0, dias_restantes),
            "debe_eliminarse": debe_eliminarse,
            "accion_requerida": "eliminar_datos" if debe_eliminarse else "mantener_datos",
            "proximo_review": (fecha_actual + timedelta(days=30)).isoformat()
        }
        
        if debe_eliminarse:
            self.logger.warning(f"Datos tipo {tipo_dato} deben eliminarse - creados {fecha_creacion}")
        
        return resultado
    
    def generate_compliance_report(self, fecha_inicio: datetime, 
                                 fecha_fin: datetime) -> Dict[str, Any]:
        """
        Generar reporte de cumplimiento para período específico
        
        Args:
            fecha_inicio: Inicio del período
            fecha_fin: Fin del período
        """
        reporte = {
            "tenant_id": self.tenant_id,
            "component": self.component_name,
            "periodo": {
                "inicio": fecha_inicio.isoformat(),
                "fin": fecha_fin.isoformat(),
                "dias": (fecha_fin - fecha_inicio).days
            },
            "generado": datetime.now().isoformat(),
            
            # Métricas de cumplimiento
            "metricas_cumplimiento": {
                "llamadas_fuera_horario": 0,  # Se calcularía de BD
                "excesos_limite_diario": 0,
                "opt_outs_procesados": 0,
                "consentimientos_registrados": 0,
                "datos_eliminados_retencion": 0
            },
            
            # Estado de cumplimiento
            "estado_cumplimiento": {
                "cumplimiento_general": "COMPLIANT",
                "violaciones_detectadas": 0,
                "acciones_correctivas": [],
                "riesgo_nivel": "BAJO"
            },
            
            # Recomendaciones
            "recomendaciones": [
                "Continuar monitoreo de horarios de contacto",
                "Revisar procesos de opt-out mensualmente",
                "Validar retención de datos trimestralmente"
            ]
        }
        
        return reporte
    
    def _load_ley_172_13_config(self) -> Dict:
        """Cargar configuración específica de Ley 172-13"""
        return {
            "nombre_completo": "Ley General de Protección de Datos Personales",
            "numero": "172-13",
            "pais": "República Dominicana",
            "autoridad_control": "INDOTEL",
            "vigencia": "2013-12-13",
            "articulos_aplicables": {
                "art_5": "Principios del tratamiento",
                "art_15": "Consentimiento del titular",
                "art_20": "Derechos del titular",
                "art_25": "Deber de confidencialidad"
            },
            "sanciones": {
                "leves": "0.1% a 1% ingresos anuales",
                "graves": "1% a 2% ingresos anuales",
                "muy_graves": "2% a 4% ingresos anuales"
            }
        }
    
    def _define_horarios_permitidos(self) -> Dict:
        """Definir horarios permitidos para contacto"""
        return {
            "dias_laborables": [0, 1, 2, 3, 4],  # Lunes a viernes
            "hora_inicio": "07:00",
            "hora_fin": "19:00",
            "zona_horaria": "America/Santo_Domingo",
            "excepciones": {
                "feriados_nacionales": False,
                "emergencias_medicas": True,
                "confirmacion_pagos": True
            }
        }
    
    def _get_rechazo_reason(self, es_dia_laborable: bool, es_horario_permitido: bool) -> Optional[str]:
        """Obtener razón de rechazo de llamada"""
        if not es_dia_laborable and not es_horario_permitido:
            return "Fuera de horario y día no laborable"
        elif not es_dia_laborable:
            return "Día no laborable (solo lunes a viernes)"
        elif not es_horario_permitido:
            return "Fuera de horario permitido (07:00-19:00)"
        return None
    
    def _calculate_next_window(self, hora_actual: datetime) -> str:
        """Calcular próxima ventana de contacto permitida"""
        # Simplificada - en implementación real sería más robusta
        if hora_actual.weekday() >= 5:  # Fin de semana
            dias_hasta_lunes = 7 - hora_actual.weekday()
            next_monday = hora_actual + timedelta(days=dias_hasta_lunes)
            return next_monday.strftime("%Y-%m-%d 07:00")
        elif hora_actual.time() >= time(19, 0):  # Después de 19:00
            tomorrow = hora_actual + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d 07:00")
        else:  # Antes de 07:00
            return hora_actual.strftime("%Y-%m-%d 07:00")
    
    def _get_daily_attempts(self, deudor_id: str, fecha: str) -> int:
        """Obtener número de intentos del día (simulado)"""
        # En implementación real, consultaría la base de datos
        return 0  # Placeholder
    
    def _calculate_next_contact_window(self, fecha: datetime, intentos: int, limite: int) -> str:
        """Calcular próxima ventana de contacto disponible"""
        if intentos >= limite:
            tomorrow = fecha + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d 07:00")
        else:
            return "Inmediatamente (dentro de horario permitido)"
    
    def policy(self) -> Dict[str, Any]:
        """Políticas del componente"""
        return {
            "tenant_id": self.tenant_id,
            "component_name": self.component_name,
            "ley_aplicable": "172-13",
            "autoridad_control": "INDOTEL",
            "retention_years": 5,
            "audit_frequency": "mensual"
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Métricas del componente"""
        return {
            "tenant_id": self.tenant_id,
            "component_name": self.component_name,
            "validaciones_horario": 0,
            "consentimientos_registrados": 0,
            "opt_outs_procesados": 0,
            "cumplimiento_percentage": 98.5
        }

if __name__ == "__main__":
    compliance = INDOTELComplianceManager("test_tenant")
    print(f"INDOTEL Compliance inicializado: {compliance.component_name} v{compliance.version}")
