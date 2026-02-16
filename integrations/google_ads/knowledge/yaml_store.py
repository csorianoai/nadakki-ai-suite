# ===============================================================================
# NADAKKI AI Suite - YamlKnowledgeStore
# core/knowledge/yaml_store.py
# Day 3 - Component 1 of 4
# ===============================================================================

"""
Multi-tenant Knowledge Store backed by YAML files.

3-Layer Merge Order:
    1. Global defaults:     knowledge/global/google_ads/*.yaml
    2. Industry templates:  knowledge/industry/{vertical}/*.yaml
    3. Tenant overrides:    knowledge/{tenant_id}/google_ads/*.yaml

For 30 rules, YAML is sufficient - no vector DB needed.
Phase 2: Optional RAG integration for 100+ rules.

Usage:
    store = YamlKnowledgeStore()
    
    # Get rules for a tenant (merges global + industry + tenant)
    rules = store.get_rules("bank01", industry="financial_services")
    
    # Get specific rule by ID
    rule = store.get_rule("bank01", "rule_search_leads_01")
    
    # Get playbook
    playbook = store.get_playbook("bank01", "playbook_weekly_optimization")
    
    # Get benchmarks for industry
    benchmarks = store.get_benchmarks("bank01", industry="banking")
    
    # Validate ad copy against guardrails
    result = store.validate_copy("bank01", headlines, descriptions)
"""

from typing import Dict, List, Optional, Any, Tuple
import os
import logging

logger = logging.getLogger("nadakki.knowledge.yaml_store")

# Try to import PyYAML, fall back to simple parser
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("PyYAML not installed. Using built-in YAML parser (limited).")


def _simple_yaml_load(filepath: str) -> dict:
    """
    Minimal YAML-like parser for when PyYAML is not installed.
    Handles basic key: value pairs and lists.
    For production, always install PyYAML.
    """
    import json
    # Try JSON first (YAML is a superset of JSON)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Basic YAML parsing - enough for our structured files
    result = {}
    current_key = None
    current_list = None
    
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        if stripped.startswith('- ') and current_key:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            value = stripped[2:].strip().strip('"').strip("'")
            current_list.append(value)
        elif ':' in stripped and not stripped.startswith('-'):
            parts = stripped.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ""
            if value:
                result[key] = value
                current_key = key
                current_list = None
            else:
                current_key = key
                current_list = None
    
    return result


def load_yaml_file(filepath: str) -> dict:
    """Load a YAML file, using PyYAML if available."""
    if not os.path.exists(filepath):
        return {}
    
    try:
        if HAS_YAML:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        else:
            return _simple_yaml_load(filepath)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return {}


