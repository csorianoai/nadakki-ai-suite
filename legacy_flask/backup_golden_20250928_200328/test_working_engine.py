# test_working_engine.py
import asyncio
import json
from core.credit_engine_simple import SimpleCreditEngine, CreditProfile

async def main():
    print("="*60)
    print("SISTEMA DE EVALUACIÓN CREDITICIA - CREDICEFI")
    print("="*60)
    
    engine = SimpleCreditEngine()
    
    # Caso de prueba real
    profile = CreditProfile(
        client_id="CRED001",
        application_id="APP2024001",
        age=35,
        income=75000,
        employment_type="employed",
        employment_years=8,
        education_level="bachelor",
        marital_status="married",
        dependents=2,
        credit_score=720,
        previous_defaults=0,
        credit_utilization=0.35,
        payment_history_score=0.95,
        credit_age_months=120,
        debt_to_income=0.28,
        monthly_expenses=3500,
        savings=25000,
        assets_value=150000,
        loan_amount=50000,
        loan_purpose="home",
        loan_term_months=60,
        collateral_value=75000
    )
    
    print("\n📋 EVALUANDO PERFIL CREDITICIO...")
    print("-"*40)
    
    result = await engine.evaluate(profile)
    
    print(f"Cliente ID: {profile.client_id}")
    print(f"Monto Solicitado: ${profile.loan_amount:,.0f}")
    print(f"Score Crediticio: {profile.credit_score}")
    print(f"Ingresos: ${profile.income:,.0f}")
    
    print("\n🎯 RESULTADOS DE EVALUACIÓN:")
    print("-"*40)
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Decisión: {result['decision']}")
    print(f"Confianza: {result['confidence']:.2%}")
    print(f"Nivel de Riesgo: {result['explanation']['risk_level']}")
    
    print("\n💡 RECOMENDACIÓN:")
    print(result['explanation']['recommendation'])
    
    print("\n📊 FACTORES PRINCIPALES:")
    for factor in result['explanation']['main_factors']:
        emoji = "🔴" if factor['impact'] in ['HIGH', 'CRITICAL'] else "🟡" if factor['impact'] == 'MEDIUM' else "🟢"
        print(f"{emoji} {factor['factor']}: {factor['value']}")
    
    print("\n✅ Evaluación completada en {:.0f}ms".format(result['processing_time_ms']))

if __name__ == "__main__":
    asyncio.run(main())
