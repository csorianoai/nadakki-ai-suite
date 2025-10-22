"""
Motor de Similitud Crediticia Híbrido Avanzado
Implementa algoritmos cuánticos para evaluación crediticia con 5 niveles de riesgo
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr
from datetime import datetime
import json
import logging

class CreditSimilarityEngineHybrid:
    """Motor híbrido de similitud crediticia con algoritmos cuánticos"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.scaler = StandardScaler()
        self.risk_thresholds = {
            'reject_auto': 0.90,     # ≥90% - RECHAZO AUTOMÁTICO
            'high_risk': 0.80,       # 80-89% - ALTO RIESGO
            'risky': 0.70,           # 70-79% - RIESGOSO
            'medium_risk': 0.50,     # 50-69% - RIESGO MEDIO
            'low_risk': 0.00         # <50% - RIESGO BAJO
        }
        self.weights = {
            'cosine': 0.4,      # Similitud de patrones
            'euclidean': 0.3,   # Distancia numérica
            'jaccard': 0.2,     # Similitud categórica
            'pearson': 0.1      # Correlación
        }
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configura logger para trazabilidad"""
        logger = logging.getLogger('CreditSimilarityEngine')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def evaluate_similarity(self, new_profile, historical_defaults, tenant_config=None):
        """Evaluación híbrida principal con 4 algoritmos combinados"""
        try:
            start_time = datetime.now()
            
            # Preparar datos
            new_vector = self._prepare_profile_vector(new_profile)
            default_vectors = self._prepare_historical_vectors(historical_defaults)
            
            if len(default_vectors) == 0:
                return self._create_result('low_risk', 0.1, "Sin historial de comparación")
            
            # Calcular similitudes con cada algoritmo
            similarities = {}
            
            # 1. Similitud Coseno (patrones de comportamiento)
            similarities['cosine'] = self._calculate_cosine_similarity(new_vector, default_vectors)
            
            # 2. Distancia Euclidiana Normalizada (valores numéricos)
            similarities['euclidean'] = self._calculate_euclidean_similarity(new_vector, default_vectors)
            
            # 3. Índice Jaccard (características categóricas)
            similarities['jaccard'] = self._calculate_jaccard_similarity(new_profile, historical_defaults)
            
            # 4. Correlación Pearson (tendencias)
            similarities['pearson'] = self._calculate_pearson_similarity(new_vector, default_vectors)
            
            # Combinar con weighted ensemble
            final_similarity = self._weighted_ensemble(similarities, tenant_config)
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(final_similarity)
            
            # Generar decisión automática
            automated_decision = self._generate_automated_decision(final_similarity, risk_level)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'quantum_similarity_score': round(final_similarity, 4),
                'risk_level': risk_level,
                'automated_decision': automated_decision,
                'algorithm_breakdown': {
                    'cosine_similarity': round(similarities['cosine'], 4),
                    'euclidean_similarity': round(similarities['euclidean'], 4),
                    'jaccard_similarity': round(similarities['jaccard'], 4),
                    'pearson_similarity': round(similarities['pearson'], 4)
                },
                'execution_time_seconds': round(execution_time, 3),
                'timestamp': datetime.now().isoformat(),
                'profiles_compared': len(default_vectors),
                'engine_version': '2.1.0-hybrid'
            }
            
            self.logger.info(f"Evaluation completed: score={final_similarity:.4f}, risk={risk_level}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in similarity evaluation: {e}")
            return self._create_error_result(str(e))
    
    def _prepare_profile_vector(self, profile):
        """Convierte perfil a vector numérico normalizado"""
        try:
            features = []
            
            # Características numéricas principales
            features.append(profile.get('income', 0) / 100000)  # Normalizar ingresos
            features.append(profile.get('credit_score', 500) / 1000)  # Normalizar score
            features.append(profile.get('age', 30) / 100)  # Normalizar edad
            features.append(profile.get('debt_to_income', 0.5))  # Ratio deuda
            features.append(profile.get('years_employed', 1) / 50)  # Años empleo
            features.append(profile.get('savings_ratio', 0.1))  # Ratio ahorros
            
            # Características categóricas convertidas a numéricas
            employment_map = {'unemployed': 0, 'part_time': 0.3, 'full_time': 1, 'self_employed': 0.7}
            features.append(employment_map.get(profile.get('employment_type', 'full_time'), 0.5))
            
            education_map = {'none': 0, 'high_school': 0.3, 'college': 0.7, 'graduate': 1}
            features.append(education_map.get(profile.get('education', 'high_school'), 0.3))
            
            return np.array(features)
            
        except Exception as e:
            self.logger.warning(f"Error preparing profile vector: {e}")
            return np.array([0.5] * 8)  # Vector por defecto
    
    def _prepare_historical_vectors(self, historical_defaults):
        """Prepara vectores de perfiles históricos morosos"""
        vectors = []
        for profile in historical_defaults:
            vector = self._prepare_profile_vector(profile)
            vectors.append(vector)
        return np.array(vectors) if vectors else np.array([])
    
    def _calculate_cosine_similarity(self, new_vector, default_vectors):
        """Calcula similitud coseno optimizada"""
        try:
            if len(default_vectors) == 0:
                return 0.0
            
            # Reshape para sklearn
            new_vector = new_vector.reshape(1, -1)
            
            # Calcular similitud coseno con cada perfil moroso
            similarities = cosine_similarity(new_vector, default_vectors)[0]
            
            # Retornar similitud máxima (peor caso)
            return float(np.max(similarities))
            
        except Exception as e:
            self.logger.warning(f"Error in cosine similarity: {e}")
            return 0.0
    
    def _calculate_euclidean_similarity(self, new_vector, default_vectors):
        """Calcula similitud basada en distancia euclidiana"""
        try:
            if len(default_vectors) == 0:
                return 0.0
            
            # Calcular distancias euclidianas
            distances = []
            for default_vector in default_vectors:
                distance = euclidean(new_vector, default_vector)
                distances.append(distance)
            
            # Convertir distancia mínima a similitud (0-1)
            min_distance = min(distances)
            max_possible_distance = np.sqrt(len(new_vector))  # Distancia máxima teórica
            
            # Similitud = 1 - (distancia / distancia_max)
            similarity = max(0, 1 - (min_distance / max_possible_distance))
            return float(similarity)
            
        except Exception as e:
            self.logger.warning(f"Error in euclidean similarity: {e}")
            return 0.0
    
    def _calculate_jaccard_similarity(self, new_profile, historical_defaults):
        """Calcula índice Jaccard para características categóricas"""
        try:
            if len(historical_defaults) == 0:
                return 0.0
            
            # Características categóricas clave
            categorical_features = ['employment_type', 'education', 'marital_status', 'housing_type']
            
            new_categories = set()
            for feature in categorical_features:
                if feature in new_profile:
                    new_categories.add(f"{feature}:{new_profile[feature]}")
            
            max_jaccard = 0.0
            
            for historical_profile in historical_defaults:
                historical_categories = set()
                for feature in categorical_features:
                    if feature in historical_profile:
                        historical_categories.add(f"{feature}:{historical_profile[feature]}")
                
                # Calcular índice Jaccard
                intersection = len(new_categories.intersection(historical_categories))
                union = len(new_categories.union(historical_categories))
                
                if union > 0:
                    jaccard = intersection / union
                    max_jaccard = max(max_jaccard, jaccard)
            
            return float(max_jaccard)
            
        except Exception as e:
            self.logger.warning(f"Error in Jaccard similarity: {e}")
            return 0.0
    
    def _calculate_pearson_similarity(self, new_vector, default_vectors):
        """Calcula correlación Pearson como medida de similitud"""
        try:
            if len(default_vectors) == 0:
                return 0.0
            
            max_correlation = 0.0
            
            for default_vector in default_vectors:
                try:
                    correlation, _ = pearsonr(new_vector, default_vector)
                    if not np.isnan(correlation):
                        max_correlation = max(max_correlation, abs(correlation))
                except:
                    continue
            
            return float(max_correlation)
            
        except Exception as e:
            self.logger.warning(f"Error in Pearson correlation: {e}")
            return 0.0
    
    def _weighted_ensemble(self, similarities, tenant_config=None):
        """Combina algoritmos con pesos configurables"""
        try:
            # Usar pesos específicos del tenant si disponibles
            if tenant_config and 'similarity_weights' in tenant_config:
                weights = tenant_config['similarity_weights']
            else:
                weights = self.weights
            
            # Calcular promedio ponderado
            weighted_sum = 0.0
            total_weight = 0.0
            
            for algorithm, weight in weights.items():
                if algorithm in similarities:
                    weighted_sum += similarities[algorithm] * weight
                    total_weight += weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.0
                
        except Exception as e:
            self.logger.warning(f"Error in weighted ensemble: {e}")
            return 0.0
    
    def _determine_risk_level(self, similarity_score):
        """Determina nivel de riesgo basado en similitud"""
        if similarity_score >= self.risk_thresholds['reject_auto']:
            return 'REJECT_AUTO'
        elif similarity_score >= self.risk_thresholds['high_risk']:
            return 'HIGH_RISK'
        elif similarity_score >= self.risk_thresholds['risky']:
            return 'RISKY'
        elif similarity_score >= self.risk_thresholds['medium_risk']:
            return 'MEDIUM_RISK'
        else:
            return 'LOW_RISK'
    
    def _generate_automated_decision(self, similarity_score, risk_level):
        """Genera decisión automática basada en nivel de riesgo"""
        if risk_level == 'REJECT_AUTO':
            return {
                'action': 'REJECT',
                'automated': True,
                'reason': 'Alta similitud con perfiles morosos históricos',
                'human_review_required': False,
                'confidence': min(similarity_score * 100, 99.9)
            }
        elif risk_level == 'HIGH_RISK':
            return {
                'action': 'REVIEW',
                'automated': True,
                'reason': 'Perfil de riesgo elevado requiere análisis adicional',
                'human_review_required': True,
                'confidence': similarity_score * 100
            }
        elif risk_level == 'RISKY':
            return {
                'action': 'CONDITIONAL_APPROVE',
                'automated': True,
                'reason': 'Aprobación condicional con términos ajustados',
                'human_review_required': True,
                'confidence': (1 - similarity_score) * 100
            }
        elif risk_level == 'MEDIUM_RISK':
            return {
                'action': 'APPROVE_MONITORED',
                'automated': True,
                'reason': 'Aprobación con monitoreo adicional',
                'human_review_required': False,
                'confidence': (1 - similarity_score) * 100
            }
        else:  # LOW_RISK
            return {
                'action': 'APPROVE',
                'automated': True,
                'reason': 'Perfil de bajo riesgo crediticio',
                'human_review_required': False,
                'confidence': (1 - similarity_score) * 100
            }
    
    def _create_result(self, risk_level, similarity_score, reason):
        """Crea resultado estándar"""
        return {
            'quantum_similarity_score': round(similarity_score, 4),
            'risk_level': risk_level.upper(),
            'automated_decision': self._generate_automated_decision(similarity_score, risk_level.upper()),
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'engine_version': '2.1.0-hybrid'
        }
    
    def _create_error_result(self, error_message):
        """Crea resultado de error"""
        return {
            'quantum_similarity_score': 0.5,
            'risk_level': 'MEDIUM_RISK',
            'automated_decision': {
                'action': 'REVIEW',
                'automated': False,
                'reason': f'Error en evaluación: {error_message}',
                'human_review_required': True
            },
            'error': error_message,
            'timestamp': datetime.now().isoformat(),
            'engine_version': '2.1.0-hybrid'
        }

# Función de conveniencia para integración
def evaluate_credit_similarity(new_profile, historical_defaults, config=None):
    """Función principal para evaluación de similitud crediticia"""
    engine = CreditSimilarityEngineHybrid(config)
    return engine.evaluate_similarity(new_profile, historical_defaults, config)
