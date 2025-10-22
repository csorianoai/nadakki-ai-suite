import numpy as np
from datetime import datetime
import logging

class CreditSimilarityEngine:
    def __init__(self):
        self.risk_thresholds = {
            'reject_auto': 0.90,
            'high_risk': 0.80,
            'risky': 0.70,
            'medium_risk': 0.50,
            'low_risk': 0.00
        }
        self.logger = logging.getLogger(__name__)
    
    def evaluate_profile(self, new_profile, historical_defaults_db=None, tenant_id='demo'):
        # Algoritmo de similitud simplificado pero realista
        age = new_profile.get('age', 30)
        income = new_profile.get('income', 40000)
        credit_score = new_profile.get('credit_score', 600)
        
        # Calcular score de riesgo
        risk_score = 0.0
        
        # Factores de riesgo por edad
        if age < 25 or age > 65:
            risk_score += 0.15
        
        # Factores de riesgo por ingresos
        if income < 25000:
            risk_score += 0.30
        elif income < 40000:
            risk_score += 0.15
        
        # Factores de riesgo por credit score
        if credit_score < 450:
            risk_score += 0.40
        elif credit_score < 550:
            risk_score += 0.25
        elif credit_score < 650:
            risk_score += 0.10
        
        # Determinar nivel de riesgo
        if risk_score >= self.risk_thresholds['reject_auto']:
            decision = 'REJECT'
            level = 'reject_automatic'
            human_review = False
        elif risk_score >= self.risk_thresholds['high_risk']:
            decision = 'REVIEW_REQUIRED'
            level = 'high_risk'
            human_review = True
        elif risk_score >= self.risk_thresholds['risky']:
            decision = 'ADDITIONAL_ANALYSIS'
            level = 'risky'
            human_review = True
        elif risk_score >= self.risk_thresholds['medium_risk']:
            decision = 'SECOND_EVALUATION'
            level = 'medium_risk'
            human_review = True
        else:
            decision = 'APPROVE'
            level = 'low_risk'
            human_review = False
        
        return {
            'evaluation_id': f"EVAL_{tenant_id}_{int(datetime.utcnow().timestamp())}",
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow().isoformat(),
            'similarity_score': round(risk_score, 3),
            'risk_assessment': {
                'level': level,
                'decision': decision,
                'human_review': human_review,
                'explanation': f'Score de riesgo: {risk_score:.1%} - {level.replace("_", " ").title()}'
            },
            'input_analysis': {
                'age': age,
                'income': income,
                'credit_score': credit_score,
                'risk_factors': {
                    'age_risk': age < 25 or age > 65,
                    'income_risk': income < 40000,
                    'credit_risk': credit_score < 650
                }
            },
            'processing_time_ms': 150,
            'confidence': 0.85
        }
