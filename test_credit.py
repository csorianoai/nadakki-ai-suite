# test_credit.py
from core.credit_engine import CreditEngine, CreditProfile

def main():
    print("="*60)
    print("SISTEMA DE EVALUACIÓN CREDITICIA - CREDICEFI")
    print("="*60)
    
    engine = CreditEngine()
    
    # Crear perfil de prueba
    profile = CreditProfile(
        client_id="TEST001",
        application_id="APP001",
        age=35,
        income=75000,
        employment_type="employed",
        employment_years=8,
        credit_score=720,
        previous_defaults=0,
        credit_utilization=0.35,
        debt_to_income=0.28,
        loan_amount=50000,
        loan_purpose="home",
        loan_term_months=60,
        collateral_value=75000
    )
    
    # Evaluar
    result = engine.evaluate(profile)
    
    print(f"\nCliente: {profile.client_id}")
    print(f"Score Crediticio: {profile.credit_score}")
    print(f"Monto Solicitado: ${profile.loan_amount:,}")
    
    print("\n🎯 RESULTADOS:")
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Decisión: {result['decision']}")
    print(f"Recomendación: {result['recommendation']}")
    
    if result['factors']:
        print("\n⚠️ FACTORES DE RIESGO:")
        for factor in result['factors']:
            print(f"  - {factor['factor']} ({factor['impact']})")
    
    print("\n✅ Evaluación completada exitosamente")

if __name__ == "__main__":
    main()
