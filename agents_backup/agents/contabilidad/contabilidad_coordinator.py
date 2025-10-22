"""
ðŸ§® CONTABILIDAD COORDINATOR - NADAKKI AI SUITE
Coordinador principal para los 6 super agentes de contabilidad
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

# Importar super agentes
from .conciliacionbancaria import Conciliacionbancaria
from .auditoriainterna import Auditoriainterna
from .controlgastos import Controlgastos
from .reportes_fiscales import ReportesFiscales
from .analisis_financiero import AnalisisFinanciero
from .compliance_contable import ComplianceContable

class ContabilidadCoordinatorConfig:
    """ConfiguraciÃ³n del coordinador de contabilidad"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.enabled_agents = config_data.get("enabled_agents", [
            "conciliacion", "auditoria", "control_costos", 
            "reportes_fiscales", "analisis_financiero", "compliance_contable"
        ])
        self.auto_execution = config_data.get("auto_execution", True)
        self.reporting_frequency = config_data.get("reporting_frequency", "daily")
        self.integration_mode = config_data.get("integration_mode", "full")

class ContabilidadCoordinator:
    """
    ðŸ§® COORDINADOR PRINCIPAL DE CONTABILIDAD
    
    Gestiona 6 super agentes de contabilidad enterprise:
    1. Conciliacionbancaria - ConciliaciÃ³n automÃ¡tica
    2. Auditoriainterna - AuditorÃ­a predictiva 
    3. Controlgastos - OptimizaciÃ³n costos
    4. ReportesFiscales - DGII/DIAN/SAT automÃ¡tico
    5. AnalisisFinanciero - ML + 50 ratios + predicciones
    6. ComplianceContable - NIIF/GAAP + blockchain audit
    """
    
    def __init__(self, tenant_id: str, config_path: str = None):
        # Backward-compat: allow dict as first arg
        try:
            from typing import Mapping
            is_mapping = isinstance(tenant_id, dict) or (hasattr(tenant_id, 'keys') and hasattr(tenant_id, '__getitem__'))
        except Exception:
            is_mapping = isinstance(tenant_id, dict)

        if is_mapping:
            cfg = tenant_id
            tenant_id = cfg.get('tenant_id', 'demo')
            # Solo asignar config_path si no está provisto
            if config_path is None:
                config_path = cfg
        self.tenant_id = tenant_id
        self.logger = self._setup_logger()
        
        # Cargar configuraciÃ³n
        self.config = self._load_config(config_path)
        
        # Inicializar agentes
        self.agents = {}
        self._initialize_agents()
        
        # Estado del coordinador
        self.estado = "operational"
        self.ultimo_reporte = None
        
        self.logger.info(f"ContabilidadCoordinator inicializado para tenant {tenant_id}")
        self.logger.info(f"Agentes activos: {len(self.agents)}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup del logger"""
        logger = logging.getLogger(f"ContabilidadCoordinator-{self.tenant_id}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self, config_path: str = None) -> ContabilidadCoordinatorConfig:
        """Carga configuraciÃ³n del coordinador"""
        try:
            if config_path:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                # ConfiguraciÃ³n por defecto
                config_data = {
                    "enabled_agents": [
                        "conciliacion", "auditoria", "control_costos",
                        "reportes_fiscales", "analisis_financiero", "compliance_contable"
                    ],
                    "auto_execution": True,
                    "reporting_frequency": "daily",
                    "integration_mode": "full"
                }
            
            return ContabilidadCoordinatorConfig(config_data)
        except Exception as e:
            self.logger.error(f"Error cargando configuraciÃ³n: {e}")
            return ContabilidadCoordinatorConfig({})
    
    def _initialize_agents(self):
        """Inicializa todos los agentes disponibles"""
        try:
            # Agentes originales (ya implementados)
            if "conciliacion" in self.config.enabled_agents:
                self.agents["conciliacion"] = Conciliacionbancaria(self.tenant_id)
                self.logger.info("âœ… Conciliacionbancaria inicializada")
            
            if "auditoria" in self.config.enabled_agents:
                self.agents["auditoria"] = Auditoriainterna(self.tenant_id)
                self.logger.info("âœ… Auditoriainterna inicializada")
            
            if "control_costos" in self.config.enabled_agents:
                self.agents["control_costos"] = Controlgastos(self.tenant_id)
                self.logger.info("âœ… Controlgastos inicializado")
            
            # Nuevos super agentes enterprise
            if "reportes_fiscales" in self.config.enabled_agents:
                self.agents["reportes_fiscales"] = ReportesFiscales(self.tenant_id)
                self.logger.info("âœ… ReportesFiscales inicializado")
            
            if "analisis_financiero" in self.config.enabled_agents:
                self.agents["analisis_financiero"] = AnalisisFinanciero(self.tenant_id)
                self.logger.info("âœ… AnalisisFinanciero inicializado")
            
            if "compliance_contable" in self.config.enabled_agents:
                self.agents["compliance_contable"] = ComplianceContable(self.tenant_id)
                self.logger.info("âœ… ComplianceContable inicializado")
                
        except Exception as e:
            self.logger.error(f"Error inicializando agentes: {e}")
    
    async def ejecutar_proceso_completo_contabilidad(self) -> Dict[str, Any]:
        """Ejecuta proceso completo de todos los agentes de contabilidad"""
        inicio_tiempo = datetime.now()
        
        try:
            resultados = {
                "tenant_id": self.tenant_id,
                "fecha_ejecucion": inicio_tiempo.isoformat(),
                "agentes_ejecutados": {},
                "resumen_ejecutivo": {},
                "alertas_criticas": [],
                "recomendaciones": []
            }
            
            # 1. Ejecutar ReportesFiscales
            if "reportes_fiscales" in self.agents:
                self.logger.info("ðŸ›ï¸ Ejecutando ReportesFiscales...")
                try:
                    # Generar los 3 formularios principales
                    periodo_actual = datetime.now()
                    
                    reporte_606 = await self.agents["reportes_fiscales"].generar_reporte_606(periodo_actual)
                    reporte_607 = await self.agents["reportes_fiscales"].generar_reporte_607(periodo_actual)
                    reporte_608 = await self.agents["reportes_fiscales"].generar_reporte_608(periodo_actual)
                    calendario = await self.agents["reportes_fiscales"].obtener_calendario_fiscal()
                    
                    resultados["agentes_ejecutados"]["reportes_fiscales"] = {
                        "estado": "exitoso",
                        "formulario_606": reporte_606,
                        "formulario_607": reporte_607,
                        "formulario_608": reporte_608,
                        "calendario_fiscal": calendario
                    }
                    
                    # Alertas crÃ­ticas de vencimientos
                    if calendario["alertas_criticas"] > 0:
                        resultados["alertas_criticas"].append({
                            "agente": "ReportesFiscales",
                            "tipo": "vencimientos_criticos",
                            "cantidad": calendario["alertas_criticas"],
                            "accion": "Revisar calendario fiscal"
                        })
                        
                except Exception as e:
                    resultados["agentes_ejecutados"]["reportes_fiscales"] = {
                        "estado": "error",
                        "error": str(e)
                    }
            
            # 2. Ejecutar AnalisisFinanciero
            if "analisis_financiero" in self.agents:
                self.logger.info("ðŸ“Š Ejecutando AnalisisFinanciero...")
                try:
                    analisis_completo = await self.agents["analisis_financiero"].realizar_analisis_completo()
                    
                    resultados["agentes_ejecutados"]["analisis_financiero"] = {
                        "estado": "exitoso",
                        "analisis_completo": analisis_completo
                    }
                    
                    # Extraer alertas del anÃ¡lisis
                    if analisis_completo.get("alertas_criticas"):
                        resultados["alertas_criticas"].extend([
                            {
                                "agente": "AnalisisFinanciero",
                                "tipo": alerta["tipo"],
                                "descripcion": alerta["descripcion"],
                                "accion": alerta["accion_requerida"]
                            }
                            for alerta in analisis_completo["alertas_criticas"]
                        ])
                    
                    # Extraer recomendaciones
                    if analisis_completo.get("recomendaciones_estrategicas"):
                        resultados["recomendaciones"].extend(analisis_completo["recomendaciones_estrategicas"])
                        
                except Exception as e:
                    resultados["agentes_ejecutados"]["analisis_financiero"] = {
                        "estado": "error",
                        "error": str(e)
                    }
            
            # 3. Ejecutar ComplianceContable
            if "compliance_contable" in self.agents:
                self.logger.info("âš–ï¸ Ejecutando ComplianceContable...")
                try:
                    validacion_compliance = await self.agents["compliance_contable"].ejecutar_validacion_completa()
                    dashboard_compliance = await self.agents["compliance_contable"].obtener_dashboard_compliance()
                    
                    resultados["agentes_ejecutados"]["compliance_contable"] = {
                        "estado": "exitoso",
                        "validacion_compliance": validacion_compliance,
                        "dashboard": dashboard_compliance
                    }
                    
                    # Alertas de compliance
                    if validacion_compliance.get("alertas_generadas"):
                        resultados["alertas_criticas"].extend([
                            {
                                "agente": "ComplianceContable",
                                "tipo": alerta["tipo"],
                                "severidad": alerta["severidad"],
                                "descripcion": alerta["descripcion"],
                                "accion": alerta["accion_requerida"]
                            }
                            for alerta in validacion_compliance["alertas_generadas"]
                            if alerta["severidad"] in ["CRITICA", "ALTA"]
                        ])
                        
                except Exception as e:
                    resultados["agentes_ejecutados"]["compliance_contable"] = {
                        "estado": "error",
                        "error": str(e)
                    }
            
            # 4. Ejecutar agentes originales si estÃ¡n habilitados
            for agente_name in ["conciliacion", "auditoria", "control_costos"]:
                if agente_name in self.agents:
                    try:
                        self.logger.info(f"ðŸ”§ Ejecutando {agente_name}...")
                        status = self.agents[agente_name].get_status()
                        resultados["agentes_ejecutados"][agente_name] = {
                            "estado": "exitoso",
                            "status": status
                        }
                    except Exception as e:
                        resultados["agentes_ejecutados"][agente_name] = {
                            "estado": "error",
                            "error": str(e)
                        }
            
            # 5. Generar resumen ejecutivo
            tiempo_total = (datetime.now() - inicio_tiempo).total_seconds()
            
            resultados["resumen_ejecutivo"] = {
                "agentes_totales": len(self.agents),
                "agentes_exitosos": len([a for a in resultados["agentes_ejecutados"].values() if a["estado"] == "exitoso"]),
                "agentes_con_error": len([a for a in resultados["agentes_ejecutados"].values() if a["estado"] == "error"]),
                "alertas_criticas_total": len(resultados["alertas_criticas"]),
                "recomendaciones_total": len(resultados["recomendaciones"]),
                "tiempo_ejecucion_segundos": tiempo_total,
                "estado_general": "exitoso" if len(resultados["alertas_criticas"]) == 0 else "con_alertas"
            }
            
            self.ultimo_reporte = resultados
            
            self.logger.info(f"âœ… Proceso contabilidad completo en {tiempo_total:.2f}s")
            self.logger.info(f"ðŸ“Š {resultados['resumen_ejecutivo']['agentes_exitosos']}/{resultados['resumen_ejecutivo']['agentes_totales']} agentes exitosos")
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error en proceso completo contabilidad: {e}")
            raise
    
    def get_status_all_agents(self) -> Dict[str, Any]:
        """Obtiene status de todos los agentes"""
        
        status_agentes = {}
        
        for nombre, agente in self.agents.items():
            try:
                status_agentes[nombre] = agente.get_status()
            except Exception as e:
                status_agentes[nombre] = {
                    "estado": "error",
                    "error": str(e)
                }
        
        return {
            "coordinator_id": f"contabilidad_{self.tenant_id}",
            "tenant_id": self.tenant_id,
            "estado_coordinator": self.estado,
            "total_agentes": len(self.agents),
            "agentes_activos": len([s for s in status_agentes.values() if s.get("estado") == "operational"]),
            "agentes_status": status_agentes,
            "ultimo_reporte": self.ultimo_reporte["fecha_ejecucion"] if self.ultimo_reporte else None,
            "configuracion": {
                "enabled_agents": self.config.enabled_agents,
                "auto_execution": self.config.auto_execution,
                "integration_mode": self.config.integration_mode
            },
            "capabilities": [
                "Reportes fiscales automÃ¡ticos DGII/DIAN/SAT",
                "AnÃ¡lisis financiero ML con 50+ ratios",
                "Compliance NIIF/GAAP/Local con blockchain",
                "ConciliaciÃ³n bancaria automÃ¡tica",
                "AuditorÃ­a interna predictiva",
                "Control costos optimizaciÃ³n IA"
            ],
            "version": "2.0.0-enterprise",
            "fecha_status": datetime.now().isoformat()
        }


    def get_module_status(self):
        """Alias para compatibilidad con versiones anteriores"""
        return self.get_status_all_agents()