class YamlKnowledgeStore:
    """
    Multi-tenant knowledge store with 3-layer merge.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge"
        )
        self._cache: Dict[str, dict] = {}
        
        # Scan available knowledge
        self._scan_available()
        logger.info(f"YamlKnowledgeStore initialized (base: {self.base_path})")
    
    def _scan_available(self):
        """Scan and log what knowledge files are available."""
        global_path = os.path.join(self.base_path, "global", "google_ads")
        if os.path.exists(global_path):
            files = [f for f in os.listdir(global_path) if f.endswith('.yaml')]
            logger.info(f"  Global knowledge: {len(files)} files > {files}")
        else:
            logger.warning(f"  Global knowledge path not found: {global_path}")
    
    # ---------------------------------------------------------------------
    # File Loading with 3-Layer Merge
    # ---------------------------------------------------------------------
    
    def _load_merged(
        self,
        filename: str,
        tenant_id: str = None,
        industry: str = None,
    ) -> dict:
        """
        Load and merge a knowledge file across 3 layers.
        
        Order: global > industry > tenant
        Later layers override earlier ones for matching keys.
        Lists are concatenated (not replaced).
        """
        cache_key = f"{filename}:{tenant_id or ''}:{industry or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Layer 1: Global
        global_file = os.path.join(self.base_path, "global", "google_ads", filename)
        merged = load_yaml_file(global_file)
        
        # Layer 2: Industry
        if industry:
            industry_file = os.path.join(
                self.base_path, "industry", industry, filename
            )
            industry_data = load_yaml_file(industry_file)
            if industry_data:
                merged = self._deep_merge(merged, industry_data)
        
        # Layer 3: Tenant overrides
        if tenant_id:
            tenant_file = os.path.join(
                self.base_path, tenant_id, "google_ads", filename
            )
            tenant_data = load_yaml_file(tenant_file)
            if tenant_data:
                merged = self._deep_merge(merged, tenant_data)
        
        self._cache[cache_key] = merged
        return merged
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Deep merge two dicts. Lists are concatenated, dicts are merged recursively.
        """
        result = {**base}
        
        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # Concatenate lists, remove duplicates by 'id' if present
                    existing_ids = set()
                    for item in result[key]:
                        if isinstance(item, dict) and 'id' in item:
                            existing_ids.add(item['id'])
                    
                    merged_list = list(result[key])
                    for item in value:
                        if isinstance(item, dict) and 'id' in item:
                            if item['id'] not in existing_ids:
                                merged_list.append(item)
                            else:
                                # Override existing item with same ID
                                merged_list = [
                                    item if (isinstance(x, dict) and x.get('id') == item['id']) else x
                                    for x in merged_list
                                ]
                        else:
                            merged_list.append(item)
                    result[key] = merged_list
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    
    def get_rules(
        self,
        tenant_id: str = None,
        industry: str = None,
        tags: List[str] = None,
    ) -> List[dict]:
        """
        Get all rules, optionally filtered by tags.
        
        Returns list of rule dicts from rules.yaml.
        """
        data = self._load_merged("rules.yaml", tenant_id, industry)
        rules = data.get("rules", [])
        
        if tags:
            rules = [
                r for r in rules
                if any(t in r.get("tags", []) for t in tags)
            ]
        
        return rules
    
    def get_rule(self, tenant_id: str, rule_id: str, industry: str = None) -> Optional[dict]:
        """Get a specific rule by ID."""
        rules = self.get_rules(tenant_id, industry)
        for rule in rules:
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def get_playbooks(
        self,
        tenant_id: str = None,
        industry: str = None,
    ) -> List[dict]:
        """Get all playbooks."""
        data = self._load_merged("playbooks.yaml", tenant_id, industry)
        return data.get("playbooks", [])
    
    def get_playbook(
        self,
        tenant_id: str,
        playbook_id: str,
        industry: str = None,
    ) -> Optional[dict]:
        """Get a specific playbook by ID."""
        playbooks = self.get_playbooks(tenant_id, industry)
        for pb in playbooks:
            if pb.get("id") == playbook_id:
                return pb
        return None
    
    def get_benchmarks(
        self,
        tenant_id: str = None,
        industry: str = None,
    ) -> dict:
        """
        Get benchmarks for the tenant's industry.
        Falls back to 'default' if industry not found.
        """
        data = self._load_merged("benchmarks.yaml", tenant_id, industry)
        benchmarks = data.get("benchmarks", {})
        thresholds = data.get("thresholds", {})
        
        # Get industry-specific or default
        industry_benchmarks = benchmarks.get(
            industry, benchmarks.get("default", {})
        )
        
        return {
            "industry": industry or "default",
            "metrics": industry_benchmarks,
            "thresholds": thresholds,
        }
    
    def get_guardrails(
        self,
        tenant_id: str = None,
        industry: str = None,
    ) -> dict:
        """Get guardrails (safety limits)."""
        return self._load_merged("guardrails.yaml", tenant_id, industry)
    
    def get_templates(
        self,
        tenant_id: str = None,
        industry: str = None,
        template_type: str = None,
    ) -> dict:
        """
        Get templates. Optional filter by type (campaign, ad_copy, report).
        """
        data = self._load_merged("templates.yaml", tenant_id, industry)
        
        if template_type:
            key = f"{template_type}_templates"
            return data.get(key, {})
        
        return data
    
    def get_ad_copy_templates(
        self,
        tenant_id: str = None,
        industry: str = "financial_services",
    ) -> List[dict]:
        """Get ad copy templates for the tenant's industry."""
        data = self._load_merged("templates.yaml", tenant_id, industry)
        ad_templates = data.get("ad_copy_templates", {})
        
        # Look for industry-specific templates
        return ad_templates.get(industry, ad_templates.get("default", []))
    
    def validate_copy(
        self,
        tenant_id: str,
        headlines: List[str],
        descriptions: List[str],
        industry: str = None,
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate ad copy against guardrails.
        
        Returns: (valid, violations, warnings)
        """
        guardrails = self.get_guardrails(tenant_id, industry)
        content_rules = guardrails.get("content_guardrails", {})
        
        violations = []
        warnings = []
        
        forbidden_words = content_rules.get("forbidden_words", [])
        max_headline = content_rules.get("max_headline_length", 30)
        max_description = content_rules.get("max_description_length", 90)
        min_headlines = content_rules.get("min_headlines_per_rsa", 8)
        min_descriptions = content_rules.get("min_descriptions_per_rsa", 3)
        
        # Check minimum counts
        if len(headlines) < min_headlines:
            warnings.append(
                f"Only {len(headlines)} headlines (minimum {min_headlines} recommended)"
            )
        if len(descriptions) < min_descriptions:
            warnings.append(
                f"Only {len(descriptions)} descriptions (minimum {min_descriptions} recommended)"
            )
        
        # Check each headline
        for i, h in enumerate(headlines):
            if len(h) > max_headline:
                violations.append(f"Headline {i+1} exceeds {max_headline} chars ({len(h)})")
            
            h_lower = h.lower()
            for word in forbidden_words:
                if word.lower() in h_lower:
                    violations.append(f"Headline {i+1} contains forbidden: '{word}'")
        
        # Check each description
        for i, d in enumerate(descriptions):
            if len(d) > max_description:
                violations.append(f"Description {i+1} exceeds {max_description} chars ({len(d)})")
            
            d_lower = d.lower()
            for word in forbidden_words:
                if word.lower() in d_lower:
                    violations.append(f"Description {i+1} contains forbidden: '{word}'")
        
        return len(violations) == 0, violations, warnings
    
    # ---------------------------------------------------------------------
    # Matching Engine
    # ---------------------------------------------------------------------
    
    def match_rules(
        self,
        tenant_id: str,
        context: dict,
        industry: str = None,
    ) -> List[dict]:
        """
        Match rules that apply to a given context.
        
        Context example:
            {"goal": "leads", "channel": "search", "phase": "launch"}
        
        Returns rules where ALL 'when' conditions match the context.
        """
        rules = self.get_rules(tenant_id, industry)
        matched = []
        
        for rule in rules:
            when = rule.get("when", {})
            if self._matches_conditions(when, context):
                matched.append(rule)
        
        # Sort by confidence (highest first)
        matched.sort(key=lambda r: r.get("confidence", 0), reverse=True)
        return matched
    
    def _matches_conditions(self, when: dict, context: dict) -> bool:
        """Check if all 'when' conditions match the context."""
        if not when:
            return True
        
        for key, expected in when.items():
            if key not in context:
                continue  # Skip conditions not in context
            
            actual = context[key]
            
            # Handle comparison operators in key names
            if key.endswith("_above"):
                base_key = key.replace("_above", "")
                if base_key in context:
                    if float(context[base_key]) <= float(expected):
                        return False
            elif key.endswith("_below"):
                base_key = key.replace("_below", "")
                if base_key in context:
                    if float(context[base_key]) >= float(expected):
                        return False
            elif actual != expected:
                return False
        
        return True
    
    # ---------------------------------------------------------------------
    # Cache Management
    # ---------------------------------------------------------------------
    
    def clear_cache(self, tenant_id: str = None):
        """Clear cached knowledge. If tenant_id given, only clear that tenant."""
        if tenant_id:
            keys_to_remove = [k for k in self._cache if f":{tenant_id}:" in k]
            for k in keys_to_remove:
                del self._cache[k]
        else:
            self._cache.clear()
        logger.info(f"Knowledge cache cleared {'for ' + tenant_id if tenant_id else '(all)'}")
    
    def get_stats(self) -> dict:
        """Get store statistics."""
        global_path = os.path.join(self.base_path, "global", "google_ads")
        global_files = []
        if os.path.exists(global_path):
            global_files = [f for f in os.listdir(global_path) if f.endswith('.yaml')]
        
        return {
            "base_path": self.base_path,
            "global_files": global_files,
            "cache_size": len(self._cache),
            "has_yaml_parser": HAS_YAML,
        }
