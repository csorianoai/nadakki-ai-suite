"""
NADAKKI AI SUITE - MULTI-INDUSTRY CONFIGURATION LAYER
======================================================

Este módulo permite configurar industrias de forma pluggable sin modificar
el core del Campaign Strategy Orchestrator.

ARQUITECTURA:
┌────────────────────────────────────────────────────────────────────┐
│                    INDUSTRY CONFIGURATIONS                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │  FINANCIAL   │ │ BOAT RENTAL  │ │   RETAIL     │               │
│  │  - Banks     │ │ - Nadaki     │ │   - E-comm   │               │
│  │  - Insurance │ │ - Charters   │ │   - Stores   │               │
│  │  - Fintech   │ │ - Tours      │ │   - B2B      │               │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘               │
│         │                │                │                        │
│         ▼                ▼                ▼                        │
│  ┌──────────────────────────────────────────────────────┐         │
│  │              CONFIGURATION REGISTRY                   │         │
│  │  - Industry Parser (pluggable)                       │         │
│  │  - Agent Registry (pluggable)                        │         │
│  │  - Context Enricher (pluggable)                      │         │
│  │  - KPI Definitions (industry-specific)               │         │
│  └──────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────┘

VERSION: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


# ============================================================================
# INDUSTRY TYPES
# ============================================================================

class IndustryType(str, Enum):
    """Supported industry types"""
    FINANCIAL_SERVICES = "financial_services"
    BOAT_RENTAL = "boat_rental"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    PROFESSIONAL_SERVICES = "professional_services"
    SAAS = "saas"
    CUSTOM = "custom"


# ============================================================================
# ABSTRACT INTERFACES
# ============================================================================

class IndustryParser(ABC):
    """Abstract base for industry-specific parsers"""
    
    @property
    @abstractmethod
    def industry_type(self) -> IndustryType:
        pass
    
    @abstractmethod
    async def parse(self, document_content: str, tenant_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def extract_industry_kpis(self, document: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def detect_audiences(self, document: str) -> List[Dict[str, Any]]:
        pass


class ContextEnricher(ABC):
    """Abstract base for context enrichment (seasonality, geography, etc.)"""
    
    @abstractmethod
    def enrich(self, strategy: Dict[str, Any], execution_date: datetime) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_seasonal_adjustments(self, date: datetime) -> Dict[str, float]:
        pass


class AgentRegistryProvider(ABC):
    """Abstract base for industry-specific agent registries"""
    
    @abstractmethod
    def get_registry(self) -> Dict[str, Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_specialized_agents(self) -> List[str]:
        pass


# ============================================================================
# FINANCIAL SERVICES IMPLEMENTATION
# ============================================================================

class FinancialServicesParser(IndustryParser):
    """Parser specialized for financial institutions"""
    
    @property
    def industry_type(self) -> IndustryType:
        return IndustryType.FINANCIAL_SERVICES
    
    async def parse(self, document_content: str, tenant_id: str) -> Dict[str, Any]:
        text_lower = document_content.lower()
        
        return {
            "industry": self.industry_type.value,
            "tenant_id": tenant_id,
            "financial_products": self._detect_products(text_lower),
            "compliance_requirements": self._detect_compliance(text_lower),
            "target_segments": self.detect_audiences(document_content),
            "kpis": self.extract_industry_kpis(document_content),
            "risk_profile": self._detect_risk_profile(text_lower)
        }
    
    def extract_industry_kpis(self, document: str) -> List[Dict[str, Any]]:
        kpis = []
        text_lower = document.lower()
        
        financial_kpis = [
            ("aum", "Assets Under Management", "growth"),
            ("nps", "Net Promoter Score", "satisfaction"),
            ("cac", "Customer Acquisition Cost", "efficiency"),
            ("ltv", "Lifetime Value", "revenue"),
            ("churn", "Churn Rate", "retention"),
            ("nii", "Net Interest Income", "revenue"),
            ("roa", "Return on Assets", "profitability"),
            ("tier 1", "Tier 1 Capital Ratio", "compliance"),
        ]
        
        for keyword, name, category in financial_kpis:
            if keyword in text_lower:
                kpis.append({
                    "name": name,
                    "keyword": keyword,
                    "category": category,
                    "industry_specific": True
                })
        
        return kpis
    
    def detect_audiences(self, document: str) -> List[Dict[str, Any]]:
        audiences = []
        text_lower = document.lower()
        
        segments = [
            (["hnwi", "high net worth", "affluent"], "High Net Worth Individuals", "premium"),
            (["sme", "small business", "pyme"], "Small & Medium Enterprises", "business"),
            (["retail banking", "consumer"], "Retail Banking Customers", "mass"),
            (["corporate", "enterprise", "institutional"], "Corporate & Institutional", "enterprise"),
            (["millennials", "gen z", "young professional"], "Young Professionals", "growth"),
            (["retirement", "pension", "senior"], "Retirement Planning", "wealth"),
        ]
        
        for keywords, name, tier in segments:
            if any(kw in text_lower for kw in keywords):
                audiences.append({
                    "name": name,
                    "tier": tier,
                    "keywords_matched": [kw for kw in keywords if kw in text_lower]
                })
        
        return audiences or [{"name": "General Banking Customers", "tier": "mass"}]
    
    def _detect_products(self, text: str) -> List[str]:
        products = []
        product_keywords = {
            "savings account": "Savings Accounts",
            "checking": "Checking Accounts",
            "credit card": "Credit Cards",
            "mortgage": "Mortgages",
            "personal loan": "Personal Loans",
            "business loan": "Business Loans",
            "investment": "Investment Products",
            "insurance": "Insurance Products",
            "wealth management": "Wealth Management",
        }
        
        for keyword, product in product_keywords.items():
            if keyword in text:
                products.append(product)
        
        return products
    
    def _detect_compliance(self, text: str) -> List[str]:
        compliance = []
        regulations = ["gdpr", "ccpa", "pci dss", "sox", "basel", "dodd-frank", 
                      "mifid", "kyc", "aml", "psd2", "open banking"]
        
        for reg in regulations:
            if reg in text:
                compliance.append(reg.upper())
        
        return compliance
    
    def _detect_risk_profile(self, text: str) -> str:
        if any(kw in text for kw in ["aggressive", "high risk", "growth"]):
            return "aggressive"
        elif any(kw in text for kw in ["conservative", "low risk", "stable"]):
            return "conservative"
        return "moderate"


class FinancialServicesContextEnricher(ContextEnricher):
    """Context enricher for financial services"""
    
    def __init__(self):
        self.financial_calendar = {
            1: {"event": "New Year Financial Planning", "budget_multiplier": 1.2},
            2: {"event": "Tax Season Prep", "budget_multiplier": 1.1},
            3: {"event": "Tax Season Peak", "budget_multiplier": 1.3},
            4: {"event": "Tax Season End / Spring Campaigns", "budget_multiplier": 1.2},
            5: {"event": "Summer Planning", "budget_multiplier": 1.0},
            6: {"event": "Mid-Year Review", "budget_multiplier": 1.1},
            7: {"event": "Summer Slow Period", "budget_multiplier": 0.9},
            8: {"event": "Back to School / Fall Planning", "budget_multiplier": 1.0},
            9: {"event": "Q3 Close / Fall Push", "budget_multiplier": 1.1},
            10: {"event": "Q4 Planning", "budget_multiplier": 1.2},
            11: {"event": "Black Friday / Holiday Shopping", "budget_multiplier": 1.3},
            12: {"event": "Year-End / Holiday Slowdown", "budget_multiplier": 0.8}
        }
    
    def enrich(self, strategy: Dict[str, Any], execution_date: datetime) -> Dict[str, Any]:
        month = execution_date.month
        calendar_info = self.financial_calendar.get(month, {})
        
        strategy["context"] = {
            "execution_month": month,
            "financial_event": calendar_info.get("event", "Standard Period"),
            "recommended_budget_multiplier": calendar_info.get("budget_multiplier", 1.0),
            "is_tax_season": month in [2, 3, 4],
            "is_year_end": month in [11, 12],
            "is_new_year_planning": month == 1,
            "recommendations": self._get_recommendations(month)
        }
        
        return strategy
    
    def get_seasonal_adjustments(self, date: datetime) -> Dict[str, float]:
        month = date.month
        base_multiplier = self.financial_calendar.get(month, {}).get("budget_multiplier", 1.0)
        
        return {
            "overall_budget": base_multiplier,
            "acquisition_campaigns": base_multiplier * (1.2 if month in [1, 9, 10] else 1.0),
            "retention_campaigns": base_multiplier * (1.3 if month in [12] else 1.0),
            "cross_sell": base_multiplier * (1.1 if month in [6] else 1.0)
        }
    
    def _get_recommendations(self, month: int) -> List[str]:
        recommendations = []
        
        if month in [2, 3, 4]:
            recommendations.extend([
                "Increase tax-related product promotions",
                "Highlight tax-advantaged accounts (IRA, HSA)",
                "Run tax preparation partner campaigns"
            ])
        
        if month in [1]:
            recommendations.extend([
                "Focus on financial wellness campaigns",
                "Promote savings goals and budgeting tools",
                "New year resolution-themed messaging"
            ])
        
        if month in [11, 12]:
            recommendations.extend([
                "Holiday spending protection messaging",
                "Year-end charitable giving campaigns",
                "Tax-loss harvesting reminders for investors"
            ])
        
        return recommendations or ["Standard campaign execution recommended"]


class FinancialServicesAgentRegistry(AgentRegistryProvider):
    """Agent registry for financial services"""
    
    def get_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "AUDIENCE_ANALYSIS": {
                "agent_id": "audiencesegmenteria",
                "core": "marketing",
                "fallback": "customersegmentatonia"
            },
            "COMPLIANCE_CHECK": {
                "agent_id": "financialcomplianceia",
                "core": "financial",
                "specialized": True,
                "description": "Checks marketing content for regulatory compliance"
            },
            "RISK_ASSESSMENT": {
                "agent_id": "riskassessmentia",
                "core": "financial",
                "specialized": True,
                "description": "Assesses customer risk profile for product matching"
            },
            "CREDIT_SCORING": {
                "agent_id": "creditscoringia",
                "core": "financial",
                "specialized": True,
                "description": "Lead scoring based on creditworthiness signals"
            },
            "WEALTH_SEGMENTATION": {
                "agent_id": "wealthsegmentatoria",
                "core": "financial",
                "specialized": True,
                "description": "Segments customers by wealth tier and investment profile"
            },
            "FRAUD_PREVENTION_MESSAGING": {
                "agent_id": "fraudpreventmessagia",
                "core": "financial",
                "specialized": True,
                "description": "Creates security awareness and fraud prevention content"
            },
            "CROSS_SELL_OPTIMIZATION": {
                "agent_id": "financialcrosssellia",
                "core": "financial",
                "specialized": True,
                "description": "Optimizes cross-selling of financial products"
            }
        }
    
    def get_specialized_agents(self) -> List[str]:
        return [
            "financialcomplianceia",
            "riskassessmentia",
            "creditscoringia",
            "regulatorycontentia",
            "wealthsegmentatoria",
            "fraudpreventmessagia",
            "financialcrosssellia"
        ]


# ============================================================================
# BOAT RENTAL IMPLEMENTATION (for Nadaki)
# ============================================================================

class BoatRentalParser(IndustryParser):
    """Parser specialized for boat rental businesses"""
    
    @property
    def industry_type(self) -> IndustryType:
        return IndustryType.BOAT_RENTAL
    
    async def parse(self, document_content: str, tenant_id: str) -> Dict[str, Any]:
        text_lower = document_content.lower()
        
        return {
            "industry": self.industry_type.value,
            "tenant_id": tenant_id,
            "boat_niches": self._detect_boat_niches(text_lower),
            "experience_types": self._detect_experience_types(text_lower),
            "target_segments": self.detect_audiences(document_content),
            "kpis": self.extract_industry_kpis(document_content),
            "marketplaces": self._detect_marketplaces(text_lower),
            "location_context": self._detect_location(text_lower)
        }
    
    def extract_industry_kpis(self, document: str) -> List[Dict[str, Any]]:
        kpis = []
        text_lower = document.lower()
        
        boat_kpis = [
            ("booking rate", "Booking Conversion Rate", "conversion"),
            ("average charter", "Average Charter Value", "revenue"),
            ("repeat customer", "Repeat Customer Rate", "retention"),
            ("review velocity", "Review Velocity", "reputation"),
            ("response time", "Inquiry Response Time", "operations"),
            ("utilization", "Fleet Utilization Rate", "operations"),
            ("getmyboat rank", "Marketplace Ranking", "visibility"),
            ("whatsapp close", "WhatsApp Close Rate", "sales"),
        ]
        
        for keyword, name, category in boat_kpis:
            if keyword in text_lower:
                kpis.append({
                    "name": name,
                    "keyword": keyword,
                    "category": category,
                    "industry_specific": True
                })
        
        return kpis
    
    def detect_audiences(self, document: str) -> List[Dict[str, Any]]:
        audiences = []
        text_lower = document.lower()
        
        segments = [
            (["birthday", "celebration", "party"], "Birthday Boat Party Planners", "high"),
            (["bachelorette", "bachelor", "bride"], "Bachelorette/Bachelor Groups", "premium"),
            (["corporate", "team building", "company event"], "Corporate Events", "enterprise"),
            (["wedding", "proposal", "anniversary"], "Wedding/Romance Seekers", "premium"),
            (["sunset", "cruise", "romantic"], "Sunset Cruise Seekers", "standard"),
            (["family", "kids", "children", "sandbar"], "Family Adventures", "standard"),
            (["fishing", "angler", "deep sea"], "Fishing Charters", "standard"),
            (["tourist", "vacation", "visitor"], "Tourists & Visitors", "standard"),
            (["yacht", "luxury", "vip"], "Luxury/VIP Experiences", "ultra-premium"),
        ]
        
        for keywords, name, tier in segments:
            if any(kw in text_lower for kw in keywords):
                audiences.append({
                    "name": name,
                    "tier": tier,
                    "keywords_matched": [kw for kw in keywords if kw in text_lower],
                    "priority": "high" if tier in ["premium", "enterprise", "ultra-premium"] else "medium"
                })
        
        return audiences or [{"name": "General Charter Customers", "tier": "standard"}]
    
    def _detect_boat_niches(self, text: str) -> List[Dict[str, Any]]:
        niches = []
        niche_patterns = [
            ("birthday boat", "Birthday Parties", 1),
            ("bachelorette", "Bachelorette Parties", 2),
            ("sunset cruise", "Sunset Cruises", 3),
            ("sandbar", "Sandbar Trips", 4),
            ("fishing charter", "Fishing Charters", 5),
            ("yacht charter", "Yacht Charters", 6),
        ]
        
        for keyword, name, priority in niche_patterns:
            if keyword in text:
                niches.append({"name": name, "priority": priority})
        
        return sorted(niches, key=lambda x: x["priority"])
    
    def _detect_experience_types(self, text: str) -> List[str]:
        experiences = []
        exp_keywords = {
            "captain included": "Captained Charter",
            "bareboat": "Bareboat Rental",
            "all inclusive": "All-Inclusive Package",
            "catering": "Catering Available",
            "decorations": "Decorations Package",
        }
        
        for keyword, exp in exp_keywords.items():
            if keyword in text:
                experiences.append(exp)
        
        return experiences
    
    def _detect_marketplaces(self, text: str) -> List[str]:
        marketplaces = []
        platforms = ["getmyboat", "boatsetter", "click&boat", "sailo", "viator"]
        
        for platform in platforms:
            if platform in text:
                marketplaces.append(platform.title())
        
        return marketplaces
    
    def _detect_location(self, text: str) -> Dict[str, Any]:
        location = {"detected": False}
        
        if "miami" in text:
            location = {
                "detected": True,
                "city": "Miami",
                "state": "Florida",
                "country": "USA",
                "water_body": "Biscayne Bay" if "biscayne" in text else "Atlantic Ocean",
            }
        
        return location


class BoatRentalContextEnricher(ContextEnricher):
    """Context enricher for Miami boat rental (handles seasonality)"""
    
    def __init__(self):
        self.miami_calendar = {
            1: {"season": "high", "events": ["Winter Visitors"], "budget_multiplier": 1.3},
            2: {"season": "peak", "events": ["Super Bowl Week", "Presidents Day"], "budget_multiplier": 1.5},
            3: {"season": "peak", "events": ["Spring Break Peak", "Ultra Music Festival"], "budget_multiplier": 1.6},
            4: {"season": "high", "events": ["Easter", "Spring Break Late"], "budget_multiplier": 1.4},
            5: {"season": "shoulder", "events": ["Memorial Day"], "budget_multiplier": 1.2},
            6: {"season": "high", "events": ["Summer Start"], "budget_multiplier": 1.4},
            7: {"season": "high", "events": ["July 4th", "Summer Peak"], "budget_multiplier": 1.4},
            8: {"season": "shoulder", "events": ["Hurricane Season"], "budget_multiplier": 1.0},
            9: {"season": "low", "events": ["Hurricane Peak"], "budget_multiplier": 0.7},
            10: {"season": "low", "events": ["Hurricane Late Season"], "budget_multiplier": 0.8},
            11: {"season": "shoulder", "events": ["Thanksgiving", "Art Basel Prep"], "budget_multiplier": 1.1},
            12: {"season": "peak", "events": ["Art Basel Miami", "Holidays", "NYE"], "budget_multiplier": 1.7}
        }
    
    def enrich(self, strategy: Dict[str, Any], execution_date: datetime) -> Dict[str, Any]:
        month = execution_date.month
        calendar_info = self.miami_calendar.get(month, {})
        
        strategy["context"] = {
            "execution_month": month,
            "season": calendar_info.get("season", "standard"),
            "events": calendar_info.get("events", []),
            "recommended_budget_multiplier": calendar_info.get("budget_multiplier", 1.0),
            "is_hurricane_season": month in [8, 9, 10],
            "is_peak_tourist": month in [2, 3, 12],
            "is_spring_break": month in [3],
            "weather_advisory": self._get_weather_advisory(month),
            "recommendations": self._get_recommendations(month)
        }
        
        return strategy
    
    def get_seasonal_adjustments(self, date: datetime) -> Dict[str, float]:
        month = date.month
        base = self.miami_calendar.get(month, {}).get("budget_multiplier", 1.0)
        
        return {
            "overall_budget": base,
            "bachelorette_campaigns": base * (1.4 if month in [3, 4, 5, 6] else 1.0),
            "birthday_campaigns": base,
            "corporate_campaigns": base * (1.2 if month in [1, 2, 10, 11] else 0.8),
            "sunset_cruise_campaigns": base * (1.3 if month in [11, 12, 1, 2] else 1.0),
            "family_campaigns": base * (1.4 if month in [6, 7, 8] else 1.0),
            "marketplace_ads": base * (1.5 if month in [2, 3, 12] else 1.0)
        }
    
    def _get_weather_advisory(self, month: int) -> Optional[str]:
        if month in [9, 10]:
            return "⚠️ Hurricane season - have cancellation policies ready"
        if month in [6, 7, 8]:
            return "☀️ Hot season - emphasize early morning/sunset charters"
        return None
    
    def _get_recommendations(self, month: int) -> List[str]:
        recs = []
        
        if month == 2:
            recs.extend([
                "🏈 Create Super Bowl watch party packages",
                "📈 Increase GetMyBoat bids 50%+"
            ])
        
        if month == 3:
            recs.extend([
                "🎉 Spring Break party packages",
                "💵 Premium pricing - high demand period"
            ])
        
        if month == 12:
            recs.extend([
                "🎨 Art Basel special packages",
                "🌅 Sunset cruise emphasis (weather is perfect)"
            ])
        
        if month in [9, 10]:
            recs.extend([
                "💰 Off-season discounts",
                "🛡️ Flexible cancellation policies"
            ])
        
        return recs or ["Standard campaign execution"]


class BoatRentalAgentRegistry(AgentRegistryProvider):
    """Agent registry for boat rental businesses"""
    
    def get_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "AUDIENCE_ANALYSIS": {
                "agent_id": "audiencesegmenteria",
                "core": "marketing",
                "fallback": "customersegmentatonia"
            },
            "MARKETPLACE_OPTIMIZATION": {
                "agent_id": "marketplacerankeria",
                "core": "boat_rental",
                "specialized": True,
                "description": "Optimizes GetMyBoat/Boatsetter profiles and rankings"
            },
            "WHATSAPP_SALES": {
                "agent_id": "whatsappcloseria",
                "core": "boat_rental",
                "specialized": True,
                "description": "Manages WhatsApp sales conversations"
            },
            "BIRTHDAY_CONTENT": {
                "agent_id": "birthdayboatcontentia",
                "core": "boat_rental",
                "specialized": True,
                "description": "Creates birthday-specific boat party content"
            },
            "BACHELORETTE_CONTENT": {
                "agent_id": "bacheloretteboatcontentia",
                "core": "boat_rental",
                "specialized": True,
                "description": "Creates bachelorette party specific content"
            },
            "REVIEW_MANAGEMENT": {
                "agent_id": "reviewvelocitia",
                "core": "boat_rental",
                "specialized": True,
                "description": "Manages review solicitation and response"
            },
            "SEASONAL_PRICING": {
                "agent_id": "seasonalpriceria",
                "core": "boat_rental",
                "specialized": True,
                "description": "Optimizes pricing based on Miami seasonality"
            },
            "WEATHER_RESPONSIVE": {
                "agent_id": "weatherresponseia",
                "core": "boat_rental",
                "specialized": True,
                "description": "Adjusts messaging based on weather forecasts"
            }
        }
    
    def get_specialized_agents(self) -> List[str]:
        return [
            "marketplacerankeria",
            "whatsappcloseria",
            "birthdayboatcontentia",
            "bacheloretteboatcontentia",
            "reviewvelocitia",
            "seasonalpriceria",
            "charterupsellia",
            "weatherresponseia"
        ]


# ============================================================================
# RETAIL IMPLEMENTATION
# ============================================================================

class RetailParser(IndustryParser):
    """Parser specialized for retail businesses"""
    
    @property
    def industry_type(self) -> IndustryType:
        return IndustryType.RETAIL
    
    async def parse(self, document_content: str, tenant_id: str) -> Dict[str, Any]:
        text_lower = document_content.lower()
        
        return {
            "industry": self.industry_type.value,
            "tenant_id": tenant_id,
            "target_segments": self.detect_audiences(document_content),
            "kpis": self.extract_industry_kpis(document_content),
            "channels": self._detect_channels(text_lower)
        }
    
    def extract_industry_kpis(self, document: str) -> List[Dict[str, Any]]:
        kpis = []
        text_lower = document.lower()
        
        retail_kpis = [
            ("aov", "Average Order Value", "revenue"),
            ("cart abandon", "Cart Abandonment Rate", "conversion"),
            ("repeat rate", "Repeat Purchase Rate", "retention"),
            ("roas", "Return on Ad Spend", "efficiency"),
            ("ltv", "Customer Lifetime Value", "revenue"),
        ]
        
        for keyword, name, category in retail_kpis:
            if keyword in text_lower:
                kpis.append({
                    "name": name,
                    "keyword": keyword,
                    "category": category,
                    "industry_specific": True
                })
        
        return kpis
    
    def detect_audiences(self, document: str) -> List[Dict[str, Any]]:
        audiences = []
        text_lower = document.lower()
        
        segments = [
            (["bargain", "discount", "deal"], "Bargain Hunters", "value"),
            (["loyal", "repeat", "member"], "Loyal Customers", "premium"),
            (["new customer", "first time"], "New Customers", "acquisition"),
        ]
        
        for keywords, name, tier in segments:
            if any(kw in text_lower for kw in keywords):
                audiences.append({"name": name, "tier": tier})
        
        return audiences or [{"name": "General Shoppers", "tier": "standard"}]
    
    def _detect_channels(self, text: str) -> List[str]:
        channels = []
        keywords = ["ecommerce", "online", "store", "amazon", "shopify"]
        
        for kw in keywords:
            if kw in text:
                channels.append(kw.title())
        
        return channels


class RetailContextEnricher(ContextEnricher):
    """Context enricher for retail"""
    
    def __init__(self):
        self.retail_calendar = {
            1: {"event": "Post-Holiday Sales", "multiplier": 1.1},
            2: {"event": "Valentine's Day", "multiplier": 1.2},
            5: {"event": "Mother's Day", "multiplier": 1.3},
            6: {"event": "Father's Day", "multiplier": 1.2},
            7: {"event": "Prime Day / Summer Sales", "multiplier": 1.4},
            11: {"event": "Black Friday / Cyber Monday", "multiplier": 2.0},
            12: {"event": "Holiday Season", "multiplier": 1.8}
        }
    
    def enrich(self, strategy: Dict[str, Any], execution_date: datetime) -> Dict[str, Any]:
        month = execution_date.month
        calendar_info = self.retail_calendar.get(month, {"event": "Standard", "multiplier": 1.0})
        
        strategy["context"] = {
            "execution_month": month,
            "retail_event": calendar_info["event"],
            "budget_multiplier": calendar_info["multiplier"]
        }
        
        return strategy
    
    def get_seasonal_adjustments(self, date: datetime) -> Dict[str, float]:
        month = date.month
        base = self.retail_calendar.get(month, {}).get("multiplier", 1.0)
        
        return {
            "overall_budget": base,
            "acquisition": base * 1.2,
            "retention": base * 0.8
        }


class RetailAgentRegistry(AgentRegistryProvider):
    """Agent registry for retail"""
    
    def get_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "INVENTORY_OPTIMIZATION": {
                "agent_id": "inventoryoptimizeria",
                "core": "retail",
                "specialized": True
            },
            "CART_RECOVERY": {
                "agent_id": "cartrecoveryia",
                "core": "retail",
                "specialized": True
            },
            "PRODUCT_RECOMMENDATIONS": {
                "agent_id": "productrecommenderia",
                "core": "retail",
                "specialized": True
            }
        }
    
    def get_specialized_agents(self) -> List[str]:
        return [
            "inventoryoptimizeria",
            "cartrecoveryia",
            "productrecommenderia",
            "pricedynamicia",
            "loyaltyprogramia"
        ]


# ============================================================================
# CONFIGURATION REGISTRY (Central Hub)
# ============================================================================

@dataclass
class IndustryConfiguration:
    """Complete configuration for an industry"""
    industry_type: IndustryType
    parser: IndustryParser
    context_enricher: ContextEnricher
    agent_registry: AgentRegistryProvider
    custom_kpis: List[Dict[str, Any]] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigurationRegistry:
    """
    Central registry for industry configurations.
    This is the KEY to making the system reusable across industries.
    """
    
    _instance = None
    _configurations: Dict[IndustryType, IndustryConfiguration] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_defaults()
        return cls._instance
    
    def _initialize_defaults(self):
        """Initialize default industry configurations"""
        # Financial Services
        self.register(IndustryConfiguration(
            industry_type=IndustryType.FINANCIAL_SERVICES,
            parser=FinancialServicesParser(),
            context_enricher=FinancialServicesContextEnricher(),
            agent_registry=FinancialServicesAgentRegistry(),
            compliance_requirements=["GDPR", "CCPA", "PCI-DSS", "KYC", "AML"],
            metadata={"region": "global", "regulated": True}
        ))
        
        # Boat Rental
        self.register(IndustryConfiguration(
            industry_type=IndustryType.BOAT_RENTAL,
            parser=BoatRentalParser(),
            context_enricher=BoatRentalContextEnricher(),
            agent_registry=BoatRentalAgentRegistry(),
            compliance_requirements=["USCG", "Local Maritime"],
            metadata={"region": "miami", "seasonal": True}
        ))
        
        # Retail
        self.register(IndustryConfiguration(
            industry_type=IndustryType.RETAIL,
            parser=RetailParser(),
            context_enricher=RetailContextEnricher(),
            agent_registry=RetailAgentRegistry(),
            compliance_requirements=["PCI-DSS", "CCPA"],
            metadata={"region": "global"}
        ))
    
    def register(self, config: IndustryConfiguration) -> None:
        """Register an industry configuration"""
        self._configurations[config.industry_type] = config
    
    def get(self, industry_type: IndustryType) -> Optional[IndustryConfiguration]:
        """Get configuration for an industry"""
        return self._configurations.get(industry_type)
    
    def list_industries(self) -> List[IndustryType]:
        """List all registered industries"""
        return list(self._configurations.keys())


# ============================================================================
# TENANT CONFIGURATION
# ============================================================================

@dataclass
class TenantConfiguration:
    """Configuration specific to a tenant"""
    tenant_id: str
    tenant_name: str
    industry_type: IndustryType
    
    # Tenant-specific settings
    timezone: str = "UTC"
    currency: str = "USD"
    language: str = "en"
    
    # Feature flags
    enable_smart_allocation: bool = True
    enable_proactive_alerts: bool = True
    enable_context_enrichment: bool = True
    
    # Compliance
    compliance_mode: str = "standard"
    data_retention_days: int = 365


class TenantRegistry:
    """Registry for tenant configurations"""
    
    def __init__(self, storage_dir: str = "./tenant_configs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._tenants: Dict[str, TenantConfiguration] = {}
    
    def register(self, config: TenantConfiguration) -> None:
        """Register a tenant"""
        self._tenants[config.tenant_id] = config
    
    def get(self, tenant_id: str) -> Optional[TenantConfiguration]:
        """Get tenant configuration"""
        return self._tenants.get(tenant_id)
    
    def list_tenants(self) -> List[str]:
        """List all registered tenant IDs"""
        return list(self._tenants.keys())


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_industry_config(industry_type: str) -> Optional[IndustryConfiguration]:
    """
    Get industry configuration by type string.
    
    Example:
        config = get_industry_config("financial_services")
        parser = config.parser
        enricher = config.context_enricher
    """
    try:
        industry = IndustryType(industry_type)
    except ValueError:
        return None
    
    registry = ConfigurationRegistry()
    return registry.get(industry)


# ============================================================================
# TEST
# ============================================================================

def test_multi_industry():
    """Test multi-industry configuration"""
    print("=" * 70)
    print("🌐 MULTI-INDUSTRY CONFIGURATION TEST")
    print("=" * 70)
    
    registry = ConfigurationRegistry()
    
    print(f"\n📊 Available Industries: {[i.value for i in registry.list_industries()]}")
    
    # Test Financial Services
    print("\n🏦 Financial Services:")
    fin_config = registry.get(IndustryType.FINANCIAL_SERVICES)
    if fin_config:
        print(f"   Specialized Agents: {fin_config.agent_registry.get_specialized_agents()}")
        print(f"   Compliance: {fin_config.compliance_requirements}")
        adjustments = fin_config.context_enricher.get_seasonal_adjustments(datetime(2025, 3, 15))
        print(f"   March (Tax Season) Multiplier: {adjustments['overall_budget']:.1f}x")
    
    # Test Boat Rental
    print("\n🚤 Boat Rental:")
    boat_config = registry.get(IndustryType.BOAT_RENTAL)
    if boat_config:
        print(f"   Specialized Agents: {boat_config.agent_registry.get_specialized_agents()}")
        print(f"   Compliance: {boat_config.compliance_requirements}")
        adjustments = boat_config.context_enricher.get_seasonal_adjustments(datetime(2025, 12, 5))
        print(f"   December (Art Basel) Multiplier: {adjustments['overall_budget']:.1f}x")
    
    print("\n" + "=" * 70)
    print("✅ MULTI-INDUSTRY TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_multi_industry()
