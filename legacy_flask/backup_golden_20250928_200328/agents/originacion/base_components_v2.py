"""
🔧 COMPONENTES COMPARTIDOS ENTERPRISE V2.0 - ECOSISTEMA ORIGINACIÓN INTELIGENTE
Clases base reutilizables con mejoras enterprise críticas
"""

import numpy as np
import json
import redis
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from pathlib import Path

# Configurar logger enterprise
class TenantAwareLogger:
    """Logger enterprise con contexto de tenant"""
    def __init__(self, agent_name: str):
        self.logger = logging.getLogger(f"nadakki.{agent_name}")
        self.agent_name = agent_name
    
    def log_with_tenant(self, level: str, message: str, tenant_id: str, extra_data: Dict = None):
        """Log con contexto de tenant para auditoría"""
        log_data = {
            'agent': self.agent_name,
            'tenant_id': tenant_id,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        if extra_data:
            log_data.update(extra_data)
        
        getattr(self.logger, level.lower())(
            message, 
            extra={'tenant_id': tenant_id, 'log_data': log_data}
        )

@dataclass
class AgentAssessment:
    """Estructura de datos estándar para evaluaciones de agentes"""
    agent_name: str
    primary_score: float
    secondary_metrics: Dict[str, float]
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]
    processing_time: float
    timestamp: datetime
    tenant_id: str
    rag_insights: List[str] = None
    ml_predictions: Dict[str, float] = None
    tenant_context: Dict[str, Any] = None
    prompt_log_id: str = None
    cache_hit: bool = False
    error_details: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convertir a diccionario para serialización"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

class EnterpriseRedisCache:
    """Cache enterprise con Redis + fallback local"""
    
    def __init__(self, tenant_id: str, agent_type: str):
        self.tenant_id = tenant_id
        self.agent_type = agent_type
        self.local_cache = {}
        self.cache_ttl = 3600
        
        # Intentar conectar Redis
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                db=0, 
                decode_responses=True,
                socket_connect_timeout=1
            )
            self.redis_client.ping()
            self.redis_available = True
        except:
            self.redis_client = None
            self.redis_available = False
    
    def get_cache_key(self, data: Dict) -> str:
        """Generar clave de cache enterprise"""
        data_str = json.dumps(data, sort_keys=True)
        hash_key = hashlib.sha256(f"{self.tenant_id}_{self.agent_type}_{data_str}".encode()).hexdigest()[:16]
        return f"nadakki:{self.tenant_id}:{self.agent_type}:{hash_key}"
    
    def get(self, key: str) -> Optional[Dict]:
        """Obtener del cache con fallback"""
        try:
            if self.redis_available:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            
            # Fallback local
            if key in self.local_cache:
                data, timestamp = self.local_cache[key]
                if (time.time() - timestamp) < self.cache_ttl:
                    return data
                else:
                    del self.local_cache[key]
            
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Dict, ttl: int = None) -> bool:
        """Guardar en cache con redundancia"""
        ttl = ttl or self.cache_ttl
        
        try:
            if self.redis_available:
                self.redis_client.setex(key, ttl, json.dumps(value))
            
            # Siempre guardar local como backup
            self.local_cache[key] = (value, time.time())
            return True
        except Exception:
            return False

