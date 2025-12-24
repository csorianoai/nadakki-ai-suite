# schemas/canonical.py - Nadakki Marketing Canonical Schemas v1.1.0
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime

class UTMParams(BaseModel):
    source: str
    medium: Optional[str] = None
    campaign: Optional[str] = None
    term: Optional[str] = None
    content: Optional[str] = None

class ContactInfo(BaseModel):
    email: str
    phone: Optional[str] = None
    whatsapp: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class Event(BaseModel):
    ts: datetime
    type: Literal['pageview', 'form_submit', 'click', 'call', 'email_open']
    path: Optional[str] = None
    form: Optional[str] = None
    fields: Optional[Dict] = None
    utm: Optional[UTMParams] = None

class LeadAttributes(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=100)
    income: Optional[float] = Field(None, ge=0)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    industry: Optional[str] = None
    channel: str
    utm: Optional[UTMParams] = None

class Lead(BaseModel):
    tenant_id: str = Field(..., min_length=3, description="Multi-tenant ID")
    lead_id: str = Field(..., pattern=r'^L-\d{8}-\d{4}$')
    persona: Dict[str, str]
    attributes: LeadAttributes
    contact: ContactInfo
    events: List[Event] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "tn_credicefi",
                "lead_id": "L-20251003-0001",
                "persona": {"segment": "SMB", "country": "DO", "region": "latam"},
                "attributes": {
                    "age": 34, "income": 48000, "credit_score": 720,
                    "industry": "Retail", "channel": "landing_form",
                    "utm": {"source": "ads", "campaign": "q4_search"}
                },
                "contact": {"email": "test@example.com", "phone": "+1-809-555-0100"},
                "events": []
            }
        }
    }

class CampaignPerformance(BaseModel):
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    spend: float = 0.0

class Cohort(BaseModel):
    key: str
    size: int
    ltv: float = 0.0
    cac: float = 0.0
    conv_rate: Optional[float] = None
    roas: Optional[float] = None

class Campaign(BaseModel):
    tenant_id: str
    campaign_id: str
    channel: str
    budget: float
    kpi: Dict[str, float]
    cohorts: List[Cohort] = []
    performance: CampaignPerformance

class LeadScoringOutput(BaseModel):
    lead_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    bucket: Literal['A', 'B', 'C', 'D']
    reasons: List[str]
    recommended_action: Literal['assign_to_sales', 'nurture', 'reject']
    latency_ms: int
    tenant_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ContactQualityIA schemas
class ContactHistory(BaseModel):
    channel: Literal['phone', 'email', 'whatsapp']
    timestamp: datetime
    outcome: Literal['answered', 'no_answer', 'busy', 'opened', 'clicked', 'bounced']

class ContactQualityInput(BaseModel):
    lead: Lead
    contact_history: List[ContactHistory] = []

class ContactQualityOutput(BaseModel):
    lead_id: str
    contactability_score: float = Field(..., ge=0.0, le=1.0)
    best_channel: Literal['phone', 'email', 'whatsapp']
    best_time_window: str
    script_variant: Literal['A', 'B', 'C']
    next_action: Literal['call_now', 'schedule', 'send_email']
    latency_ms: int
    tenant_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ConversionCohortIA schemas
class ConversionCohortInput(BaseModel):
    tenant_id: str
    campaigns: List[Campaign]
    time_range: Dict[str, str] = {"start": "2025-01-01", "end": "2025-12-31"}

class ConversionCohortOutput(BaseModel):
    tenant_id: str
    cohorts: List[Cohort]
    insights: List[str]
    recommendations: List[str]
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# CampaignOptimizerIA schemas
class BudgetConstraints(BaseModel):
    min_per_campaign: float = 100
    max_daily_spend: float = 10000
    channel_mix: Dict[str, float] = {}

class CampaignAllocation(BaseModel):
    campaign_id: str
    recommended_spend: float
    delta: str

class CampaignOptimizerInput(BaseModel):
    tenant_id: str
    campaigns: List[Campaign]
    total_budget: float
    constraints: BudgetConstraints

class CampaignOptimizerOutput(BaseModel):
    tenant_id: str
    allocation: List[CampaignAllocation]
    expected_uplift: Dict[str, str]
    constraints_met: List[str]
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# TIER 2 SCHEMAS - EmailPersonalizerIA
# ============================================================================

