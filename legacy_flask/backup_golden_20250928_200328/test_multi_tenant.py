#!/usr/bin/env python3
"""
Script de test para verificar configuraciones multi-tenant
"""

from tenant_manager import tenant_manager
from pathlib import Path

def test_tenant_configs():
    """Prueba las configuraciones de tenants"""
    
    print("🧪 Testing configuraciones multi-tenant de Nadakki AI Suite\n")
    
    # Verificar que existen los archivos de configuración
    config_dir = Path(__file__).parent / "config" / "tenants"
    
    print(f"📁 Verificando directorio: {config_dir}")
    if not config_dir.exists():
        print("❌ Directorio config/tenants no existe")
        return False
    
    print(f"✅ Directorio encontrado\n")
    
    # Listar todos los tenants configurados
    all_tenants = tenant_manager.list_all_tenants()
    
    if not all_tenants:
        print("❌ No se encontraron tenants configurados")
        print("💡 Ejecuta primero los comandos de setup:")
        print("   python setup_multi_tenant_legal.py --tenant-id banco-popular-rd --name 'Banco Popular' --test")
        return False
    
    print(f"📊 Tenants encontrados: {len(all_tenants)}\n")
    
    # Probar cada tenant
    for tenant_data in all_tenants:
        tenant_id = tenant_data["tenant_id"]
        
        print(f"🏦 Testing {tenant_id}:")
        print(f"   Nombre: {tenant_data['name']}")
        print(f"   Tipo: {tenant_data['type']}")
        print(f"   Plan: {tenant_data['tier']}")
        print(f"   Límite mensual: {tenant_data['monthly_limit']:,}")
        
        # Probar carga de configuraciones específicas
        thresholds = tenant_manager.get_ai_thresholds(tenant_id)
        rules = tenant_manager.get_business_rules(tenant_id)
        weights = tenant_manager.get_algorithm_weights(tenant_id)
        
        print(f"   🎯 Umbral rechazo automático: {thresholds.get('reject_auto', 'N/A')}")
        print(f"   💰 Monto máximo préstamo: ${rules.get('max_loan_amount', 0):,}")
        print(f"   📊 Score mínimo: {rules.get('min_credit_score', 'N/A')}")
        
        # Verificar que los pesos suman 1.0
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) < 0.01:
            print(f"   ✅ Pesos de algoritmos válidos (suma: {weight_sum:.2f})")
        else:
            print(f"   ⚠️  Pesos de algoritmos incorrectos (suma: {weight_sum:.2f})")
        
        # Validar tenant
        is_valid = tenant_manager.validate_tenant(tenant_id)
        print(f"   {'✅' if is_valid else '❌'} Tenant {'válido' if is_valid else 'inválido'}")
        
        print()
    
    print("🎉 Tests de multi-tenant completados")
    return True

if __name__ == "__main__":
    test_tenant_configs()