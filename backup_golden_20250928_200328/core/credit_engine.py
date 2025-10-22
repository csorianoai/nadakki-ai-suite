# core/credit_engine.py
"""Motor de Evaluación Crediticia - Versión Funcional"""
import json
from datetime import datetime
from typing import Dict, Any, List
import random

class CreditProfile:
    def __init__(self, **kwargs):
        self.client_id = kwargs.get('client_id', '')
        self.application_id = kwargs.get('application_id', '')
        self.age = kwargs.get('age', 0)
        self.income = kwargs.get('income', 0)
        self.employment_type = kwargs.get('employment_type', '')
        self.employment_years = kwargs.get('employment_years', 0)
        self.education_level = kwargs.get('education_level', '')
        self.marital_status = kwargs.get('marital_status', '')
        self.dependents = kwargs.get('dependents', 0)
        self.credit_score = kwargs.get('credit_score', 0)
        self.previous_defaults = kwargs.get('previous_defaults', 0)
        self.credit_utilization = kwargs.get('credit_utilization', 0)
        self.payment_history_score = kwargs.get('payment_history_score', 0)
        self.credit_age_months = kwargs.get('credit_age_months', 0)
        self.debt_to_income = kwargs.get('debt_to_income', 0)
        self.monthly_expenses = kwargs.get('monthly_expenses', 0)
        self.savings = kwargs.get('savings', 0)
        self.assets_value = kwargs.get('assets_value', 0)
        self.loan_amount = kwargs.get('loan_amount', 0)
        self.loan_purpose = kwargs.get('loan_purpose', '')
        self.loan_term_months = kwargs.get('loan_term_months', 0)
        self.collateral_value = kwargs.get('collateral_value', 0)

class CreditEngine:
    def evaluate(self, profile: CreditProfile) -> Dict[str, Any]:
        # Calcular risk score basado en factores clave
        risk_score = self._calculate_risk_score(profile)
        
        # Determinar decisión
        if profile.previous_defaults > 2 or profile.credit_score < 500:
            decision = "AUTO_REJECTED"
        elif risk_score < 0.3 and profile.credit_score > 700:
            decision = "AUTO_APPROVED"
        elif risk_score < 0.5:
            decision = "CONDITIONAL_APPROVED"
        elif risk_score < 0.7:
            decision = "MANUAL_REVIEW"
        else:
            decision = "AUTO_REJECTED"
        
        return {
            'application_id': profile.application_id,
            'timestamp': datetime.now().isoformat(),
            'risk_score': round(risk_score, 4),
            'decision': decision,
            'factors': self._get_factors(profile),
            'recommendation': self._get_recommendation(risk_score, decision)
        }
    
    def _calculate_risk_score(self, profile: CreditProfile) -> float:
        # Fórmula simple pero efectiva
        score = 0.0
        
        # Factor credit score (40% peso)
        if profile.credit_score > 0:
            score += (850 - profile.credit_score) / 850 * 0.4
        
        # Factor DTI (30% peso)
        score += min(profile.debt_to_income, 1.0) * 0.3
        
        # Factor defaults (20% peso)
        score += min(profile.previous_defaults / 5, 1.0) * 0.2
        
        # Factor utilization (10% peso)
        score += profile.credit_utilization * 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _get_factors(self, profile: CreditProfile) -> List[Dict]:
        factors = []
        
        if profile.credit_score < 650:
            factors.append({'factor': 'Low Credit Score', 'impact': 'HIGH'})
        
        if profile.debt_to_income > 0.4:
            factors.append({'factor': 'High Debt-to-Income', 'impact': 'HIGH'})
        
        if profile.previous_defaults > 0:
            factors.append({'factor': f'{profile.previous_defaults} Previous Defaults', 'impact': 'CRITICAL'})
        
        return factors
    
    def _get_recommendation(self, risk_score: float, decision: str) -> str:
        if decision == "AUTO_APPROVED":
            return "Proceed with loan approval"
        elif decision == "AUTO_REJECTED":
            return "Decline application - High risk profile"
        elif decision == "CONDITIONAL_APPROVED":
            return "Approve with conditions - Request additional collateral"
        else:
            return "Requires manual review by credit analyst"
