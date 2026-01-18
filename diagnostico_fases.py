#!/usr/bin/env python3
"""
NADAKKI AI SUITE - DIAGNÓSTICO COMPLETO FASE 1 Y FASE 2
"""
import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

def ok(msg): print(f"   ✅ {msg}")
def fail(msg): print(f"   ❌ {msg}")
def warn(msg): print(f"   ⚠️  {msg}")

results = {"f1_pass": 0, "f1_fail": 0, "f2_pass": 0, "f2_fail": 0}

async def main():
    print("\n" + "="*70)
    print("   NADAKKI AI SUITE - DIAGNÓSTICO FASE 1 Y FASE 2")
    print("   " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)

    # === FASE 1: ARCHIVOS ===
    print("\n[FASE 1.1] VERIFICACIÓN DE ARCHIVOS")
    files = [
        "agents/shared_layers/executors/llm_executor.py",
        "agents/shared_layers/executors/providers/openai_executor.py",
        "agents/shared_layers/executors/providers/anthropic_executor.py",
        "agents/shared_layers/executors/providers/deepseek_executor.py",
        "agents/shared_layers/executors/providers/grok_executor.py",
    ]
    for f in files:
        if os.path.exists(f):
            ok(f)
            results["f1_pass"] += 1
        else:
            fail(f)
            results["f1_fail"] += 1

    # === FASE 1: API KEYS ===
    print("\n[FASE 1.2] VERIFICACIÓN DE API KEYS")
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GROK_API_KEY"]
    for k in keys:
        if os.getenv(k) and len(os.getenv(k)) > 10:
            ok(k)
            results["f1_pass"] += 1
        else:
            fail(f"{k} - No configurada")
            results["f1_fail"] += 1

    # === FASE 1: LLM EXECUTOR ===
    print("\n[FASE 1.3] PRUEBA DE LLM EXECUTOR")
    try:
        from agents.shared_layers.executors.llm_executor import get_llm
        llm = get_llm()
        ok(f"LLM Executor inicializado - Modelos: {llm.get_models()}")
        results["f1_pass"] += 1
    except Exception as e:
        fail(f"LLM Executor: {e}")
        results["f1_fail"] += 1
        return

    # === FASE 1: GENERACIÓN ===
    print("\n[FASE 1.4] PRUEBA DE GENERACIÓN (4 modelos)")
    models = [
        ("gpt-4o-mini", "OpenAI"),
        ("deepseek-chat", "DeepSeek"),
        ("claude-3-haiku-20240307", "Claude"),
        ("grok-3", "Grok"),
    ]
    for model, name in models:
        try:
            r = await llm.generate("Di solo: OK", model=model)
            ok(f"{name}: {r['content'][:20]}... ${r['cost']:.6f}")
            results["f1_pass"] += 1
        except Exception as e:
            fail(f"{name}: {str(e)[:50]}")
            results["f1_fail"] += 1

    # === FASE 2: ARCHIVOS ===
    print("\n[FASE 2.1] VERIFICACIÓN DE ARCHIVOS SOCIAL")
    social_files = [
        "agents/shared_layers/executors/social/base_social.py",
        "agents/shared_layers/executors/social/facebook_executor.py",
        "agents/shared_layers/executors/social/instagram_executor.py",
        "agents/shared_layers/executors/social/social_manager.py",
    ]
    for f in social_files:
        if os.path.exists(f):
            ok(f)
            results["f2_pass"] += 1
        else:
            fail(f)
            results["f2_fail"] += 1

    # === FASE 2: IMPORTS ===
    print("\n[FASE 2.2] VERIFICACIÓN DE IMPORTS SOCIAL")
    try:
        from agents.shared_layers.executors.social import FacebookExecutor, InstagramExecutor, SocialManager, get_social
        ok("Todos los imports de social funcionan")
        results["f2_pass"] += 1
    except Exception as e:
        fail(f"Imports social: {e}")
        results["f2_fail"] += 1

    # === FASE 2: SOCIAL MANAGER ===
    print("\n[FASE 2.3] PRUEBA DE SOCIAL MANAGER")
    try:
        from agents.shared_layers.executors.social import get_social
        social = get_social()
        platforms = social.get_platforms()
        ok(f"SocialManager OK - Plataformas: {platforms if platforms else 'Ninguna (requiere config)'}")
        results["f2_pass"] += 1
    except Exception as e:
        fail(f"SocialManager: {e}")
        results["f2_fail"] += 1

    # === RESUMEN ===
    print("\n" + "="*70)
    print("   RESUMEN DE DIAGNÓSTICO")
    print("="*70)
    
    f1_total = results["f1_pass"] + results["f1_fail"]
    f2_total = results["f2_pass"] + results["f2_fail"]
    f1_pct = (results["f1_pass"] / f1_total * 100) if f1_total > 0 else 0
    f2_pct = (results["f2_pass"] / f2_total * 100) if f2_total > 0 else 0
    
    print(f"\n   FASE 1 (LLM Executors):")
    print(f"   ├── Pasados: {results['f1_pass']}/{f1_total}")
    print(f"   └── Estado:  {'✅ COMPLETADA' if results['f1_fail'] == 0 else '⚠️ CON ERRORES'} ({f1_pct:.0f}%)")
    
    print(f"\n   FASE 2 (Social Executors):")
    print(f"   ├── Pasados: {results['f2_pass']}/{f2_total}")
    print(f"   └── Estado:  {'✅ COMPLETADA' if results['f2_fail'] == 0 else '⚠️ CON ERRORES'} ({f2_pct:.0f}%)")
    
    total_pct = ((results["f1_pass"] + results["f2_pass"]) / (f1_total + f2_total) * 100)
    
    print("\n" + "="*70)
    if total_pct >= 90:
        print("   🚀 LISTO PARA CONTINUAR A FASE 3 Y FASE 4")
    elif total_pct >= 70:
        print("   ⚠️  REVISAR ERRORES MENORES ANTES DE CONTINUAR")
    else:
        print("   ❌ CORREGIR ERRORES CRÍTICOS PRIMERO")
    print("="*70 + "\n")

asyncio.run(main())
