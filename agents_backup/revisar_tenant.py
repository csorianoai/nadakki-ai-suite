#!/usr/bin/env python3
"""
Script para revisar configuración específica de un tenant
"""

import sys
from tenant_manager import tenant_manager
import json

def revisar_tenant(tenant_id):
    """Revisa configuración detallada de un tenant específico"""
    
    print(f"🔍 REVISIÓN DETALLADA DE: {tenant_id}")
    print("=" * 50)
    
    # Verificar si existe
    if not tenant_manager.validate_tenant(tenant_id):
        print(f"❌ Tenant {tenant_id} no existe o no está activo")
        return False
    
    # Obtener todas las configuraciones
    config = tenant_manager.load_tenant_config(tenant_id)
    tenant_info = tenant_manager.get_tenant_info(tenant_id)
    ai_thresholds = tenant_manager.get_ai_thresholds(tenant_id)
    business_rules = tenant_manager.get_business_rules(tenant_id)
    pricing = tenant_manager.get_pricing_plan(tenant_id)
    weights = tenant_manager.get_algorithm_weights(tenant_id)
    
    # Mostrar información básica
    print(f"\n🏦 INFORMACIÓN BÁSICA:")
    print(f"   ID: {tenant_info.get('id')}")
    print(f"   Nombre: {tenant_info.get('name')}")
    print(f"   Tipo: {tenant_info.get('type')}")
    print(f"   País: {tenant_info.get('country')}")
    print(f"   Estado: {tenant_info.get('status')}")
    print(f"   Creado: {tenant_info.get('created_at', 'N/A')}")
    
    # Mostrar plan de pricing
    print(f"\n💰 PLAN DE PRICING:")
    print(f"   Tier: {pricing.get('tier')}")
    print(f"   Precio mensual: ${pricing.get('price_per_month', 0):,}")
    print(f"   Límite evaluaciones: {pricing.get('monthly_evaluations_limit', 0):,}")
    print(f"   Precio por exceso: ${pricing.get('overage_price_per_evaluation', 0)}")
    
    # Mostrar reglas de negocio
    print(f"\n📋 REGLAS DE NEGOCIO:")
    print(f"   Monto máximo préstamo: ${business_rules.get('max_loan_amount', 0):,}")
    print(f"   Score crediticio mínimo: {business_rules.get('min_credit_score', 0)}")
    print(f"   Debt-to-income máximo: {business_rules.get('max_debt_to_income', 0):.2f}")
    
    docs = business_rules.get('required_documents', [])
    if docs:
        print(f"   Documentos requeridos: {', '.join(docs)}")
    
    # Mostrar umbrales de IA
    print(f"\n🤖 UMBRALES DE IA:")
    print(f"   Rechazo automático: {ai_thresholds.get('reject_auto', 0):.2f} (≥{ai_thresholds.get('reject_auto', 0)*100:.0f}%)")
    print(f"   Alto riesgo: {ai_thresholds.get('high_risk', 0):.2f} ({ai_thresholds.get('high_risk', 0)*100:.0f}%-{ai_thresholds.get('reject_auto', 0)*100-1:.0f}%)")
    print(f"   Riesgoso: {ai_thresholds.get('risky', 0):.2f} ({ai_thresholds.get('risky', 0)*100:.0f}%-{ai_thresholds.get('high_risk', 0)*100-1:.0f}%)")
    print(f"   Riesgo medio: {ai_thresholds.get('medium_risk', 0):.2f} ({ai_thresholds.get('medium_risk', 0)*100:.0f}%-{ai_thresholds.get('risky', 0)*100-1:.0f}%)")
    print(f"   Riesgo bajo: <{ai_thresholds.get('medium_risk', 0):.2f} (<{ai_thresholds.get('medium_risk', 0)*100:.0f}%)")
    
    # Mostrar pesos de algoritmos
    print(f"\n⚖️  PESOS DE ALGORITMOS:")
    for alg, peso in weights.items():
        print(f"   {alg.capitalize()}: {peso:.1f} ({peso*100:.0f}%)")
    
    peso_total = sum(weights.values())
    print(f"   Total: {peso_total:.2f} {'✅' if abs(peso_total - 1.0) < 0.01 else '❌'}")
    
    # Mostrar módulos habilitados
    if config and 'agents_config' in config:
        enabled_modules = config['agents_config'].get('enabled_modules', [])
        print(f"\n🔧 MÓDULOS HABILITADOS ({len(enabled_modules)}):")
        for i, module in enumerate(enabled_modules, 1):
            print(f"   {i:2d}. {module}")
    
    print(f"\n✅ Revisión completada para {tenant_id}")
    return True

def main():
    if len(sys.argv) != 2:
        print("Uso: python revisar_tenant.py <tenant-id>")
        print("Ejemplo: python revisar_tenant.py credicefi-rd")
        sys.exit(1)
    
    tenant_id = sys.argv[1]
    revisar_tenant(tenant_id)

if __name__ == "__main__":
    main()