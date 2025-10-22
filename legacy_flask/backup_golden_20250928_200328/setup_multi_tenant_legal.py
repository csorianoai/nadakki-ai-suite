#!/usr/bin/env python3
"""
Setup Multi-Tenant Legal System for Nadakki AI Suite
Configura instituciones financieras con parámetros específicos
"""

import os
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

class MultiTenantSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / "config" / "tenants"
        
        # Crear directorios si no existen
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_tenant_config(self, tenant_id, name, tenant_type="financial"):
        """Crea configuración específica para un tenant"""
        
        config = {
            "tenant_info": {
                "id": tenant_id,
                "name": name,
                "type": tenant_type,
                "country": "RD",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            
            "ai_engine": {
                "similarity_thresholds": {
                    "reject_auto": 0.90,
                    "high_risk": 0.80,
                    "risky": 0.70,
                    "medium_risk": 0.50,
                    "low_risk": 0.00
                },
                "algorithm_weights": {
                    "cosine": 0.4,
                    "euclidean": 0.3,
                    "jaccard": 0.3
                },
                "feature_weights": {
                    "credit_score": 0.25,
                    "income": 0.20,
                    "debt_to_income": 0.20,
                    "employment_history": 0.15,
                    "payment_history": 0.20
                }
            },
            
            "agents_config": {
                "enabled_modules": [
                    "originacion",
                    "decision",
                    "vigilancia", 
                    "recuperacion",
                    "compliance",
                    "operacional",
                    "experiencia",
                    "inteligencia",
                    "fortaleza",
                    "orchestration"
                ]
            },
            
            "business_rules": {
                "max_loan_amount": 5000000,  # RD$5M
                "min_credit_score": 600,
                "max_debt_to_income": 0.50,
                "required_documents": [
                    "cedula",
                    "certificacion_ingresos", 
                    "referencias_comerciales",
                    "estados_cuenta"
                ]
            },
            
            "pricing_plan": {
                "tier": "professional",
                "monthly_evaluations_limit": 10000,
                "price_per_month": 1999,
                "overage_price_per_evaluation": 0.05
            },
            
            "performance_targets": {
                "response_time_ms": 3000,
                "accuracy_threshold": 0.95,
                "uptime_sla": 0.995
            }
        }
        
        # Configuraciones específicas por institución
        if "banco-popular" in tenant_id:
            config["business_rules"]["max_loan_amount"] = 8000000
            config["pricing_plan"]["tier"] = "enterprise"
            config["pricing_plan"]["monthly_evaluations_limit"] = 50000
            config["pricing_plan"]["price_per_month"] = 4999
            
        elif "banreservas" in tenant_id:
            config["business_rules"]["min_credit_score"] = 650
            config["ai_engine"]["similarity_thresholds"]["reject_auto"] = 0.85
            
        elif "cofaci" in tenant_id:
            config["pricing_plan"]["tier"] = "starter" 
            config["pricing_plan"]["monthly_evaluations_limit"] = 1000
            config["pricing_plan"]["price_per_month"] = 999
            
        elif "credicefi" in tenant_id:
            config["pricing_plan"]["tier"] = "professional"
            config["pricing_plan"]["monthly_evaluations_limit"] = 15000
            config["pricing_plan"]["price_per_month"] = 2499
            config["business_rules"]["max_loan_amount"] = 6000000
            config["business_rules"]["min_credit_score"] = 620
            config["ai_engine"]["similarity_thresholds"]["reject_auto"] = 0.88
        
        return config
    
    def save_config(self, tenant_id, config):
        """Guarda configuración en archivo JSON"""
        config_file = self.config_dir / f"{tenant_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuración guardada: {config_file}")
        return config_file
    
    def test_config(self, tenant_id):
        """Prueba la configuración cargándola"""
        try:
            config_file = self.config_dir / f"{tenant_id}.json"
            
            if not config_file.exists():
                print(f"❌ Archivo no existe: {config_file}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✅ Configuración válida para {tenant_id}")
            print(f"   📊 Plan: {config['pricing_plan']['tier']}")
            print(f"   🏦 Institución: {config['tenant_info']['name']}")
            print(f"   💰 Límite mensual: {config['pricing_plan']['monthly_evaluations_limit']:,}")
            print(f"   🎯 Umbral rechazo: {config['ai_engine']['similarity_thresholds']['reject_auto']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Setup Multi-Tenant para Nadakki AI Suite')
    parser.add_argument('--tenant-id', required=True, help='ID único del tenant')
    parser.add_argument('--name', required=True, help='Nombre de la institución')
    parser.add_argument('--type', default='financial', help='Tipo de institución')
    parser.add_argument('--test', action='store_true', help='Ejecutar tests')
    
    args = parser.parse_args()
    
    setup = MultiTenantSetup()
    
    try:
        print(f"🚀 Configurando tenant: {args.tenant_id}")
        print(f"🏢 Institución: {args.name}")
        
        # Crear configuración
        config = setup.create_tenant_config(args.tenant_id, args.name, args.type)
        
        # Guardar configuración
        config_file = setup.save_config(args.tenant_id, config)
        
        # Ejecutar tests si se solicita
        if args.test:
            print(f"\n🧪 Ejecutando tests para {args.tenant_id}...")
            success = setup.test_config(args.tenant_id)
            if success:
                print("✅ Tests completados exitosamente")
            else:
                print("❌ Tests fallaron")
                return 1
        
        print(f"\n🎉 Setup completado para {args.tenant_id}")
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())