"""Descubrir formato correcto de Lead"""
import sys
sys.path.append('.')

from schemas.canonical import Lead, LeadAttributes
import json

print("\n" + "="*60)
print("INSPECCION DE SCHEMA Lead")
print("="*60 + "\n")

# Schema completo
schema = Lead.model_json_schema()

print("CAMPOS REQUERIDOS:")
for field, info in schema.get('properties', {}).items():
    required = field in schema.get('required', [])
    field_type = info.get('type', info.get('anyOf', 'unknown'))
    print(f"  {'*' if required else ' '} {field}: {field_type}")

print("\n" + "="*60)
print("EJEMPLO DE CREACION CORRECTA:")
print("="*60 + "\n")

# Intentar diferentes formatos
test_cases = [
    {
        "name": "Test 1: persona como dict vacio",
        "data": {
            "tenant_id": "test",
            "lead_id": "L-20251012-0001",
            "persona": {},
            "contact": {"email": "test@test.com"},
            "attributes": LeadAttributes(credit_score=700, income=50000, channel="referral"),
            "events": []
        }
    },
    {
        "name": "Test 2: persona con tipo",
        "data": {
            "tenant_id": "test",
            "lead_id": "L-20251012-0001",
            "persona": {"type": "individual"},
            "contact": {"email": "test@test.com"},
            "attributes": LeadAttributes(credit_score=700, income=50000, channel="referral"),
            "events": []
        }
    },
    {
        "name": "Test 3: minimo requerido",
        "data": {
            "tenant_id": "test",
            "lead_id": "L-20251012-0001",
            "persona": {"customer_type": "individual"},
            "contact": {},
            "attributes": LeadAttributes(credit_score=700, income=50000, channel="referral"),
        }
    }
]

for test in test_cases:
    print(f"\n{test['name']}:")
    try:
        lead = Lead(**test['data'])
        print(f"  ✓ FUNCIONA!")
        print(f"  Lead ID: {lead.lead_id}")
        print(f"  Persona: {lead.persona}")
        print(f"  Contact: {lead.contact}")
        break  # Si funciona, usar este formato
    except Exception as e:
        print(f"  ✖ Error: {str(e)[:100]}")

print("\n")