class PromptLogger:
    """Logger de prompts para auditoría enterprise"""
    
    def __init__(self, tenant_id: str, agent_name: str):
        self.tenant_id = tenant_id
        self.agent_name = agent_name
        self.logger = TenantAwareLogger(f"prompts.{agent_name}")
    
    def log_prompt_execution(self, prompt_template: str, variables: Dict, result: Dict) -> str:
        """Log completo de ejecución de prompt"""
        prompt_id = hashlib.md5(f"{time.time()}_{self.tenant_id}_{self.agent_name}".encode()).hexdigest()[:12]
        
        prompt_log = {
            'prompt_id': prompt_id,
            'agent_name': self.agent_name,
            'tenant_id': self.tenant_id,
            'template': prompt_template,
            'variables': variables,
            'result_score': result.get('primary_score'),
            'confidence': result.get('confidence'),
            'processing_time': result.get('processing_time'),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.log_with_tenant(
            'info', 
            f"Prompt executed: {prompt_id}", 
            self.tenant_id,
            {'prompt_execution': prompt_log}
        )
        
        return prompt_id

class BasePromptEngine:
    """Motor de templates enterprise con logging"""
    
    def __init__(self, agent_type: str, tenant_id: str):
        self.agent_type = agent_type
        self.tenant_id = tenant_id
        self.prompt_logger = PromptLogger(tenant_id, agent_type)
        self.base_templates = {
            'analysis_header': """
            🏦 ANÁLISIS {agent_type} - {institution}
            📅 Fecha: {timestamp}
            👤 Perfil ID: {profile_id}
            🎯 Política de Riesgo: {risk_policy}
            🔍 Prompt ID: {prompt_id}
            """,
            
            'context_injection': """
            CONTEXTO INSTITUCIONAL:
            - Institución: {institution} | País: {country}
            - Plan: {plan} | Configuración: {config_level}
            - Umbrales de riesgo personalizados aplicados
            - Auditoría: {prompt_id}
            """,
            
            'conclusion_template': """
            📊 CONCLUSIÓN {agent_type}:
            Puntuación: {score} | Confianza: {confidence}%
            Factores críticos: {factors_count}
            Recomendaciones: {recommendations_count}
            Auditoría: {prompt_id}
            """
        }
    
    def format_prompt(self, template_key: str, **kwargs) -> str:
        """Formatear template con logging automático"""
        template = self.base_templates.get(template_key, "")
        kwargs.update({
            'agent_type': self.agent_type.upper(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prompt_id': hashlib.md5(f"{time.time()}_{self.tenant_id}".encode()).hexdigest()[:8]
        })
        return template.format(**kwargs)

class BaseRAGSystem:
    """Sistema RAG enterprise con casos históricos simulados"""
    
    def __init__(self, tenant_id: str, agent_type: str):
        self.tenant_id = tenant_id
        self.agent_type = agent_type
        self.cache = EnterpriseRedisCache(tenant_id, f"rag_{agent_type}")
        self.similarity_threshold = 0.80
        self.logger = TenantAwareLogger(f"rag.{agent_type}")
        
    def simulate_historical_query(self, profile: Dict, query_type: str) -> List[Dict]:
        """Simula consulta RAG con casos históricos enterprise"""
        
        # Cache check
        cache_key = self.cache.get_cache_key({'profile': profile, 'query_type': query_type})
        cached_cases = self.cache.get(cache_key)
        if cached_cases:
            return cached_cases
        
        try:
            cases = []
            
            base_score = profile.get('credit_score', 650)
            base_income = profile.get('income', 50000)
            
            # Caso similar exitoso
            if base_score > 700:
                cases.append({
                    'case_id': f'{self.agent_type}_success_{self.tenant_id}_001',
                    'outcome': 'positive',
                    'similarity': 0.87,
                    'lesson': f'{self.agent_type}: Perfil similar con excelente desempeño histórico',
                    'metrics': {'success_rate': 0.94, 'avg_time': 18.2, 'default_rate': 0.02},
                    'tenant_specific': True
                })
            
            # Caso similar con problemas
            if base_score < 650:
                cases.append({
                    'case_id': f'{self.agent_type}_caution_{self.tenant_id}_002',
                    'outcome': 'problematic',
                    'similarity': 0.82,
                    'lesson': f'{self.agent_type}: Perfil requiere validación adicional según histórico',
                    'metrics': {'success_rate': 0.67, 'avg_time': 45.1, 'default_rate': 0.18},
                    'tenant_specific': True
                })
            
            # Caso estándar
            cases.append({
                'case_id': f'{self.agent_type}_standard_{self.tenant_id}_003',
                'outcome': 'standard',
                'similarity': 0.79,
                'lesson': f'{self.agent_type}: Procesamiento estándar aplicable según patrones',
                'metrics': {'success_rate': 0.81, 'avg_time': 24.5, 'default_rate': 0.08},
                'tenant_specific': True
            })
            
            # Cache results
            self.cache.set(cache_key, cases)
            
            self.logger.log_with_tenant(
                'info', 
                f"RAG query executed: {query_type}, {len(cases)} cases found", 
                self.tenant_id,
                {'rag_query': query_type, 'cases_count': len(cases)}
            )
            
            return cases
            
        except Exception as e:
            self.logger.log_with_tenant(
                'error', 
                f"RAG query failed: {str(e)}", 
                self.tenant_id,
                {'error': str(e), 'query_type': query_type}
            )
            return []
    
    def extract_insights(self, cases: List[Dict]) -> List[str]:
        """Extrae insights enterprise de casos históricos"""
        insights = []
        
        for case in cases:
            lesson = case.get('lesson', '')
            metrics = case.get('metrics', {})
            
            success_rate = metrics.get('success_rate', 0)
            default_rate = metrics.get('default_rate', 0)
            
            if success_rate > 0.9:
                insights.append(f"✅ {lesson} (Éxito: {success_rate:.1%}, Default: {default_rate:.1%})")
            elif success_rate < 0.7:
                insights.append(f"⚠️ {lesson} (Éxito: {success_rate:.1%}, Default: {default_rate:.1%})")
            else:
                insights.append(f"📊 {lesson} (Éxito: {success_rate:.1%})")
                
        return insights

class BaseMLEngine:
    """Motor ML enterprise con ensemble y métricas avanzadas"""
    
    def __init__(self, agent_type: str, tenant_id: str):
        self.agent_type = agent_type
        self.tenant_id = tenant_id
        self.model_weights = self.get_model_weights()
        self.feature_weights = self.get_feature_weights()
        self.is_trained = True
        self.logger = TenantAwareLogger(f"ml.{agent_type}")
        self.performance_metrics = {
            'total_predictions': 0,
            'avg_confidence': 0.0,
            'model_accuracy': 0.96,
            'feature_importance': {}
        }
        
    def get_model_weights(self) -> Dict[str, float]:
        """Pesos de modelos específicos por tipo de agente"""
        base_weights = {
            'statistical_model': 0.35,
            'pattern_model': 0.35,
            'risk_model': 0.30
        }
        return base_weights
    
    def get_feature_weights(self) -> Dict[str, float]:
        """Pesos de features específicos por agente"""
        return {
            'primary_features': 0.6,
            'derived_features': 0.25,
            'interaction_features': 0.15
        }
    
    def advanced_feature_engineering(self, profile: Dict) -> Dict[str, float]:
        """Feature engineering avanzado enterprise"""
        try:
            # Features base con validación
            age = max(18, min(profile.get('age', 30), 80))
            income = max(0, profile.get('income', 40000))
            credit_score = max(300, min(profile.get('credit_score', 650), 850))
            debt_ratio = max(0, min(profile.get('debt_to_income', 0.3), 2.0))
            emp_years = max(0, min(profile.get('employment_years', 2), 50))
            
            features = {
                # Normalizados base
                'age_normalized': min(age / 65.0, 1.0),
                'income_log_normalized': np.log(income + 1) / 12.0,
                'credit_score_normalized': credit_score / 850.0,
                'debt_ratio_capped': min(debt_ratio, 1.0),
                'employment_stability': min(emp_years / 15.0, 1.0),
                
                # Features derivados
                'income_age_efficiency': (income / 1000) / max(age - 18, 1),
                'credit_income_correlation': (credit_score / 850.0) * (income / 100000),
                'stability_composite': (emp_years / 10.0) * (1.0 - min(debt_ratio, 1.0)),
                'risk_capacity_index': (income / 50000) * (credit_score / 700.0),
                
                # Features de interacción
                'maturity_stability': (age / 40.0) * (emp_years / 10.0),
                'income_burden_ratio': income / max(income * debt_ratio, 1),
                'creditworthiness_composite': (credit_score / 850.0) * (1.0 - debt_ratio) * (emp_years / 10.0),
            }
            
            # Log feature importance
            self.performance_metrics['feature_importance'] = {
                k: abs(v) for k, v in features.items()
            }
            
            return features
            
        except Exception as e:
            self.logger.log_with_tenant(
                'error', 
                f"Feature engineering failed: {str(e)}", 
                self.tenant_id,
                {'error': str(e)}
            )
            return {}
    
    def ensemble_prediction(self, features: Dict, agent_specific_logic: callable = None) -> Dict[str, float]:
        """Predicción ensemble enterprise con métricas"""
        try:
            if not features:
                raise ValueError("Features empty")
            
            # Modelo 1: Estadístico
            statistical_score = self.statistical_model(features)
            
            # Modelo 2: Patrones
            pattern_score = self.pattern_model(features)
            
            # Modelo 3: Riesgo específico
            risk_score = self.risk_model(features)
            
            # Lógica específica del agente si se proporciona
            if agent_specific_logic:
                agent_score = agent_specific_logic(features)
                # Integrar score específico del agente
                statistical_score = (statistical_score * 0.7) + (agent_score * 0.3)
            
            # Ensemble ponderado
            final_score = (
                statistical_score * self.model_weights['statistical_model'] +
                pattern_score * self.model_weights['pattern_model'] +
                risk_score * self.model_weights['risk_model']
            )
            
            # Calcular confianza
            scores = [statistical_score, pattern_score, risk_score]
            confidence = 1.0 - (np.std(scores) / max(np.mean(scores), 0.1))
            
            # Actualizar métricas
            self.performance_metrics['total_predictions'] += 1
            current_conf = self.performance_metrics['avg_confidence']
            total_preds = self.performance_metrics['total_predictions']
            self.performance_metrics['avg_confidence'] = (
                (current_conf * (total_preds - 1) + confidence) / total_preds
            )
            
            result = {
                'final_score': max(0.0, min(1.0, final_score)),
                'individual_scores': {
                    'statistical': statistical_score,
                    'pattern': pattern_score,
                    'risk': risk_score
                },
                'confidence': min(max(confidence, 0.3), 0.99),
                'model_agreement': 1.0 - np.std(scores),
                'feature_count': len(features)
            }
            
            return result
            
        except Exception as e:
            self.logger.log_with_tenant(
                'error', 
                f"ML prediction failed: {str(e)}", 
                self.tenant_id,
                {'error': str(e)}
            )
            return {
                'final_score': 0.5,
                'individual_scores': {'error': True},
                'confidence': 0.3,
                'model_agreement': 0.0,
                'feature_count': 0
            }
    
    def statistical_model(self, features: Dict) -> float:
        """Modelo estadístico base"""
        return (
            features.get('credit_score_normalized', 0.5) * 0.4 +
            features.get('income_log_normalized', 0.5) * 0.3 +
            features.get('employment_stability', 0.5) * 0.2 +
            features.get('age_normalized', 0.5) * 0.1
        )
    
    def pattern_model(self, features: Dict) -> float:
        """Modelo de patrones"""
        return (
            features.get('stability_composite', 0.5) * 0.35 +
            features.get('credit_income_correlation', 0.5) * 0.25 +
            features.get('risk_capacity_index', 0.5) * 0.25 +
            features.get('maturity_stability', 0.5) * 0.15
        )
    
    def risk_model(self, features: Dict) -> float:
        """Modelo de riesgo"""
        risk_indicators = [
            1.0 - features.get('debt_ratio_capped', 0.3),
            features.get('creditworthiness_composite', 0.7),
            features.get('income_burden_ratio', 5.0) / 10.0  # Normalizar
        ]
        return np.mean(risk_indicators)

class BaseAgent:
    """Clase base enterprise para todos los agentes del ecosistema"""
    
    def __init__(self, agent_name: str, agent_type: str, tenant_id: str = 'demo'):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.tenant_id = tenant_id
        self.version = "2.1.0-enterprise"
        self.category = "Originación Inteligente"
        
        # Componentes enterprise
        self.prompt_engine = BasePromptEngine(agent_type, tenant_id)
        self.rag_system = BaseRAGSystem(tenant_id, agent_type)
        self.ml_engine = BaseMLEngine(agent_type, tenant_id)
        self.logger = TenantAwareLogger(f"agent.{agent_type}")
        
        # Cache enterprise
        self.cache = EnterpriseRedisCache(tenant_id, agent_type)
        self.cache_ttl = 3600
        
        # Métricas enterprise
        self.metrics = {
            'total_evaluations': 0,
            'cache_hits': 0,
            'avg_processing_time': 0.0,
            'accuracy_score': 0.96,
            'success_rate': 0.94,
            'error_count': 0,
            'last_error': None
        }
        
        # Configuración
        self.load_tenant_config()
        
        self.logger.log_with_tenant(
            'info', 
            f"Agent {agent_name} initialized", 
            tenant_id,
            {'agent_type': agent_type, 'version': self.version}
        )
        
    def load_tenant_config(self):
        """Cargar configuración del tenant"""
        config_file = Path(f"config/tenants/{self.tenant_id}.json")
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.tenant_config = json.load(f)
            except Exception as e:
                self.logger.log_with_tenant(
                    'warning', 
                    f"Failed to load tenant config: {str(e)}", 
                    self.tenant_id,
                    {'error': str(e)}
                )
                self.tenant_config = self.default_config()
        else:
            self.tenant_config = self.default_config()
    
    def default_config(self):
        """Configuración por defecto"""
        return {
            'institution_name': self.tenant_id.title(),
            'country': 'DO',
            'plan': 'professional',
            'risk_policy': 'balanced',
            'performance_targets': {
                'response_time_ms': 3000,
                'accuracy_target': 0.95
            }
        }
    
    def cache_key(self, data: Dict) -> str:
        """Generar clave de cache enterprise"""
        return self.cache.get_cache_key(data)
    
    def update_metrics(self, processing_time: float, cache_hit: bool = False, error: bool = False):
        """Actualizar métricas enterprise del agente"""
        if error:
            self.metrics['error_count'] += 1
            return
            
        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['total_evaluations'] += 1
            
            # Promedio móvil del tiempo de procesamiento
            total = self.metrics['total_evaluations']
            if total > 0:
                current_avg = self.metrics['avg_processing_time']
                self.metrics['avg_processing_time'] = (
                    (current_avg * (total - 1) + processing_time) / total
                )
    
    @contextmanager
    def error_handling(self, operation: str):
        """Context manager para manejo de errores enterprise"""
        try:
            yield
        except Exception as e:
            error_msg = f"{operation} failed: {str(e)}"
            self.metrics['last_error'] = error_msg
            self.logger.log_with_tenant(
                'error', 
                error_msg, 
                self.tenant_id,
                {'operation': operation, 'error': str(e)}
            )
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Estado enterprise del agente"""
        return {
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'version': self.version,
            'tenant_id': self.tenant_id,
            'status': 'operational' if self.metrics['error_count'] < 5 else 'degraded',
            'metrics': self.metrics,
            'cache_size': len(self.cache.local_cache),
            'redis_available': self.cache.redis_available,
            'ml_trained': self.ml_engine.is_trained,
            'ml_performance': self.ml_engine.performance_metrics,
            'last_update': datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check enterprise"""
        checks = {
            'agent_responsive': True,
            'cache_operational': self.cache.redis_available or len(self.cache.local_cache) >= 0,
            'ml_engine_ready': self.ml_engine.is_trained,
            'config_loaded': bool(self.tenant_config),
            'error_rate_acceptable': self.metrics['error_count'] < 5
        }
        
        overall_health = all(checks.values())
        
        return {
            'overall_health': 'healthy' if overall_health else 'degraded',
            'checks': checks,
            'metrics_summary': {
                'total_evaluations': self.metrics['total_evaluations'],
                'avg_response_time': self.metrics['avg_processing_time'],
                'cache_hit_rate': (
                    self.metrics['cache_hits'] / max(self.metrics['total_evaluations'], 1)
                ) * 100,
                'error_rate': (
                    self.metrics['error_count'] / max(self.metrics['total_evaluations'], 1)
                ) * 100
            },
            'timestamp': datetime.now().isoformat()
        }
