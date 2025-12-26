from agents.marketing.layers.compliance_layer import detect_protected_attributes

test_cases = [
    {"age": 25},  # ✓ Debe detectar
    {"person_age": 30},  # ✓ Debe detectar
    {"engagement": 85.5},  # ✗ NO debe detectar
    {"engagement_score": 90},  # ✗ NO debe detectar
    {"management": "senior"},  # ✗ NO debe detectar
    {"gender": "female"}  # ✓ Debe detectar
]

for i, data in enumerate(test_cases, 1):
    protected = detect_protected_attributes(data)
    print(f"Test {i}: {data}")
    print(f"  Detected: {protected}")
    print()
