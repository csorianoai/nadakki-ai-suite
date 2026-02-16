# ===============================================================================
# NADAKKI AI Suite - SearchTermsCleanerIA
# agents/marketing/search_terms_cleaner_agent.py
# Day 4 - Component 3 of 3
# ===============================================================================

"""
Search Terms Cleaner Agent - classifies search terms as positive/negative.

Analyzes search terms data and:
1. Identifies wasted spend on irrelevant terms
2. Recommends negative keywords to add
3. Identifies high-performing terms to add as exact match
4. Generates ActionPlan with cleanup operations

Classification logic:
- Spend > threshold + 0 conversions > NEGATIVE (waste)
- Conversions > 0 + good CPA > POSITIVE (add as exact)
- Low impressions > MONITOR (need more data)
- Contains irrelevant keywords > NEGATIVE (pattern match)

Usage:
    cleaner = SearchTermsCleanerIA(knowledge_store)
    
    plan = cleaner.analyze_and_clean(
        tenant_id="bank01",
        search_terms=[
            {"term": "personal loan rates", "impressions": 500, "clicks": 25, "cost": 50, "conversions": 3},
            {"term": "free money no credit check", "impressions": 200, "clicks": 15, "cost": 30, "conversions": 0},
        ],
        industry="financial_services",
    )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from integrations.google_ads.knowledge.yaml_store import YamlKnowledgeStore
from integrations.google_ads.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger("nadakki.agents.search_terms_cleaner")


class TermClassification:
    POSITIVE = "positive"       # Good term, add as keyword
    NEGATIVE = "negative"       # Bad term, add as negative
    MONITOR = "monitor"         # Need more data
    NEUTRAL = "neutral"         # OK, no action needed


class SearchTermsCleanerIA:
    """
    Classifies search terms and generates cleanup ActionPlans.
    """
    
    AGENT_NAME = "SearchTermsCleanerIA"
    VERSION = "1.0.0"
    
    # Default thresholds
    WASTE_SPEND_THRESHOLD = 10.0    # $10 spend with 0 conversions = waste
    LOW_IMPRESSION_THRESHOLD = 50   # Below 50 impressions = need more data
    GOOD_CPA_MULTIPLIER = 1.5      # CPA below 1.5x benchmark = good
    HIGH_CTR_THRESHOLD = 5.0       # CTR > 5% = strong positive signal
    
    # Irrelevant patterns for financial services
    DEFAULT_IRRELEVANT_PATTERNS = [
        "free", "hack", "cheat", "scam", "reddit", "forum",
        "youtube", "tutorial", "diy", "template", "sample",
        "salary", "job", "career", "internship", "interview",
        "download", "torrent", "crack", "pirate",
    ]
    
    def __init__(self, knowledge_store: YamlKnowledgeStore):
        self.kb = knowledge_store
        logger.info(f"{self.AGENT_NAME} v{self.VERSION} initialized")
    
    # ---------------------------------------------------------------------
    # Main Entry Point
    # ---------------------------------------------------------------------
    
    def analyze_and_clean(
        self,
        tenant_id: str,
        search_terms: List[dict],
        industry: str = "financial_services",
        custom_negatives: List[str] = None,
        target_cpa: float = None,
    ) -> ActionPlan:
        """
        Analyze search terms and generate cleanup ActionPlan.
        
        Args:
            tenant_id: Tenant ID
            search_terms: List of dicts with:
                - term: str (the search query)
                - impressions: int
                - clicks: int
                - cost: float (spend)
                - conversions: int
                - cpa: float (optional, calculated if missing)
                - ctr: float (optional, calculated if missing)
            industry: For benchmark comparison
            custom_negatives: Additional words to flag as negative
            target_cpa: Override target CPA (otherwise uses benchmark)
        """
        # Get benchmarks for CPA comparison
        benchmarks = self.kb.get_benchmarks(tenant_id, industry)
        benchmark_cpa = target_cpa or benchmarks.get("metrics", {}).get(
            "search", {}
        ).get("avg_cpa", 50.0)
        
        # Get guardrails for forbidden words
        guardrails = self.kb.get_guardrails(tenant_id, industry)
        forbidden = guardrails.get("content_guardrails", {}).get("forbidden_words", [])
        
        # Build negative patterns list
        negative_patterns = list(self.DEFAULT_IRRELEVANT_PATTERNS)
        if custom_negatives:
            negative_patterns.extend(custom_negatives)
        
        logger.info(
            f"[{tenant_id}] Analyzing {len(search_terms)} search terms "
            f"(benchmark CPA: ${benchmark_cpa:.2f})"
        )
        
        # Classify each term
        classifications = []
        for term_data in search_terms:
            classification = self._classify_term(
                term_data, benchmark_cpa, negative_patterns, forbidden
            )
            classifications.append(classification)
        
        # Build ActionPlan
        plan = self._build_cleanup_plan(
            tenant_id, classifications, benchmark_cpa
        )
        
        return plan
    
    # ---------------------------------------------------------------------
    # Classification Logic
    # ---------------------------------------------------------------------
    
    def _classify_term(
        self,
        term_data: dict,
        benchmark_cpa: float,
        negative_patterns: List[str],
        forbidden_words: List[str],
    ) -> dict:
        """Classify a single search term."""
        term = term_data.get("term", "").strip().lower()
        impressions = term_data.get("impressions", 0)
        clicks = term_data.get("clicks", 0)
        cost = term_data.get("cost", 0.0)
        conversions = term_data.get("conversions", 0)
        
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpa = (cost / conversions) if conversions > 0 else float('inf')
        
        classification = TermClassification.NEUTRAL
        reasons = []
        confidence = 0.5
        
        # Rule 1: Pattern match - contains irrelevant word
        for pattern in negative_patterns:
            if pattern.lower() in term:
                classification = TermClassification.NEGATIVE
                reasons.append(f"Contains irrelevant pattern: '{pattern}'")
                confidence = 0.85
                break
        
        # Rule 2: Contains forbidden words from guardrails
        if classification == TermClassification.NEUTRAL:
            for forbidden in forbidden_words:
                if forbidden.lower() in term:
                    classification = TermClassification.NEGATIVE
                    reasons.append(f"Contains forbidden term: '{forbidden}'")
                    confidence = 0.9
                    break
        
        # Rule 3: High spend + zero conversions = waste
        if classification == TermClassification.NEUTRAL:
            if cost >= self.WASTE_SPEND_THRESHOLD and conversions == 0:
                classification = TermClassification.NEGATIVE
                reasons.append(f"Wasted ${cost:.2f} with 0 conversions")
                confidence = 0.9
        
        # Rule 4: Low data - need more impressions
        if classification == TermClassification.NEUTRAL:
            if impressions < self.LOW_IMPRESSION_THRESHOLD:
                classification = TermClassification.MONITOR
                reasons.append(f"Only {impressions} impressions - need more data")
                confidence = 0.4
        
        # Rule 5: Good performer - add as keyword
        if classification == TermClassification.NEUTRAL:
            if conversions > 0 and cpa <= benchmark_cpa * self.GOOD_CPA_MULTIPLIER:
                classification = TermClassification.POSITIVE
                reasons.append(
                    f"Converting at ${cpa:.2f} CPA (benchmark: ${benchmark_cpa:.2f})"
                )
                confidence = 0.8
                
                if ctr > self.HIGH_CTR_THRESHOLD:
                    confidence = 0.9
                    reasons.append(f"High CTR: {ctr:.1f}%")
        
        # Rule 6: Converting but expensive
        if classification == TermClassification.NEUTRAL:
            if conversions > 0 and cpa > benchmark_cpa * 2:
                classification = TermClassification.MONITOR
                reasons.append(
                    f"Converting but expensive: ${cpa:.2f} CPA "
                    f"(2x+ benchmark ${benchmark_cpa:.2f})"
                )
                confidence = 0.6
        
        if not reasons:
            reasons.append("No strong signal either way")
        
        return {
            "term": term_data.get("term", ""),
            "impressions": impressions,
            "clicks": clicks,
            "cost": cost,
            "conversions": conversions,
            "ctr": round(ctr, 2),
            "cpa": round(cpa, 2) if cpa != float('inf') else None,
            "classification": classification,
            "reasons": reasons,
            "confidence": confidence,
        }
    
    # ---------------------------------------------------------------------
    # ActionPlan Building
    # ---------------------------------------------------------------------
    
    def _build_cleanup_plan(
        self,
        tenant_id: str,
        classifications: List[dict],
        benchmark_cpa: float,
    ) -> ActionPlan:
        """Build ActionPlan from classifications."""
        negatives = [c for c in classifications if c["classification"] == TermClassification.NEGATIVE]
        positives = [c for c in classifications if c["classification"] == TermClassification.POSITIVE]
        monitors = [c for c in classifications if c["classification"] == TermClassification.MONITOR]
        
        total_waste = sum(c["cost"] for c in negatives)
        
        plan = ActionPlan(
            tenant_id=tenant_id,
            agent_name=self.AGENT_NAME,
            title=f"Search Terms Cleanup - {len(negatives)} negatives, {len(positives)} positives",
            description=(
                f"Analyzed {len(classifications)} search terms. "
                f"Found {len(negatives)} to negate (${total_waste:.2f} wasted), "
                f"{len(positives)} high performers to add, "
                f"{len(monitors)} to monitor."
            ),
            rationale=self._build_rationale(classifications, benchmark_cpa),
        )
        
        # Get applicable rules
        rules = self.kb.match_rules(tenant_id, {"wasted_spend_pct_above": 15})
        plan.rules_consulted = [r["id"] for r in rules]
        
        # Store full classification data in benchmarks_referenced
        plan.benchmarks_referenced = {
            "negatives": [{"term": c["term"], "cost": c["cost"], "reasons": c["reasons"]} for c in negatives],
            "positives": [{"term": c["term"], "conversions": c["conversions"], "cpa": c["cpa"]} for c in positives],
            "monitors": [{"term": c["term"], "impressions": c["impressions"]} for c in monitors],
            "total_waste": total_waste,
            "benchmark_cpa": benchmark_cpa,
        }
        
        # Add metrics operation to track improvement
        if negatives or positives:
            plan.add_operation(
                operation_name="get_campaign_metrics@v1",
                payload={
                    "metrics": ["search_terms", "wasted_spend", "negative_keywords"],
                    "context": "search_terms_cleanup",
                    "negatives_to_add": [c["term"] for c in negatives],
                    "positives_to_add": [c["term"] for c in positives],
                },
                description=(
                    f"Apply {len(negatives)} negative keywords "
                    f"(save ~${total_waste:.2f}) and "
                    f"add {len(positives)} positive terms as exact match"
                ),
                priority=OperationPriority.HIGH if total_waste > 50 else OperationPriority.MEDIUM,
            )
        
        plan.risk_score = min(0.1 + (total_waste / 500) * 0.3, 0.6)
        plan.requires_approval = total_waste > 100 or len(negatives) > 20
        plan.propose()
        
        logger.info(
            f"[{tenant_id}] Cleanup plan: {len(negatives)} negatives (${total_waste:.2f} waste), "
            f"{len(positives)} positives, {len(monitors)} monitoring"
        )
        
        return plan
    
    def _build_rationale(
        self, classifications: List[dict], benchmark_cpa: float
    ) -> str:
        """Build rationale summary."""
        negatives = [c for c in classifications if c["classification"] == TermClassification.NEGATIVE]
        positives = [c for c in classifications if c["classification"] == TermClassification.POSITIVE]
        
        parts = [f"Benchmark CPA: ${benchmark_cpa:.2f}"]
        
        if negatives:
            top_waste = sorted(negatives, key=lambda c: c["cost"], reverse=True)[:3]
            parts.append("Top wasted terms:")
            for t in top_waste:
                parts.append(f"  * '{t['term']}' - ${t['cost']:.2f} ({t['reasons'][0]})")
        
        if positives:
            parts.append("Top performing terms:")
            for t in positives[:3]:
                parts.append(
                    f"  * '{t['term']}' - {t['conversions']} conv, "
                    f"${t['cpa']:.2f} CPA"
                )
        
        return "\n".join(parts)
    
    # ---------------------------------------------------------------------
    # Quick Summary
    # ---------------------------------------------------------------------
    
    def get_summary(
        self,
        tenant_id: str,
        search_terms: List[dict],
        industry: str = "financial_services",
    ) -> dict:
        """
        Quick summary without ActionPlan. For dashboard widgets.
        """
        benchmarks = self.kb.get_benchmarks(tenant_id, industry)
        benchmark_cpa = benchmarks.get("metrics", {}).get("search", {}).get("avg_cpa", 50.0)
        guardrails = self.kb.get_guardrails(tenant_id, industry)
        forbidden = guardrails.get("content_guardrails", {}).get("forbidden_words", [])
        
        classifications = []
        for term_data in search_terms:
            c = self._classify_term(
                term_data, benchmark_cpa,
                self.DEFAULT_IRRELEVANT_PATTERNS, forbidden
            )
            classifications.append(c)
        
        negatives = [c for c in classifications if c["classification"] == TermClassification.NEGATIVE]
        positives = [c for c in classifications if c["classification"] == TermClassification.POSITIVE]
        
        return {
            "tenant_id": tenant_id,
            "total_terms": len(classifications),
            "negatives": len(negatives),
            "positives": len(positives),
            "monitoring": sum(1 for c in classifications if c["classification"] == TermClassification.MONITOR),
            "neutral": sum(1 for c in classifications if c["classification"] == TermClassification.NEUTRAL),
            "total_waste": sum(c["cost"] for c in negatives),
            "benchmark_cpa": benchmark_cpa,
            "classifications": classifications,
        }

