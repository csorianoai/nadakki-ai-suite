from .base_components_v2 import *
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class DNAProfiler(BaseAgent):
    def __init__(self, tenant_id: str):
        super().__init__("DNAProfiler", "originacion", tenant_id)
        self.genetic_factors = [
            "demographic_dna", "financial_dna", "behavioral_dna", 
            "credit_dna", "social_dna"
        ]
        self.profile_database = {}
        print(f"🧬 DNAProfiler inicializado para tenant {tenant_id}")
    
    def create_credit_dna(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"🧬 Creando perfil DNA crediticio para tenant {self.tenant_id}")
            
            # Generar DNA signatures por factor
            dna_signatures = {}
            for factor in self.genetic_factors:
                signature = self._generate_dna_signature(applicant_data, factor)
                dna_signatures[factor] = signature
            
            # DNA único del perfil
            unique_dna = self._generate_unique_dna(dna_signatures)
            
            # Análisis de similitud con base histórica
            similarity_matches = self._find_similar_profiles(unique_dna)
            
            result = {
                "applicant_id": applicant_data.get("id", "unknown"),
                "unique_dna": unique_dna,
                "dna_signatures": dna_signatures,
                "similarity_matches": similarity_matches,
                "risk_inheritance": self._calculate_risk_inheritance(similarity_matches),
                "profile_strength": self._calculate_profile_strength(dna_signatures),
                "analysis_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "tenant": self.tenant_id
            }
            
            print(f"✅ DNA Profile creado: {unique_dna[:8]}...")
            return result
            
        except Exception as e:
            print(f"❌ Error en creación DNA profile: {str(e)}")
            return self._error_response(str(e))
    
    def _generate_dna_signature(self, data: Dict, factor: str) -> str:
        if factor == "demographic_dna":
            age = data.get("age", 30)
            location = data.get("location", "unknown")
            return hashlib.md5(f"{age}-{location}".encode()).hexdigest()[:12]
        elif factor == "financial_dna":
            income = data.get("monthly_income", 0)
            assets = data.get("assets", 0)
            return hashlib.md5(f"{income}-{assets}".encode()).hexdigest()[:12]
        elif factor == "behavioral_dna":
            spending = data.get("spending_pattern", "normal")
            return hashlib.md5(f"{spending}".encode()).hexdigest()[:12]
        elif factor == "credit_dna":
            score = data.get("credit_score", 300)
            history = data.get("credit_history_years", 0)
            return hashlib.md5(f"{score}-{history}".encode()).hexdigest()[:12]
        elif factor == "social_dna":
            employment = data.get("employment_type", "unknown")
            education = data.get("education", "unknown")
            return hashlib.md5(f"{employment}-{education}".encode()).hexdigest()[:12]
        else:
            return "000000000000"
    
    def _generate_unique_dna(self, signatures: Dict[str, str]) -> str:
        combined = "-".join(signatures.values())
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _find_similar_profiles(self, unique_dna: str) -> List[Dict]:
        # Simulación de búsqueda en base histórica
        return [
            {"dna": "abc123def456", "risk_level": "LOW", "similarity": 0.78},
            {"dna": "xyz789uvw012", "risk_level": "MEDIUM", "similarity": 0.65}
        ]
    
    def _calculate_risk_inheritance(self, matches: List[Dict]) -> float:
        if not matches:
            return 0.5
        risk_scores = {"LOW": 0.2, "MEDIUM": 0.6, "HIGH": 0.9}
        weighted_risk = sum(
            risk_scores.get(match["risk_level"], 0.5) * match["similarity"]
            for match in matches
        )
        total_weight = sum(match["similarity"] for match in matches)
        return round(weighted_risk / total_weight if total_weight > 0 else 0.5, 3)
    
    def _calculate_profile_strength(self, signatures: Dict[str, str]) -> float:
        # Strength basado en completitud de datos
        non_empty = sum(1 for sig in signatures.values() if sig != "000000000000")
        return round(non_empty / len(signatures), 3)
    
    def get_agent_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "category": self.category,
            "tenant_id": self.tenant_id,
            "status": "ACTIVE",
            "genetic_factors_count": len(self.genetic_factors),
            "profiles_in_database": len(self.profile_database)
        }