class EmailPersonalizationInput(BaseModel):
    lead_id: str
    name: str = "Cliente"
    segment: Literal['high_value', 'mid_value', 'low_value'] = 'mid_value'
    persona: Literal['young_professional', 'business_owner', 'retired', 'default'] = 'default'
    timezone: str = "UTC"
    campaign_id: Optional[str] = None
    context: Dict[str, Any] = {}
    previous_emails: int = Field(default=0, ge=0)
    last_contact_at: Optional[str] = None
    consent_opt_in: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "lead_id": "L-20251005-0001",
                "name": "María González",
                "segment": "high_value",
                "persona": "young_professional",
                "timezone": "America/Mexico_City",
                "campaign_id": "cmp_demo_001",
                "context": {
                    "product": "crédito personal",
                    "offer_amount": 50000,
                    "approval_probability": 0.85
                },
                "previous_emails": 1,
                "last_contact_at": "2025-10-01T10:00:00Z",
                "consent_opt_in": True
            }
        }
    }

class ComplianceCheck(BaseModel):
    status: Literal['pass', 'fail']
    blocked_reasons: List[str] = []

class EmailPersonalizationOutput(BaseModel):
    tenant_id: str
    lead_id: str
    status: Literal['ready', 'blocked', 'suppressed', 'error']
    campaign_id: Optional[str] = None
    subject_line: Optional[str] = None
    preview_text: Optional[str] = None
    content_blocks: Optional[List[Dict[str, Any]]] = None
    cta_text: Optional[str] = None
    optimal_send_time: Optional[str] = None
    personalization_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ab_variant: Optional[Literal['A', 'B']] = None
    tone: Optional[str] = None
    estimated_open_rate: Optional[float] = None
    estimated_metrics: Optional[Dict[str, float]] = None
    template_id: Optional[str] = None
    compliance: Optional[ComplianceCheck] = None
    decision_trace: Optional[List[str]] = None
    version: Optional[str] = None
    error: Optional[str] = None
    reason: Optional[str] = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# TIER 2 SCHEMAS - ABTestOptimizerIA
# ============================================================================

class ABTestVariant(BaseModel):
    variant_id: str
    name: str = ""
    impressions: int = Field(..., ge=0)
    clicks: int = Field(..., ge=0)
    conversions: int = Field(..., ge=0)
    revenue: float = Field(default=0, ge=0)

    @field_validator('clicks')
    @classmethod
    def clicks_not_exceed_impressions(cls, v: int, info) -> int:
        if 'impressions' in info.data and v > info.data['impressions']:
            raise ValueError('Clicks cannot exceed impressions')
        return v

class ABTestInput(BaseModel):
    test_id: str
    test_name: str = "Unnamed test"
    started_at: str  # ISO 8601 datetime
    variants: List[ABTestVariant] = Field(..., min_length=2, max_length=5)
    metric: Literal['conversion_rate', 'ctr', 'revenue_per_user'] = 'conversion_rate'

    model_config = {
        "json_schema_extra": {
            "example": {
                "test_id": "test_001",
                "test_name": "Subject Line Test",
                "started_at": "2025-10-04T00:00:00Z",
                "variants": [
                    {
                        "variant_id": "A",
                        "name": "Control",
                        "impressions": 5000,
                        "clicks": 250,
                        "conversions": 50,
                        "revenue": 5000
                    },
                    {
                        "variant_id": "B",
                        "name": "Variant",
                        "impressions": 5000,
                        "clicks": 310,
                        "conversions": 68,
                        "revenue": 6800
                    }
                ],
                "metric": "conversion_rate"
            }
        }
    }

class VariantMetrics(BaseModel):
    variant_id: str
    name: str
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    ctr: float
    conversion_rate: float
    revenue_per_user: float

class ABTestOutput(BaseModel):
    tenant_id: str
    test_id: str
    test_name: str
    test_status: Literal['winner_found', 'keep_running', 'inconclusive', 'error']
    winner_variant: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    uplift_pct: float
    statistical_power: float = Field(..., ge=0.0, le=1.0)
    p_value: float = Field(..., ge=0.0, le=1.0)
    recommendation: str
    runtime_hours: float
    variant_analysis: List[VariantMetrics]
    sample_size_adequate: bool
    minimum_detectable_effect: float
    error_message: Optional[str] = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# TIER 2 SCHEMAS - AudienceSegmentationIA
