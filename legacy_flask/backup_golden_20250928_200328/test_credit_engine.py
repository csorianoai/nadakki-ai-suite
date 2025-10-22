# test_credit_engine.py
import asyncio
from core.credit_engine_production_v3 import ProductionCreditEngineV3, CreditProfile

async def main():
    # Inicializar engine
    engine = ProductionCreditEngineV3()
    
    # Crear perfil de prueba
    profile = CreditProfile(
        client_id="TEST001",
        application_id="APP001",
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
    
    # Evaluar
    result = await engine.evaluate(profile)
    print("Risk Score:", result["risk_score"])
    print("Decision:", result["decision"])
    print("Model Version:", result["model_version"])

if __name__ == "__main__":
    asyncio.run(main())
