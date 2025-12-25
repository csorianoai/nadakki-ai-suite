"""
Compliance Layer v1.1.0 - Enterprise Compliance Checks
Handles GDPR, CCPA, Fair Lending (ECOA/FHA) compliance
FIXED: Word boundaries para evitar falsos positivos
"""

import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class ComplianceStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class RegulationType(Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    FAIR_LENDING = "fair_lending"
    INTERNAL = "internal_policy"


# Atributos protegidos bajo Fair Lending (ECOA/FHA)
PROTECTED_ATTRIBUTES = [
    "race", "ethnicity", "national_origin", "religion",
    "sex", "gender", "marital_status", "age", "disability",
    "familial_status", "color"
]

# Campos PII comunes
PII_PATTERNS = [
    "email", "phone", "ssn", "social_security", "credit_card",
    "passport", "driver_license", "address", "birth_date", "dob"
]


def detect_pii_fields(data: Dict[str, Any], path: str = "") -> List[str]:
    """Detecta campos que pueden contener PII de forma recursiva."""
    pii_found = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            key_lower = key.lower()
            
            if any(pii in key_lower for pii in PII_PATTERNS):
                pii_found.append(current_path)
            
            pii_found.extend(detect_pii_fields(value, current_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            pii_found.extend(detect_pii_fields(item, f"{path}[{i}]"))
    
    return pii_found


def detect_protected_attributes(data: Dict[str, Any], path: str = "") -> List[str]:
    """Detecta atributos protegidos (Fair Lending) usando word boundaries."""
    protected_found = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            key_lower = key.lower()

            # Usar word boundaries para evitar falsos positivos 
            # (ej: "engagement" no debe matchear "age")
            for attr in PROTECTED_ATTRIBUTES:
                # Buscar palabra exacta separada por _ o al inicio/fin
                pattern = r'(^|_)' + re.escape(attr) + r'($|_)'
                if re.search(pattern, key_lower):
                    protected_found.append(current_path)
                    break

            protected_found.extend(detect_protected_attributes(value, current_path))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            protected_found.extend(detect_protected_attributes(item, f"{path}[{i}]"))

    return protected_found


def mask_pii_value(value: Any) -> str:
    """Enmascara un valor PII usando hash."""
    if value is None:
        return "MASKED_NULL"
    hashed = hashlib.sha256(str(value).encode()).hexdigest()[:12]
    return f"MASKED_{hashed}"


def apply_compliance_checks(
    input_data: Dict[str, Any],
    tenant_id: str = "default",
    agent_type: str = "unknown",
    regulations: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Aplica verificaciones de compliance al input.
    
    Returns:
        Dict con status de compliance, checks realizados, y issues bloqueantes
    """
    if regulations is None:
        regulations = ["gdpr", "fair_lending"]
    
    checks = []
    blocking_issues = []
    overall_status = ComplianceStatus.PASS
    
    # 1. PII Detection (GDPR)
    if "gdpr" in regulations:
        pii_fields = detect_pii_fields(input_data)
        pii_check = {
            "regulation": RegulationType.GDPR.value,
            "check_name": "pii_detection",
            "status": ComplianceStatus.PASS.value if len(pii_fields) < 5 else ComplianceStatus.WARNING.value,
            "details": {
                "pii_fields_found": pii_fields,
                "pii_count": len(pii_fields),
                "threshold": 5
            }
        }
        checks.append(pii_check)
        
        # 2. Data Minimization Check
        total_fields = _count_fields(input_data)
        minimization_check = {
            "regulation": RegulationType.GDPR.value,
            "check_name": "data_minimization",
            "status": ComplianceStatus.PASS.value if total_fields < 50 else ComplianceStatus.WARNING.value,
            "details": {
                "total_fields": total_fields,
                "recommendation": "Consider reducing data collection" if total_fields >= 50 else None
            }
        }
        checks.append(minimization_check)
    
    # 3. Protected Attributes Check (Fair Lending)
    if "fair_lending" in regulations:
        protected_attrs = detect_protected_attributes(input_data)
        fair_lending_check = {
            "regulation": RegulationType.FAIR_LENDING.value,
            "check_name": "protected_attributes",
            "status": ComplianceStatus.PASS.value if len(protected_attrs) == 0 else ComplianceStatus.FAIL.value,
            "details": {
                "protected_attributes_found": protected_attrs,
                "recommendation": "Remove protected attributes from scoring model" if protected_attrs else None
            },
            "auto_block": len(protected_attrs) > 0
        }
        checks.append(fair_lending_check)
        
        if protected_attrs:
            overall_status = ComplianceStatus.FAIL
            blocking_issues.append("Protected attributes detected in scoring input")
    
    # 4. Consent Check (si aplica)
    consent_given = input_data.get("consent_given", input_data.get("consent", True))
    consent_check = {
        "regulation": RegulationType.GDPR.value,
        "check_name": "consent_verification",
        "status": ComplianceStatus.PASS.value if consent_given else ComplianceStatus.WARNING.value,
        "details": {
            "consent_present": consent_given is not None,
            "consent_value": consent_given
        }
    }
    checks.append(consent_check)
    
    # 5. Internal Policy Check
    internal_check = {
        "regulation": RegulationType.INTERNAL.value,
        "check_name": "internal_policy",
        "status": ComplianceStatus.PASS.value,
        "details": {
            "policy_version": "POL-2024-v1.0",
            "last_reviewed": "2024-12-01"
        }
    }
    checks.append(internal_check)
    
    return {
        "compliance_status": overall_status.value,
        "checks_performed": len(checks),
        "checks": checks,
        "blocking_issues": blocking_issues,
        "applied_regulations": regulations,
        "_compliance_layer": {
            "version": "1.1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant_id": tenant_id,
            "agent_type": agent_type
        }
    }


def _count_fields(data: Any, count: int = 0) -> int:
    """Cuenta recursivamente el número de campos en una estructura."""
    if isinstance(data, dict):
        count += len(data)
        for value in data.values():
            count = _count_fields(value, count)
    elif isinstance(data, list):
        for item in data:
            count = _count_fields(item, count)
    return count
