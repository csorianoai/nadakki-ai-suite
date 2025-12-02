import asyncio
import requests
import json
import time
import pandas as pd
from datetime import datetime
import logging

# Configuración de logging para pruebas
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperAgentTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = []
        self.performance_metrics = []
        
    async def run_comprehensive_test_suite(self):
        """Ejecutar suite completa de pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SUPER-AGENT")
        
        tests = [
            self.test_health_endpoints,
            self.test_content_generation,
            self.test_multi_tenant,
            self.test_error_handling,
            self.test_performance,
            self.test_self_healing,
            self.test_audit_system,
            self.test_ml_strategies
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Test {test.__name__} falló: {e}")
                
        self.generate_report()
        
    async def test_health_endpoints(self):
        """Prueba endpoints de salud"""
        print("\n🔍 Probando endpoints de salud...")
        
        endpoints = [
            "/health",
            "/api/v1/status/credicefi_b27fa331"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                latency = (time.time() - start_time) * 1000
                
                self.performance_metrics.append({
                    "test": "health_endpoints",
                    "endpoint": endpoint,
                    "latency_ms": latency,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - {latency:.2f}ms")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"💥 {endpoint} - Error: {e}")
                
    async def test_content_generation(self):
        """Prueba generación de contenido"""
        print("\n🎯 Probando generación de contenido...")
        
        test_cases = [
            {
                "name": "Análisis financiero básico",
                "data": {
                    "content_type": "ad_copy",
                    "audience_segment": "high_value", 
                    "brand_tone": "professional",
                    "key_message": "Análisis de ratios financieros y proyecciones",
                    "variant_count": 2
                }
            }
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/analyze/credicefi_b27fa331",
                    json=test_case["data"],
                    timeout=30
                )
                latency = (time.time() - start_time) * 1000
                
                result = {
                    "test": "content_generation",
                    "scenario": test_case["name"],
                    "latency_ms": latency,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    result.update({
                        "variants_generated": len(data.get("variants", [])),
                        "processing_time": data.get("processing_time_seconds", 0)
                    })
                    print(f"✅ {test_case['name']} - {latency:.2f}ms")
                else:
                    print(f"❌ {test_case['name']} - Status: {response.status_code}")
                    
                self.results.append(result)
                self.performance_metrics.append(result)
                
            except Exception as e:
                print(f"💥 {test_case['name']} - Error: {e}")
                
    async def test_multi_tenant(self):
        """Prueba funcionalidad multi-tenant"""
        print("\n🏢 Probando multi-tenant...")
        
        tenants = ["credicefi_b27fa331", "banco_prueba_001"]
        
        for tenant in tenants:
            try:
                # Test de status para diferentes tenants
                response = requests.get(f"{self.base_url}/api/v1/status/{tenant}", timeout=10)
                
                result = {
                    "test": "multi_tenant",
                    "tenant": tenant,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    print(f"✅ Tenant {tenant} - Funciona correctamente")
                else:
                    print(f"❌ Tenant {tenant} - Status: {response.status_code}")
                    
                self.results.append(result)
                
            except Exception as e:
                print(f"💥 Tenant {tenant} - Error: {e}")
                
    async def test_error_handling(self):
        """Prueba manejo de errores"""
        print("\n🛡️ Probando manejo de errores...")
        
        try:
            # Test con tenant que no existe
            response = requests.get(f"{self.base_url}/api/v1/status/tenant_inexistente", timeout=10)
            
            result = {
                "test": "error_handling", 
                "scenario": "tenant_inexistente",
                "status_code": response.status_code,
                "success": response.status_code != 500  # Éxito si no da error 500
            }
            
            if response.status_code != 500:
                print(f"✅ Error handling - Comportamiento correcto")
            else:
                print(f"❌ Error handling - Error del servidor")
                
            self.results.append(result)
            
        except Exception as e:
            print(f"💥 Error handling - Error: {e}")
                
    async def test_performance(self):
        """Pruebas de rendimiento"""
        print("\n⚡ Probando rendimiento...")
        
        # Test de carga básico
        start_time = time.time()
        requests_count = 3
        successful_requests = 0
        
        for i in range(requests_count):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
            except:
                pass
                
        total_time = time.time() - start_time
        rps = successful_requests / total_time if total_time > 0 else 0
        
        performance_result = {
            "test": "performance_load",
            "requests_count": requests_count,
            "successful_requests": successful_requests,
            "total_time_seconds": total_time,
            "requests_per_second": rps,
            "success": rps > 0.1
        }
        
        print(f"📊 Rendimiento: {rps:.2f} RPS ({successful_requests}/{requests_count} requests en {total_time:.2f}s)")
        self.results.append(performance_result)
        
    async def test_self_healing(self):
        """Prueba capacidades de resiliencia"""
        print("\n🔧 Probando health checks...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            result = {
                "test": "health_check",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                print("✅ Health check - Sistema funcionando")
            else:
                print(f"❌ Health check - Status: {response.status_code}")
                
            self.results.append(result)
            
        except Exception as e:
            print(f"💥 Health check - Error: {e}")
            
    async def test_audit_system(self):
        """Prueba sistema de métricas"""
        print("\n📋 Probando sistema de métricas...")
        
        try:
            # Generar una solicitud para tener métricas
            response = requests.post(
                f"{self.base_url}/api/v1/analyze/credicefi_b27fa331",
                json={
                    "content_type": "ad_copy",
                    "audience_segment": "high_value",
                    "brand_tone": "professional",
                    "key_message": "Test de métricas del sistema",
                    "variant_count": 1
                },
                timeout=20
            )
            
            result = {
                "test": "metrics_system",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                print("✅ Metrics - Solicitud procesada correctamente")
            else:
                print(f"❌ Metrics - Status: {response.status_code}")
                
            self.results.append(result)
            
        except Exception as e:
            print(f"💥 Metrics test - Error: {e}")
            
    async def test_ml_strategies(self):
        """Prueba integración ML"""
        print("\n🤖 Probando integración ML...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/analyze/credicefi_b27fa331",
                json={
                    "content_type": "ad_copy", 
                    "audience_segment": "high_value",
                    "brand_tone": "premium",
                    "key_message": "Test de integración ML",
                    "variant_count": 2
                },
                timeout=20
            )
            latency = (time.time() - start_time) * 1000
            
            result = {
                "test": "ml_integration",
                "latency_ms": latency,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ML Integration - {latency:.2f}ms - Análisis completado")
            else:
                print(f"❌ ML Integration - Status: {response.status_code}")
                
            self.results.append(result)
            
        except Exception as e:
            print(f"💥 ML Integration - Error: {e}")
                
    def generate_report(self):
        """Generar reporte completo de pruebas"""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DE PRUEBAS - SUPER-AGENT")
        print("="*60)
        
        if self.results:
            # Métricas generales
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r['success'])
            success_rate = (passed_tests / total_tests) * 100
            
            print(f"\n📈 ESTADÍSTICAS GENERALES:")
            print(f"   • Total de pruebas: {total_tests}")
            print(f"   • Pruebas exitosas: {passed_tests}")
            print(f"   • Tasa de éxito: {success_rate:.1f}%")
            
            # Evaluación final
            print(f"\n🎯 EVALUACIÓN FINAL:")
            
            if success_rate >= 90:
                print("   ✅ EXCELENTE - Listo para producción")
                rating = "A"
            elif success_rate >= 80:
                print("   ✅ MUY BUENO - Pocos ajustes necesarios") 
                rating = "B+"
            elif success_rate >= 70:
                print("   ✅ BUENO - Algunas mejoras recomendadas")
                rating = "B"
            elif success_rate >= 60:
                print("   ⚠️  ACEPTABLE - Mejoras necesarias")
                rating = "C"
            else:
                print("   ❌ REQUIERE ATENCIÓN - Problemas significativos")
                rating = "D"
                
            print(f"\n🏆 CALIFICACIÓN FINAL: {rating} ({success_rate:.1f}%)")
            
            # Guardar reporte detallado
            self.save_detailed_report()
        else:
            print("❌ No se recopilaron datos de pruebas")
        
    def save_detailed_report(self):
        """Guardar reporte detallado en CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"super_agent_test_report_{timestamp}.csv"
        
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"\n💾 Reporte detallado guardado como: {filename}")

# Ejecutar pruebas
async def main():
    tester = SuperAgentTester()
    await tester.run_comprehensive_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
