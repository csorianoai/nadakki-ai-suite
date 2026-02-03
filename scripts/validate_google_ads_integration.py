"""Validador de Integración Google Ads"""
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("🔍 VALIDACIÓN INTEGRACIÓN GOOGLE ADS")
print("="*60 + "\n")

# Test 1: Importar agentes
print("1️⃣ Validando agentes Google Ads...")
try:
    from agents.marketing.google_ads import (
        GoogleAdsBudgetPacingIA,
        GoogleAdsStrategistIA,
        RSAAdCopyGeneratorIA,
        SearchTermsCleanerIA,
        OrchestratorIA,
        __all__
    )
    print(f"   ✅ {len(__all__)} agentes importan correctamente")
    for agent in __all__:
        print(f"      ✅ {agent}")
except Exception as e:
    print(f"   ❌ Error importando agentes: {e}")
    sys.exit(1)

# Test 2: Verificar archivos
print("\n2️⃣ Verificando estructura...")
files_to_check = [
    "nadakki-google-ads-mvp/agents/marketing/google_ads_budget_pacing_agent.py",
    "nadakki-google-ads-mvp/agents/marketing/google_ads_strategist_agent.py",
    "nadakki-google-ads-mvp/agents/marketing/rsa_ad_copy_generator_agent.py",
    "nadakki-google-ads-mvp/agents/marketing/search_terms_cleaner_agent.py",
    "nadakki-google-ads-mvp/agents/marketing/orchestrator_agent.py",
    ".env.google_ads"
]

missing_files = []
for file in files_to_check:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - NO ENCONTRADO")
        missing_files.append(file)

# Test 3: Configuración
print("\n3️⃣ Validando configuración...")
env_file = ".env.google_ads"
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_developer_token_here' in content:
            print(f"   ⚠️  .env.google_ads necesita credenciales reales")
        else:
            print(f"   ✅ .env.google_ads configurado")
else:
    print(f"   ❌ .env.google_ads no encontrado")

# Resumen
print("\n" + "="*60)
if not missing_files:
    print("✅ VALIDACIÓN EXITOSA")
    print("\n📋 Próximos pasos:")
    print("   1. Editar .env.google_ads con credenciales reales")
    print("   2. Ejecutar: python -m pytest tests/test_google_ads_integration.py")
    print("   3. Conectar dashboard con APIs")
else:
    print("❌ VALIDACIÓN CON ERRORES")
    print(f"\n   Archivos faltantes: {len(missing_files)}")
    
print("="*60 + "\n")
