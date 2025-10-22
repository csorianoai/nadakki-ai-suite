"""
GeoSegmentationIA - Production-Ready v2.1.1

PropÃ³sito:
  Detectar clusters geogrÃ¡ficos por performance y asignar presupuesto Ã³ptimo,
  con trazabilidad, mÃ©tricas y checks bÃ¡sicos de compliance.

CaracterÃ­sticas:
  - Contract-first + validate_request()
  - NormalizaciÃ³n y composite score
  - Clustering por tier y asignaciÃ³n de budget
  - Compliance flags (blocked_zips, disparate_impact placeholder)
  - health_check(), get_metrics(), decision_trace
  - Determinista, stdlib-only
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoSegmentationIA:
    VERSION = "v2.1.1"

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.tenant_id = tenant_id
        self.name = "GeoSegmentationIA"
        self.config = config or self._default_config()
        logger.info("GeoSegmentationIA init tenant=%s version=%s", tenant_id, self.VERSION)

    def _default_config(self) -> Dict[str, Any]:
        return {
            "geo_hierarchy": ["country", "region", "city", "zip"],
            "performance_thresholds": {
                "high": {"roas": 3.0, "conv_rate": 0.05},
                "medium": {"roas": 2.0, "conv_rate": 0.03},
                "low": {"roas": 1.5, "conv_rate": 0.02}
            },
            "budget_allocation": {"high": 0.50, "medium": 0.35, "low": 0.15},
            "compliance": {
                "check_disparate_impact": True,
                "blocked_zips": [],  # e.g., ["94110", "33101"]
                "min_population_per_segment": 1000
            },
            "clustering": {"min_cluster_size": 5, "similarity_threshold": 0.7}
        }

    # -------------------- Validaciones & helpers ------------------------------
    def validate_request(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return "invalid_input: payload must be object"
        if not data.get("segmentation_id"):
            return "invalid_input: segmentation_id required"
        geos = data.get("geo_data")
        if not isinstance(geos, list) or len(geos) == 0:
            return "invalid_input: geo_data required"
        level = data.get("optimization_level")
        if level not in ["country", "region", "city", "zip"]:
            return "invalid_input: invalid optimization_level"
        if data.get("total_budget", 0) < 0:
            return "invalid_input: total_budget must be >= 0"
        return None

    def _normalize_performance(self, geos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not geos:
            return []
        max_roas = max((g.get("roas", 0) or 0) for g in geos) or 1.0
        max_conv = max((g.get("conversion_rate", 0) or 0) for g in geos) or 1.0
        out: List[Dict[str, Any]] = []
        for g in geos:
            n_roas = (g.get("roas", 0) or 0) / max_roas
            n_conv = (g.get("conversion_rate", 0) or 0) / max_conv
            comp = n_roas * 0.6 + n_conv * 0.4
            h = dict(g)
            h["normalized_roas"] = round(n_roas, 3)
            h["normalized_conv"] = round(n_conv, 3)
            h["composite_score"] = round(comp, 3)
            out.append(h)
        return out

    def _classify_performance_tier(self, roas: float, conv_rate: float) -> str:
        th = self.config["performance_thresholds"]
        if roas >= th["high"]["roas"] and conv_rate >= th["high"]["conv_rate"]:
            return "high"
        if roas >= th["medium"]["roas"] and conv_rate >= th["medium"]["conv_rate"]:
            return "medium"
        return "low"

    def _cluster_geos(self, geos: List[Dict[str, Any]], level: str) -> List[Dict[str, Any]]:
        if not geos:
            return []
        clusters = defaultdict(list)
        for g in geos:
            clusters[g.get("performance_tier", "low")].append(g)
        min_sz = self.config["clustering"]["min_cluster_size"]
        out: List[Dict[str, Any]] = []
        for tier, members in clusters.items():
            if len(members) >= min_sz:
                out.append({
                    "cluster_id": f"{level}_{tier}",
                    "tier": tier,
                    "level": level,
                    "size": len(members),
                    "members": [m.get("geo_id") for m in members],
                    "avg_roas": round(sum(m.get("roas", 0) or 0 for m in members) / len(members), 2),
                    "avg_conv_rate": round(sum(m.get("conversion_rate", 0) or 0 for m in members) / len(members), 4),
                    "total_spend": sum(m.get("spend", 0) or 0 for m in members),
                    "total_conversions": sum(m.get("conversions", 0) or 0 for m in members)
                })
        return out

    def _allocate_budget(self, clusters: List[Dict[str, Any]], total_budget: float) -> List[Dict[str, Any]]:
        rules = self.config["budget_allocation"]
        buckets = defaultdict(list)
        for c in clusters:
            buckets[c["tier"]].append(c)
        allocations: List[Dict[str, Any]] = []
        for tier, pct in rules.items():
            tier_clusters = buckets.get(tier, [])
            if not tier_clusters:
                continue
            per = total_budget * pct / len(tier_clusters)
            for c in tier_clusters:
                expected_conv = int(per / c["avg_roas"]) if c["avg_roas"] > 0 else 0
                allocations.append({
                    "cluster_id": c["cluster_id"],
                    "tier": tier,
                    "level": c["level"],
                    "allocated_budget": round(per, 2),
                    "expected_roas": c["avg_roas"],
                    "expected_conversions": expected_conv,
                    "geo_count": c["size"],
                    "members": c["members"]
                })
        return allocations

    def _compliance_check(self, clusters: List[Dict[str, Any]], geos: List[Dict[str, Any]]) -> Dict[str, Any]:
        issues: List[str] = []
        blocked = set(self.config["compliance"]["blocked_zips"])
        for g in geos:
            z = g.get("zip")
            if z and z in blocked:
                issues.append(f"blocked_zip:{z}")
        return {
            "status": "fail" if issues else "pass",
            "issues": issues,
            "disparate_impact_checked": self.config["compliance"]["check_disparate_impact"]
        }

    def _generate_recommendations(self, allocations: List[Dict[str, Any]]) -> List[str]:
        recs: List[str] = []
        highs = [a for a in allocations if a["tier"] == "high"]
        if highs:
            top = max(highs, key=lambda x: x["expected_roas"])
            recs.append(f"Increase spend in {top['cluster_id']} (ROAS {top['expected_roas']:.2f})")
        lows = [a for a in allocations if a["tier"] == "low"]
        if lows:
            bottom = min(lows, key=lambda x: x["expected_roas"])
            recs.append(f"Reduce or test {bottom['cluster_id']} (ROAS {bottom['expected_roas']:.2f})")
        recs.append("Consider expansion to similar geos in high-performing clusters")
        return recs

    # ------------------------------- API -------------------------------------
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()
        err = self.validate_request(data)
        if err:
            return self._error_response(err, int((time.perf_counter() - t0) * 1000))

        decision_trace: List[str] = []
        segmentation_id = data["segmentation_id"]
        geos = data["geo_data"]
        total_budget = float(data.get("total_budget", 0.0))
        level = data["optimization_level"]

        decision_trace.append(f"geos={len(geos)}")
        decision_trace.append(f"level={level}")

        normalized = self._normalize_performance(geos)
        for g in normalized:
            g["performance_tier"] = self._classify_performance_tier(
                float(g.get("roas", 0.0) or 0.0),
                float(g.get("conversion_rate", 0.0) or 0.0)
            )

        tier_counts = defaultdict(int)
        for g in normalized:
            tier_counts[g["performance_tier"]] += 1
        decision_trace.append(f"tiers=high:{tier_counts['high']},medium:{tier_counts['medium']},low:{tier_counts['low']}")

        clusters = self._cluster_geos(normalized, level)
        decision_trace.append(f"clusters={len(clusters)}")

        allocations = self._allocate_budget(clusters, total_budget)
        decision_trace.append(f"allocations={len(allocations)}")

        total_spend = sum((g.get("spend", 0) or 0) for g in geos)
        total_revenue = sum((g.get("revenue", 0) or 0) for g in geos)
        total_conversions = sum((g.get("conversions", 0) or 0) for g in geos)
        clicks_total = sum((g.get("clicks", 0) or 0) for g in geos) or 1

        performance_summary = {
            "total_spend": total_spend,
            "total_revenue": total_revenue,
            "total_conversions": total_conversions,
            "overall_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0.0,
            "overall_conv_rate": round(total_conversions / clicks_total, 4),
            "geos_analyzed": len(geos),
            "clusters_formed": len(clusters)
        }

        recommendations = self._generate_recommendations(allocations)
        decision_trace.append(f"recommendations={len(recommendations)}")

        compliance = self._compliance_check(clusters, geos)
        decision_trace.append(f"compliance={compliance['status']}")

        latency = int((time.perf_counter() - t0) * 1000)
        out = {
            "tenant_id": self.tenant_id,
            "segmentation_id": segmentation_id,
            "optimization_level": level,
            "clusters": clusters,
            "budget_allocations": allocations,
            "performance_summary": performance_summary,
            "recommendations": recommendations,
            "compliance": compliance,
            "decision_trace": decision_trace,
            "version": self.VERSION,
            "latency_ms": latency
        }
        logger.info(
            "geo_segmentation result tenant=%s id=%s clusters=%d budget=%.2f latency=%dms",
            self.tenant_id, segmentation_id, len(clusters), total_budget, latency
        )
        return out

    # ----------------------- Health & MÃ©tricas --------------------------------
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "version": self.VERSION, "tenant_id": self.tenant_id}

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_name": self.name,
            "agent_version": self.VERSION,
            "tenant_id": self.tenant_id,
            "geo_levels_supported": len(self.config["geo_hierarchy"]),
            "status": "healthy"
        }

    # --------------------------- Errores --------------------------------------
    def _error_response(self, error: str, latency_ms: int) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "status": "error",
            "error": error,
            "latency_ms": latency_ms,
            "version": self.VERSION
        }
