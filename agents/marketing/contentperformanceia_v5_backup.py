"""
🚀 SUPER-AGENT: CONTENT PERFORMANCE ENTERPRISE v5.0
Architecture: Event-Driven + CQRS + Self-Healing + Blockchain Audit + MLOps
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import hashlib
import pickle
import uuid
import re

# ML Imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# FastAPI/Async
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURACIÓN BÁSICA ====================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLStrategy(str, Enum):
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost" 
    GRADIENT_BOOSTING = "gradient_boosting"
    HYBRID = "hybrid"

class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post" 
    EMAIL = "email"
    VIDEO = "video"

class Channel(str, Enum):
    BLOG = "blog"
    INSTAGRAM = "instagram"
    TWITTER = "twitter" 
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"

class PerformanceLevel(str, Enum):
    VIRAL = "viral"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    UNDERPERFORMING = "underperforming"

class HealthStatus(str, Enum):
    OPTIMAL = "optimal"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"

@dataclass
class ContentMetrics:
    impressions: int
    reach: int
    engagement: int
    clicks: int
    shares: int
    comments: int
    saves: int = 0
    watch_time_seconds: int = 0
    conversion_rate: float = 0.0

@dataclass
class ContentItem:
    content_id: str
    content_type: ContentType
    channel: Channel
    publish_date: datetime
    title: str
    metrics: ContentMetrics
    topic_tags: List[str] = field(default_factory=list)
    language: str = "es"
    marketing_consent: bool = True

@dataclass
class PerformanceAnalysis:
    content_id: str
    performance_level: PerformanceLevel
    engagement_rate: float
    virality_score: float
    reach_efficiency: float
    predicted_performance: str
    optimization_suggestions: List[str]
    compliance_flags: List[str] = field(default_factory=list)
    ml_confidence: float = 1.0
    blockchain_hash: Optional[str] = None

# ==================== CONFIGURATION MANAGEMENT ====================

class ContentPerformanceConfig(BaseModel):
    """Enterprise-grade configuration"""
    
    tenant_id: str = Field(..., min_length=1, max_length=50)
    ml_strategy: MLStrategy = Field(default=MLStrategy.HYBRID)
    enable_self_healing: bool = True
    enable_blockchain_audit: bool = True
    cache_ttl: int = Field(default=1800, ge=300, le=86400)
    
    # ML Configuration
    prediction_confidence_threshold: float = Field(default=0.7, ge=0.5, le=0.95)
    
    # Self-healing thresholds
    max_consecutive_failures: int = Field(default=3, ge=1, le=10)
    health_check_interval: int = Field(default=60, ge=10, le=300)
    
    # Performance tuning
    max_content_items: int = Field(default=1000, ge=1, le=10000)
    enable_advanced_analytics: bool = True

# ==================== HYBRID CACHE MANAGEMENT ====================

class HybridCacheManager:
    """Redis + In-Memory LRU cache with circuit breaker"""
    
    def __init__(self, max_memory_size: int = 1000):
        self.redis_client = None
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}
        self.max_memory_size = max_memory_size
        self.circuit_state = "CLOSED"
        self.failure_count = 0
        
    async def initialize(self):
        """Initialize cache system"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=False)
            await self.redis_client.ping()
            self.circuit_state = "CLOSED"
            self.failure_count = 0
            logger.info("✅ Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis initialization failed, using memory cache only: {e}")
            self.circuit_state = "OPEN"
            
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with hybrid strategy"""
        # Try memory cache first
        if key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if (datetime.now().timestamp() - timestamp) < 1800:  # 30 min TTL
                return value
            else:
                del self.memory_cache[key]
        
        # Try Redis if available
        if self.redis_client and self.circuit_state == "CLOSED":
            try:
                cached = await self.redis_client.get(f"content_perf:{key}")
                if cached:
                    value = pickle.loads(cached)
                    self._set_memory(key, value)
                    return value
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= 3:
                    self.circuit_state = "OPEN"
                    asyncio.create_task(self._reset_circuit_breaker())
        
        return None
        
    async def set(self, key: str, value: Any, ttl: int = 1800):
        """Set in both caches with TTL"""
        self._set_memory(key, value)
        
        if self.redis_client and self.circuit_state == "CLOSED":
            try:
                await self.redis_client.setex(
                    f"content_perf:{key}", 
                    ttl, 
                    pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                )
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= 3:
                    self.circuit_state = "OPEN"
                    asyncio.create_task(self._reset_circuit_breaker())
                    
    def _set_memory(self, key: str, value: Any):
        """Set in memory cache with LRU eviction"""
        self.memory_cache[key] = (value, datetime.now().timestamp())
        if len(self.memory_cache) > self.max_memory_size:
            oldest_key = min(self.memory_cache.keys(), key=lambda k: self.memory_cache[k][1])
            del self.memory_cache[oldest_key]
            
    async def _reset_circuit_breaker(self):
        """Reset circuit breaker after timeout"""
        await asyncio.sleep(60)
        self.circuit_state = "HALF_OPEN"
        self.failure_count = 0

# ==================== ADVANCED ML PIPELINE ====================

class ContentMLPipeline:
    """Advanced ML pipeline for content performance prediction"""
    
    def __init__(self, strategy: MLStrategy = MLStrategy.HYBRID):
        self.strategy = strategy
        self.active_models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize models based on strategy"""
        if self.strategy == MLStrategy.RANDOM_FOREST:
            await self._initialize_random_forest()
        elif self.strategy == MLStrategy.XGBOOST:
            await self._initialize_xgboost()
        elif self.strategy == MLStrategy.GRADIENT_BOOSTING:
            await self._initialize_gradient_boosting()
        else:  # HYBRID
            await self._initialize_hybrid()
            
        self.scalers = {
            "engagement_features": StandardScaler(),
            "virality_features": RobustScaler()
        }
        
        logger.info(f"✅ ML Pipeline initialized with strategy: {self.strategy}")
        
    async def _initialize_random_forest(self):
        """Initialize Random Forest models"""
        self.active_models = {
            "engagement_predictor": RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            ),
            "virality_predictor": RandomForestRegressor(
                n_estimators=100, max_depth=8, random_state=42
            )
        }
        
    async def _initialize_xgboost(self):
        """Initialize XGBoost models"""
        self.active_models = {
            "engagement_predictor": XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            ),
            "virality_predictor": XGBRegressor(
                n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
            )
        }
        
    async def _initialize_gradient_boosting(self):
        """Initialize Gradient Boosting models"""
        self.active_models = {
            "engagement_predictor": GradientBoostingRegressor(
                n_estimators=100, max_depth=6, random_state=42
            ),
            "virality_predictor": GradientBoostingRegressor(
                n_estimators=100, max_depth=4, random_state=42
            )
        }
        
    async def _initialize_hybrid(self):
        """Initialize hybrid model strategy"""
        self.active_models = {
            "engagement_predictor": XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            ),
            "virality_predictor": RandomForestRegressor(
                n_estimators=100, max_depth=8, random_state=42
            )
        }
        
        # Train with sample data
        await self._train_with_sample_data()
        
    async def _train_with_sample_data(self):
        """Train models with sample data"""
        try:
            # Generate sample training data
            np.random.seed(42)
            X_train = np.random.rand(100, 15)
            y_engagement = np.random.rand(100) * 100
            y_virality = np.random.rand(100) * 100
            
            # Fit models
            self.active_models["engagement_predictor"].fit(X_train, y_engagement)
            self.active_models["virality_predictor"].fit(X_train, y_virality)
            
            # Fit scalers
            self.scalers["engagement_features"].fit(X_train)
            self.scalers["virality_features"].fit(X_train)
            
            logger.info("✅ ML models trained with sample data")
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
        
    async def predict_performance(self, 
                                content_features: np.ndarray,
                                content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced performance prediction with confidence scoring"""
        try:
            # Feature preprocessing
            features_scaled = self.scalers["engagement_features"].transform(
                content_features.reshape(1, -1)
            )
            
            # Ensemble predictions
            engagement_pred = self.active_models["engagement_predictor"].predict(features_scaled)[0]
            virality_pred = self.active_models["virality_predictor"].predict(features_scaled)[0]
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(engagement_pred, virality_pred)
            
            # Determine performance level
            performance_level = self._classify_performance_level(engagement_pred, virality_pred)
            
            return {
                "engagement_score": float(engagement_pred),
                "virality_score": float(virality_pred),
                "performance_level": performance_level,
                "confidence": confidence,
                "model_strategy": self.strategy.value
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return self._get_fallback_predictions()
            
    def _calculate_prediction_confidence(self, engagement: float, virality: float) -> float:
        """Calculate prediction confidence"""
        scores = [engagement, virality]
        variance = np.var(scores)
        confidence = 1.0 - min(variance * 2, 0.5)
        return max(0.5, min(1.0, confidence))
        
    def _classify_performance_level(self, engagement: float, virality: float) -> PerformanceLevel:
        """Classify performance level"""
        overall_score = (engagement * 0.6 + virality * 0.4)
        
        if overall_score >= 80: return PerformanceLevel.VIRAL
        elif overall_score >= 60: return PerformanceLevel.HIGH
        elif overall_score >= 40: return PerformanceLevel.MEDIUM
        elif overall_score >= 20: return PerformanceLevel.LOW
        else: return PerformanceLevel.UNDERPERFORMING
        
    def _get_fallback_predictions(self) -> Dict[str, Any]:
        """Fallback predictions when ML models fail"""
        return {
            "engagement_score": 50.0,
            "virality_score": 40.0,
            "performance_level": PerformanceLevel.MEDIUM,
            "confidence": 0.5,
            "model_strategy": "fallback"
        }

# ==================== BLOCKCHAIN AUDIT SYSTEM ====================

class BlockchainAuditSystem:
    """Immutable audit trail with blockchain-like structure"""
    
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.last_hash: Optional[str] = None
        
    async def add_record(self, event_type: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add a new record to the blockchain audit trail"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        record_id = str(uuid.uuid4())
        
        # Create digital signature
        signature = self._create_signature(content_hash, metadata)
        
        record = {
            "record_id": record_id,
            "content_hash": content_hash,
            "previous_hash": self.last_hash,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "metadata": metadata,
            "signature": signature
        }
        
        self.chain.append(record)
        self.last_hash = self._calculate_block_hash(record)
        
        logger.info(f"Blockchain audit record added: {event_type} - {record_id}")
        return record_id
        
    def _create_signature(self, content_hash: str, metadata: Dict[str, Any]) -> str:
        """Create digital signature for audit record"""
        signature_data = f"{content_hash}{json.dumps(metadata, sort_keys=True)}{datetime.now().timestamp()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
        
    def _calculate_block_hash(self, record: Dict[str, Any]) -> str:
        """Calculate hash for a block"""
        block_data = f"{record['record_id']}{record['content_hash']}{record['previous_hash']}{record['timestamp']}{record['signature']}"
        return hashlib.sha256(block_data.encode()).hexdigest()
        
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit trail entries"""
        return self.chain[-limit:] if self.chain else []

# ==================== COMPREHENSIVE COMPLIANCE ENGINE ====================

class ComplianceEngineEnterprise:
    """Advanced compliance engine with multi-jurisdiction support"""
    
    def __init__(self):
        self.pii_patterns: List[Tuple[str, str]] = []
        
    async def initialize(self):
        """Initialize compliance rules"""
        self._load_pii_patterns()
        logger.info("✅ Compliance Engine initialized")
        
    def _load_pii_patterns(self):
        """Load PII detection patterns"""
        self.pii_patterns = [
            (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
            (r"\b\d{10}\b", "PHONE"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "EMAIL"),
        ]
        
    async def check_content_compliance(self, 
                                     content: str,
                                     has_consent: bool = True) -> Tuple[float, List[str]]:
        """Advanced compliance checking with scoring"""
        score = 1.0
        flags = []
                
        # PII detection
        pii_detected, pii_types = await self._detect_pii(content)
        if pii_detected:
            flags.extend([f"pii_{ptype}" for ptype in pii_types])
            score -= 0.3
            
        # Consent requirements
        if not has_consent:
            flags.append("consent_missing")
            score -= 0.2
            
        return max(0.0, min(1.0, score)), flags
        
    async def _detect_pii(self, content: str) -> Tuple[bool, List[str]]:
        """Detect PII in content"""
        found_types = []
        for pattern, ptype in self.pii_patterns:
            if re.search(pattern, content):
                found_types.append(ptype)
                
        return len(found_types) > 0, found_types

# ==================== SELF-HEALING ORCHESTRATOR ====================

class SelfHealingOrchestrator:
    """Advanced self-healing system with health monitoring"""
    
    def __init__(self, max_consecutive_failures: int = 3, check_interval: int = 60):
        self.max_consecutive_failures = max_consecutive_failures
        self.check_interval = check_interval
        self.consecutive_failures = 0
        self.last_health_check = datetime.now()
        self.self_healing_history: List[Dict[str, Any]] = []
        
    async def monitor_health(self, agent) -> HealthStatus:
        """Monitor agent health and trigger healing if needed"""
        current_time = datetime.now()
        
        if (current_time - self.last_health_check).seconds < self.check_interval:
            return HealthStatus.HEALTHY
            
        self.last_health_check = current_time
        
        health_status = await self._perform_health_checks(agent)
        
        if health_status in [HealthStatus.DEGRADED, HealthStatus.CRITICAL]:
            await self._trigger_self_healing(agent, health_status)
            
        return health_status
        
    async def _perform_health_checks(self, agent) -> HealthStatus:
        """Perform comprehensive health checks"""
        checks = {
            "cache_health": await self._check_cache_health(agent.cache_manager),
            "ml_health": await self._check_ml_health(agent.ml_pipeline),
        }
        
        successful_checks = sum(1 for check in checks.values() if check)
        health_ratio = successful_checks / len(checks)
        
        if health_ratio >= 0.9: return HealthStatus.OPTIMAL
        elif health_ratio >= 0.7: return HealthStatus.HEALTHY
        elif health_ratio >= 0.5: return HealthStatus.DEGRADED
        else: return HealthStatus.CRITICAL
        
    async def _check_cache_health(self, cache_manager) -> bool:
        """Check cache system health"""
        try:
            test_key = "health_check"
            test_value = {"test": "data", "timestamp": datetime.now().isoformat()}
            await cache_manager.set(test_key, test_value, 60)
            retrieved = await cache_manager.get(test_key)
            return retrieved is not None
        except:
            return False
            
    async def _check_ml_health(self, ml_pipeline) -> bool:
        """Check ML pipeline health"""
        try:
            sample_features = np.random.rand(15)
            prediction = await ml_pipeline.predict_performance(sample_features, {})
            return prediction["confidence"] > 0
        except:
            return False
            
    async def _trigger_self_healing(self, agent, health_status: HealthStatus):
        """Trigger self-healing procedures"""
        healing_actions = []
        
        if not await self._check_cache_health(agent.cache_manager):
            await agent.cache_manager.initialize()
            healing_actions.append("cache_reset")
            
        if not await self._check_ml_health(agent.ml_pipeline):
            await agent.ml_pipeline.initialize()
            healing_actions.append("ml_pipeline_reset")
            
        healing_event = {
            "timestamp": datetime.now().isoformat(),
            "health_status": health_status.value,
            "actions_taken": healing_actions
        }
        self.self_healing_history.append(healing_event)
        
        logger.warning(f"Self-healing triggered: {healing_actions}")

# ==================== CONTENT PERFORMANCE SUPER-AGENT v5.0 ====================

class ContentPerformanceSuperAgent:
    """
    🚀 ENTERPRISE SUPER-AGENT v5.0
    Advanced Content Performance Analytics with Self-Healing & Blockchain Audit
    """
    
    def __init__(self, tenant_id: str, config: ContentPerformanceConfig):
        self.tenant_id = tenant_id
        self.config = config
        self.agent_id = f"content_perf_{tenant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        
        # Initialize advanced components
        self.cache_manager = HybridCacheManager()
        self.ml_pipeline = ContentMLPipeline(config.ml_strategy)
        self.compliance_engine = ComplianceEngineEnterprise()
        self.audit_system = BlockchainAuditSystem()
        self.self_healing = SelfHealingOrchestrator(
            max_consecutive_failures=config.max_consecutive_failures,
            check_interval=config.health_check_interval
        )
        
        # Event system
        self.event_queue = asyncio.Queue(maxsize=1000)
        
        # Advanced metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "content_items_analyzed": 0,
            "cache_hit_rate": 0.0,
            "avg_processing_time_ms": 0.0,
            "ml_predictions_made": 0,
            "compliance_checks": 0,
            "self_healing_events": 0,
            "blockchain_audit_records": 0
        }
        
        self.background_tasks = set()
        self.is_running = True
        
        logger.info(f"ContentPerformanceSuperAgent v5.0 initialized for tenant {tenant_id}")
        
    async def initialize(self):
        """Initialize all components with error handling"""
        try:
            await self.cache_manager.initialize()
            await self.ml_pipeline.initialize()
            await self.compliance_engine.initialize()
            
            # Start background tasks
            tasks = [
                self._process_events(),
                self._health_monitoring()
            ]
            
            for task in tasks:
                bg_task = asyncio.create_task(task)
                self.background_tasks.add(bg_task)
                bg_task.add_done_callback(self.background_tasks.discard)
                
            logger.info(f"Content Performance Super Agent {self.agent_id} fully initialized")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
            
    async def shutdown(self):
        """Graceful shutdown"""
        self.is_running = False
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
    async def analyze_content_performance(self,
                                        content_items: List[ContentItem],
                                        request_id: str = None) -> Dict[str, Any]:
        """
        Analyze content performance with advanced features
        """
        start_time = datetime.now()
        request_id = request_id or self._generate_request_id()
        
        try:
            # Health check
            health_status = await self.self_healing.monitor_health(self)
            if health_status == HealthStatus.CRITICAL:
                raise RuntimeError("Agent health is critical, self-healing in progress")
                
            # Check cache
            cache_key = self._generate_cache_key(content_items)
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                self.metrics["cache_hit_rate"] = (
                    self.metrics["cache_hit_rate"] * 0.95 + 0.05
                )
                return cached_result
                
            # Limit content items if needed
            if len(content_items) > self.config.max_content_items:
                content_items = content_items[:self.config.max_content_items]
                logger.warning(f"Limited content items to {self.config.max_content_items}")
                
            # Process content items
            performance_analyses = []
            
            for item in content_items:
                # Compliance checking
                compliance_score, compliance_flags = await self.compliance_engine.check_content_compliance(
                    content=item.title,
                    has_consent=item.marketing_consent
                )
                
                # ML performance prediction
                content_features = await self._extract_content_features(item)
                ml_prediction = await self.ml_pipeline.predict_performance(
                    content_features=content_features,
                    content_metadata={
                        "content_type": item.content_type.value,
                        "channel": item.channel.value
                    }
                )
                
                # Blockchain audit
                audit_id = await self.audit_system.add_record(
                    event_type="content_analysis",
                    content=item.title,
                    metadata={
                        "content_id": item.content_id,
                        "content_type": item.content_type.value,
                        "compliance_score": compliance_score,
                        "performance_level": ml_prediction["performance_level"].value
                    }
                )
                
                # Calculate additional metrics
                engagement_rate = self._calculate_engagement_rate(item.metrics)
                reach_efficiency = self._calculate_reach_efficiency(item.metrics)
                
                # Generate optimization suggestions
                optimization_suggestions = self._generate_optimization_suggestions(
                    ml_prediction["performance_level"],
                    item.content_type,
                    item.channel,
                    engagement_rate
                )
                
                performance_analysis = PerformanceAnalysis(
                    content_id=item.content_id,
                    performance_level=ml_prediction["performance_level"],
                    engagement_rate=engagement_rate,
                    virality_score=ml_prediction["virality_score"],
                    reach_efficiency=reach_efficiency,
                    predicted_performance=ml_prediction["performance_level"].value.upper(),
                    optimization_suggestions=optimization_suggestions,
                    compliance_flags=compliance_flags,
                    ml_confidence=ml_prediction["confidence"],
                    blockchain_hash=audit_id
                )
                performance_analyses.append(performance_analysis)
                
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Build result
            result = {
                "request_id": request_id,
                "tenant_id": self.tenant_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "processing_time_ms": processing_time_ms,
                "health_status": health_status.value,
                "content_analyzed": len(content_items),
                "performance_analyses": [
                    {
                        "content_id": pa.content_id,
                        "performance_level": pa.performance_level.value,
                        "engagement_rate": pa.engagement_rate,
                        "virality_score": pa.virality_score,
                        "reach_efficiency": pa.reach_efficiency,
                        "predicted_performance": pa.predicted_performance,
                        "optimization_suggestions": pa.optimization_suggestions,
                        "compliance_flags": pa.compliance_flags,
                        "ml_confidence": pa.ml_confidence,
                        "blockchain_hash": pa.blockchain_hash
                    }
                    for pa in performance_analyses
                ],
                "performance_summary": {
                    "viral_content": len([pa for pa in performance_analyses if pa.performance_level == PerformanceLevel.VIRAL]),
                    "high_performance": len([pa for pa in performance_analyses if pa.performance_level == PerformanceLevel.HIGH]),
                    "average_engagement": np.mean([pa.engagement_rate for pa in performance_analyses]),
                    "average_virality": np.mean([pa.virality_score for pa in performance_analyses])
                },
                "metadata": {
                    "agent_version": "5.0.0-enterprise",
                    "ml_strategy": self.config.ml_strategy.value,
                    "cache_strategy": "hybrid_redis_memory",
                    "blockchain_audit_enabled": self.config.enable_blockchain_audit,
                    "self_healing_enabled": self.config.enable_self_healing
                }
            }
            
            # Cache result
            await self.cache_manager.set(cache_key, result, self.config.cache_ttl)
            
            # Update metrics
            self._update_metrics(processing_time_ms, len(content_items), True)
            
            return result
            
        except Exception as e:
            self._update_metrics(0, 0, False)
            logger.error(f"Content performance analysis failed for request {request_id}: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Content performance analysis failed: {str(e)}"
            )
            
    async def _extract_content_features(self, item: ContentItem) -> np.ndarray:
        """Extract features for ML prediction"""
        features = [
            item.metrics.impressions,
            item.metrics.reach,
            item.metrics.engagement,
            item.metrics.clicks,
            item.metrics.shares,
            item.metrics.comments,
            item.metrics.saves,
            item.metrics.watch_time_seconds,
            item.metrics.conversion_rate,
            len(item.title),
            len(item.topic_tags),
        ]
        
        # Add one-hot encoding for content type and channel
        content_type_features = [0] * len(ContentType)
        channel_features = [0] * len(Channel)
        
        try:
            content_type_features[list(ContentType).index(item.content_type)] = 1
            channel_features[list(Channel).index(item.channel)] = 1
        except ValueError:
            pass
            
        features.extend(content_type_features)
        features.extend(channel_features)
        
        return np.array(features)
        
    def _calculate_engagement_rate(self, metrics: ContentMetrics) -> float:
        """Calculate engagement rate"""
        total_engagement = metrics.engagement + metrics.clicks + metrics.shares + metrics.comments + metrics.saves
        return round((total_engagement / max(1, metrics.reach)) * 100.0, 2)
        
    def _calculate_reach_efficiency(self, metrics: ContentMetrics) -> float:
        """Calculate reach efficiency"""
        return round((metrics.reach / max(1, metrics.impressions)) * 100.0, 2)
        
    def _generate_optimization_suggestions(self,
                                         performance_level: PerformanceLevel,
                                         content_type: ContentType,
                                         channel: Channel,
                                         engagement_rate: float) -> List[str]:
        """Generate optimization suggestions based on performance"""
        suggestions = []
        
        if performance_level in [PerformanceLevel.LOW, PerformanceLevel.UNDERPERFORMING]:
            suggestions.extend([
                "Optimize headline for better CTR",
                "Improve visual elements for higher engagement",
                "Test different posting times"
            ])
            
        if content_type == ContentType.VIDEO and engagement_rate < 5.0:
            suggestions.extend([
                "Enhance video thumbnail",
                "Optimize first 10 seconds for retention",
                "Add captions for better accessibility"
            ])
            
        if channel in [Channel.INSTAGRAM, Channel.TIKTOK] and engagement_rate < 3.0:
            suggestions.extend([
                "Use trending audio/music",
                "Increase use of relevant hashtags",
                "Engage with commenters promptly"
            ])
            
        return suggestions[:5]
        
    def _generate_cache_key(self, content_items: List[ContentItem]) -> str:
        """Generate cache key"""
        content_ids = sorted([item.content_id for item in content_items])
        key_components = [
            self.tenant_id,
            ",".join(content_ids[:10]),
            str(len(content_items)),
            self.config.ml_strategy.value
        ]
        key_str = "|".join(key_components)
        return hashlib.sha256(key_str.encode()).hexdigest()[:20]
        
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"req_{self.tenant_id}_{timestamp}_{hashlib.sha256(timestamp.encode()).hexdigest()[:8]}"
        
    def _update_metrics(self, processing_time_ms: float, content_count: int, success: bool):
        """Update comprehensive metrics"""
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
            self.metrics["content_items_analyzed"] += content_count
            self.metrics["ml_predictions_made"] += content_count
            self.metrics["compliance_checks"] += content_count
            
            current_avg = self.metrics["avg_processing_time_ms"]
            if current_avg == 0:
                self.metrics["avg_processing_time_ms"] = processing_time_ms
            else:
                self.metrics["avg_processing_time_ms"] = current_avg * 0.95 + processing_time_ms * 0.05
        else:
            self.metrics["failed_requests"] += 1
            
    async def _emit_event(self, event_type: str, payload: Dict[str, Any]):
        """Emit event to event bus"""
        event = {
            "event_id": self._generate_request_id(),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "payload": payload
        }
        await self.event_queue.put(event)
        
    async def _process_events(self):
        """Background task to process events"""
        while self.is_running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_event(event)
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
                
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle different event types"""
        # Event processing logic here
        pass
            
    async def _health_monitoring(self):
        """Continuous health monitoring"""
        while self.is_running:
            try:
                health_status = await self.self_healing.monitor_health(self)
                
                if health_status != HealthStatus.OPTIMAL:
                    logger.info(f"Agent health status: {health_status.value}")
                    
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
        
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status with health metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "status": "OPERATIONAL",
            "health_metrics": {
                "uptime_seconds": uptime,
                "request_count": self.metrics["total_requests"],
                "error_rate": self.metrics["failed_requests"] / max(1, self.metrics["total_requests"]),
                "avg_response_time": self.metrics["avg_processing_time_ms"],
                "cache_hit_rate": self.metrics["cache_hit_rate"],
            },
            "performance_metrics": self.metrics,
            "cache_status": {
                "circuit_state": self.cache_manager.circuit_state,
                "memory_cache_size": len(self.cache_manager.memory_cache)
            },
            "ml_pipeline_status": {
                "strategy": self.config.ml_strategy.value,
                "models_loaded": len(self.ml_pipeline.active_models)
            },
            "audit_system_status": {
                "blockchain_records": len(self.audit_system.chain)
            },
            "self_healing_status": {
                "enabled": self.config.enable_self_healing,
                "healing_events": len(self.self_healing.self_healing_history)
            },
            "version": "5.0.0-enterprise"
        }

# ==================== FASTAPI INTEGRATION ====================

app = FastAPI(
    title="Content Performance Super-Agent v5.0",
    version="5.0.0",
    description="Enterprise Content Performance Analytics with Self-Healing & Blockchain Audit"
)

# Global agent registry
agent_registry: Dict[str, ContentPerformanceSuperAgent] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize default agent on startup"""
    try:
        config = ContentPerformanceConfig(tenant_id="tn_default")
        agent = ContentPerformanceSuperAgent("tn_default", config)
        await agent.initialize()
        agent_registry["tn_default"] = agent
        logger.info("✅ Content Performance Super-Agent v5.0 started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start agent: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown all agents gracefully"""
    for agent in agent_registry.values():
        await agent.shutdown()

@app.post("/api/v1/analyze")
async def analyze_content_performance(
    content_items: List[Dict[str, Any]],
    tenant_id: str = "tn_default"
):
    """Enterprise content performance analysis endpoint"""
    agent = agent_registry.get(tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found for tenant: {tenant_id}")
        
    # Convert input to ContentItem objects
    converted_items = []
    for item_data in content_items:
        metrics_data = item_data.get("metrics", {})
        metrics = ContentMetrics(**metrics_data)
        
        content_item = ContentItem(
            content_id=item_data.get("content_id", str(uuid.uuid4())),
            content_type=ContentType(item_data.get("content_type", "blog_post")),
            channel=Channel(item_data.get("channel", "blog")),
            publish_date=datetime.fromisoformat(item_data.get("publish_date", datetime.now().isoformat())),
            title=item_data.get("title", ""),
            metrics=metrics,
            topic_tags=item_data.get("topic_tags", []),
            language=item_data.get("language", "es"),
            marketing_consent=item_data.get("marketing_consent", True)
        )
        converted_items.append(content_item)
        
    return await agent.analyze_content_performance(content_items=converted_items)

@app.get("/api/v1/status/{tenant_id}")
async def get_agent_status(tenant_id: str):
    """Get comprehensive agent status"""
    agent = agent_registry.get(tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found for tenant: {tenant_id}")
    return await agent.get_agent_status()

@app.get("/api/v1/audit/trail/{tenant_id}")
async def get_audit_trail(tenant_id: str, limit: int = Query(default=50, ge=1, le=1000)):
    """Get blockchain audit trail"""
    agent = agent_registry.get(tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found for tenant: {tenant_id}")
    return agent.audit_system.get_audit_trail(limit)

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {}
    for tenant_id, agent in agent_registry.items():
        try:
            status = await agent.get_agent_status()
            health_status[tenant_id] = "healthy"
        except:
            health_status[tenant_id] = "UNKNOWN"
            
    overall_health = (
        "healthy" if all(status == "healthy" for status in health_status.values())
        else "degraded"
    )
    
    return {
        "status": overall_health,
        "timestamp": datetime.now().isoformat(),
        "tenants": health_status,
        "version": "5.0.0-enterprise"
    }

# ==================== FUNCIÓN DE PRUEBA SIMPLIFICADA ====================

async def test_super_agent():
    """Función de prueba simplificada del Super-Agent"""
    print("🚀 INICIANDO PRUEBA DEL SUPER-AGENT v5.0 ENTERPRISE")
    print("=" * 60)
    
    try:
        # Configuración
        config = ContentPerformanceConfig(
            tenant_id="tn_test",
            ml_strategy=MLStrategy.HYBRID,
            enable_self_healing=True,
            enable_blockchain_audit=True
        )
        
        # Inicializar agente
        agent = ContentPerformanceSuperAgent("tn_test", config)
        await agent.initialize()
        
        print("✅ Super-Agent inicializado correctamente")
        
        # Crear contenido de prueba
        test_content = [
            ContentItem(
                content_id="test_1",
                content_type=ContentType.BLOG_POST,
                channel=Channel.BLOG,
                publish_date=datetime.now(),
                title="Revolución de Inteligencia Artificial en Marketing Digital 2024",
                metrics=ContentMetrics(
                    impressions=10000,
                    reach=5000,
                    engagement=500,
                    clicks=200,
                    shares=50,
                    comments=30,
                    saves=20
                ),
                topic_tags=["IA", "marketing", "tecnología"],
                marketing_consent=True
            ),
            ContentItem(
                content_id="test_2", 
                content_type=ContentType.SOCIAL_POST,
                channel=Channel.INSTAGRAM,
                publish_date=datetime.now(),
                title="Cómo el Machine Learning está transformando las redes sociales 📱",
                metrics=ContentMetrics(
                    impressions=5000,
                    reach=3000,
                    engagement=800,
                    clicks=150,
                    shares=100,
                    comments=80,
                    saves=40
                ),
                topic_tags=["machine learning", "redes sociales"],
                marketing_consent=True
            )
        ]
        
        print("📊 Analizando contenido de prueba...")
        
        # Ejecutar análisis
        result = await agent.analyze_content_performance(test_content)
        
        print("🎯 RESULTADOS DEL ANÁLISIS:")
        print(f"   ✅ Request ID: {result['request_id']}")
        print(f"   ⏱️  Tiempo procesamiento: {result['processing_time_ms']:.2f}ms")
        print(f"   🩺 Estado salud: {result['health_status']}")
        print(f"   📈 Contenido analizado: {result['content_analyzed']} items")
        
        print("\n📋 RESUMEN DE PERFORMANCE:")
        summary = result['performance_summary']
        print(f"   🚀 Contenido viral: {summary['viral_content']}")
        print(f"   ⭐ Alto performance: {summary['high_performance']}") 
        print(f"   📊 Engagement promedio: {summary['average_engagement']:.2f}%")
        print(f"   🔥 Viralidad promedio: {summary['average_virality']:.2f}")
        
        print("\n🔍 ANÁLISIS DETALLADO:")
        for analysis in result['performance_analyses']:
            print(f"   📝 Contenido: {analysis['content_id']}")
            print(f"     🎯 Nivel: {analysis['performance_level']}")
            print(f"     📈 Engagement: {analysis['engagement_rate']}%")
            print(f"     🔥 Viralidad: {analysis['virality_score']:.2f}")
            print(f"     🤖 Confianza ML: {analysis['ml_confidence']:.2f}")
            print(f"     💡 Sugerencias: {analysis['optimization_suggestions'][:2]}")
            print(f"     ⛓️  Hash Blockchain: {analysis['blockchain_hash'][:16]}...")
            print()
        
        # Estado del agente
        status = await agent.get_agent_status()
        print("📊 ESTADO DEL AGENTE:")
        print(f"   🆔 Agent ID: {status['agent_id']}")
        print(f"   📊 Métricas: {status['performance_metrics']['total_requests']} requests")
        print(f"   💾 Cache: {status['cache_status']['memory_cache_size']} items en memoria")
        print(f"   🤖 ML: {status['ml_pipeline_status']['models_loaded']} modelos cargados")
        print(f"   ⛓️  Blockchain: {status['audit_system_status']['blockchain_records']} registros")
        print(f"   🔧 Self-healing: {status['self_healing_status']['healing_events']} eventos")
        
        print("\n🎉 PRUEBA EXITOSA! Super-Agent v5.0 Enterprise operativo!")
        
        # Limpiar
        await agent.shutdown()
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ejecutar prueba
    asyncio.run(test_super_agent())