# ============================================================================

class AudienceSegmentationInput(BaseModel):
    audience_id: str
    leads: List[Dict[str, Any]] = Field(..., min_length=1)
    segmentation_strategy: Literal['behavioral', 'demographic', 'hybrid'] = 'hybrid'
    max_segments: int = Field(default=5, ge=2, le=10)

    model_config = {
        "json_schema_extra": {
            "example": {
                "audience_id": "aud_001",
                "leads": [
                    {
                        "lead_id": "L1",
                        "credit_score": 750,
                        "income": 70000,
                        "age": 35,
                        "engagement_score": 0.8,
                        "days_since_last_interaction": 5,
                        "previous_conversions": 1,
                        "product_interests": ["loan", "credit_card"],
                        "location": {"city": "Santo Domingo", "state": "DN"}
                    },
                    {
                        "lead_id": "L2",
                        "credit_score": 650,
                        "income": 45000,
                        "age": 42,
                        "engagement_score": 0.5,
                        "days_since_last_interaction": 45,
                        "previous_conversions": 0,
                        "product_interests": ["savings"],
                        "location": {"city": "Santiago", "state": "ST"}
                    }
                ],
                "segmentation_strategy": "hybrid",
                "max_segments": 5
            }
        }
    }

class Segment(BaseModel):
    segment_id: str
    segment_name: str
    size: int
    characteristics: Dict[str, Any]
    lead_ids: List[str]
    priority: Optional[int] = None
    recommended_actions: List[str] = []

class OverlapAnalysis(BaseModel):
    total_unique_leads: int
    overlapping_leads: int
    overlap_rate: float = Field(..., ge=0.0, le=1.0)

class AudienceSegmentationOutput(BaseModel):
    tenant_id: str
    audience_id: str
    strategy_used: Literal['behavioral', 'demographic', 'hybrid']
    total_leads: int
    segments: List[Segment]
    coverage: float = Field(..., ge=0.0, le=1.0)
    overlap_analysis: OverlapAnalysis
    segmentation_quality_score: float = Field(..., ge=0.0, le=1.0)
    error: Optional[str] = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# TIER 2 SCHEMAS - 4 agentes financieros
# ============================================================================

# MinimalFormIA
class MinimalFormInput(BaseModel):
    form_id: str
    profile: Dict[str, Any]
    current_fields: List[str] = []
    optimization_goal: Literal['minimize_fields', 'maximize_qualification', 'balanced'] = 'balanced'
    ab_test_seed: Optional[str] = None

class MinimalFormOutput(BaseModel):
    tenant_id: str
    form_id: str
    status: str
    recommended_fields: List[str]
    field_config: List[Dict[str, Any]]
    progressive_steps: List[List[str]]
    compliance: Dict[str, Any]
    estimated_metrics: Dict[str, float]
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ProductAffinityIA
class ProductAffinityInput(BaseModel):
    customer_id: str
    customer: Dict[str, Any]
    max_recommendations: int = 3
    ab_test_seed: Optional[str] = None

class ProductAffinityOutput(BaseModel):
    tenant_id: str
    customer_id: str
    recommendations: List[Dict[str, Any]]
    revenue_impact: Dict[str, float]
    compliance: Dict[str, Any]
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# CashOfferFilterIA
class CashOfferInput(BaseModel):
    customer_id: str
    customer: Dict[str, Any]
    requested_amount: Optional[float] = None
    purpose: Optional[str] = None

class CashOfferOutput(BaseModel):
    tenant_id: str
    customer_id: str
    eligible: bool
    tier: Optional[str] = None
    primary_offer: Optional[Dict[str, Any]] = None
    alternative_offers: Optional[List[Dict[str, Any]]] = None
    ineligibility_reason: Optional[str] = None
    compliance: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# GeoSegmentationIA
class GeoSegmentationInput(BaseModel):
    segmentation_id: str
    geo_data: List[Dict[str, Any]]
    total_budget: float
    optimization_level: Literal['country', 'region', 'city', 'zip'] = 'city'

class GeoSegmentationOutput(BaseModel):
    tenant_id: str
    segmentation_id: str
    optimization_level: str
    clusters: List[Dict[str, Any]]
    budget_allocations: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]
    recommendations: List[str]
    compliance: Dict[str, Any]
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)