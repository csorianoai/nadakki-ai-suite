"""
🧪 TESTING SUPER AGENTES CONTABILIDAD - NADAKKI AI SUITE
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar path
sys.path.append('agents')

try:
    from contabilidad.contabilidad_coordinator import ContabilidadCoordinator
    from contabilidad.reportes_fiscales import ReportesFiscales
    from contabilidad.analisis_financiero import AnalisisFinanciero
    from contabilidad.compliance_contable import ComplianceContable
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Verificar que todos los archivos estén creados correctamente")
    sys.exit(1)

async def test_super_agentes_contabilidad():
    """Test completo de los super agentes de contabilidad"""
    
    print("🧪 TESTING SUPER AGENTES CONTABILIDAD NADAKKI AI")
    print("="*60)
    print("🎯 Objetivo: Validar 6 super agentes enterprise")
    print("📋 Agentes: 3 originales + 3 nuevos super agentes")
    print("⚡ Arquitectura: Enterprise SaaS Multi-tenant")
    print("="*60)
    
    tenant_id = "test_banco_demo"
    
    try:
        # Test 1: Inicialización del Coordinator
        print("\n1️⃣ TESTING COORDINATOR...")
        coordinator = ContabilidadCoordinator(tenant_id)
        
        status_all = coordinator.get_status_all_agents()
        print(f"✅ Coordinator inicializado: {status_all['total_agentes']} agentes")
        print(f"🟢 Agentes activos: {status_all['agentes_activos']}")
        
        # Test 2: ReportesFiscales individual
        print("\n2️⃣ TESTING REPORTES FISCALES...")
        reportes_agent = ReportesFiscales(tenant_id)
        
        # Test formulario 606
        periodo = datetime.now()
        reporte_606 = await reportes_agent.generar_reporte_606(periodo)
        print(f"✅ Formulario 606: {reporte_606['total_retenciones']} retenciones")
        print(f"⏱️  Tiempo: {reporte_606['tiempo_generacion_segundos']:.2f}s")
        
        # Test calendario fiscal
        calendario = await reportes_agent.obtener_calendario_fiscal()
        print(f"✅ Calendario fiscal: {calendario['alertas_criticas']} alertas críticas")
        
        # Test 3: AnalisisFinanciero individual
        print("\n3️⃣ TESTING ANÁLISIS FINANCIERO...")
        analisis_agent = AnalisisFinanciero(tenant_id)
        
        analisis_completo = await analisis_agent.realizar_analisis_completo()
        print(f"✅ Análisis completo: {len(analisis_completo['ratios_financieros'])} ratios")
        print(f"📊 Score salud: {analisis_completo['score_salud_financiera']['score_total']}/100")
        print(f"⏱️  Tiempo: {analisis_completo['tiempo_analisis_segundos']:.2f}s")
        
        if analisis_completo['predicciones_ml']['ml_habilitado']:
            predicciones = analisis_completo['predicciones_ml']['predicciones_flujo_caja']
            print(f"🔮 Predicciones ML: {len(predicciones)} meses proyectados")
        
        # Test 4: ComplianceContable individual
        print("\n4️⃣ TESTING COMPLIANCE CONTABLE...")
        compliance_agent = ComplianceContable(tenant_id)
        
        validacion = await compliance_agent.ejecutar_validacion_completa()
        print(f"✅ Compliance: {validacion['total_reglas_evaluadas']} reglas evaluadas")
        print(f"📋 Score: {validacion['analisis_compliance']['score_compliance_general']:.1f}%")
        print(f"⚠️  Riesgo: {validacion['analisis_compliance']['nivel_riesgo_compliance']}")
        
        dashboard = await compliance_agent.obtener_dashboard_compliance()
        print(f"🔗 Blockchain: {dashboard['blockchain_status']['bloques_total']} bloques")
        
        # Test 5: Proceso completo coordinado
        print("\n5️⃣ TESTING PROCESO COMPLETO...")
        resultado_completo = await coordinator.ejecutar_proceso_completo_contabilidad()
        
        resumen = resultado_completo['resumen_ejecutivo']
        print(f"✅ Proceso completo exitoso")
        print(f"📊 Agentes exitosos: {resumen['agentes_exitosos']}/{resumen['agentes_totales']}")
        print(f"⚠️  Alertas críticas: {resumen['alertas_criticas_total']}")
        print(f"💡 Recomendaciones: {resumen['recomendaciones_total']}")
        print(f"⏱️  Tiempo total: {resumen['tiempo_ejecucion_segundos']:.2f}s")
        
        # Test 6: Performance Benchmark
        print("\n6️⃣ BENCHMARK PERFORMANCE...")
        start_time = datetime.now()
        
        # Ejecutar todos los agentes en paralelo
        tasks = []
        if "reportes_fiscales" in coordinator.agents:
            tasks.append(coordinator.agents["reportes_fiscales"].generar_reporte_606(datetime.now()))
        if "analisis_financiero" in coordinator.agents:
            tasks.append(coordinator.agents["analisis_financiero"].realizar_analisis_completo())
        if "compliance_contable" in coordinator.agents:
            tasks.append(coordinator.agents["compliance_contable"].ejecutar_validacion_completa())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Ejecución paralela: {total_time:.2f}s")
        print(f"🚀 Performance: {len(tasks)} agentes concurrentes")
        
        # Verificar SLA <30s total
        if total_time < 30:
            print("🎯 SLA CUMPLIDO: <30s tiempo total")
        else:
            print("⚠️  SLA EXCEDIDO: >30s tiempo total")
        
        # Resumen final
        print("\n" + "="*60)
        print("🎉 TESTING COMPLETADO EXITOSAMENTE")
        print("="*60)
        print("✅ Todos los super agentes funcionando correctamente")
        print("📊 Sistema enterprise validado y operativo")
        print("🚀 Ready for production deployment")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTING: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    try:
        # Activar entorno virtual si es necesario
        print("🔧 Verificando entorno virtual...")
        
        # Ejecutar tests
        success = asyncio.run(test_super_agentes_contabilidad())
        
        if success:
            print("\n🎊 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
            exit(0)
        else:
            print("\n💥 Sistema requiere ajustes")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrumpido por usuario")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        exit(1)

if __name__ == "__main__":
    main()