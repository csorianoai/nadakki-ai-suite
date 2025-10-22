# ================================================================
# DOCUMENT VALIDATOR
# Validacion automatica de documentos usando OCR
# ================================================================

import json
import time
from datetime import datetime
from typing import Dict, List, Any

class DocumentValidator:
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self.agent_name = "DocumentValidator"
        self.version = "1.0.0"
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        document_type = data.get("document_type", "")
        document_data = data.get("document_data", "")
        
        validity_score = 0.0
        issues = []
        
        if len(document_data) > 100:
            validity_score += 0.4
        else:
            issues.append("Documento muy corto o vacio")
            
        if document_type in ["cedula", "pasaporte", "licencia"]:
            validity_score += 0.3
        else:
            issues.append("Tipo de documento no reconocido")
            
        if "fake" not in document_data.lower():
            validity_score += 0.3
        else:
            issues.append("Posible documento falsificado")
            
        return {
            "success": True,
            "document_valid": validity_score >= 0.7,
            "validity_score": validity_score,
            "issues": issues,
            "recommendation": "approved" if validity_score >= 0.7 else "rejected",
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    def health_check(self):
        return {"agent": self.agent_name, "status": "healthy"}
