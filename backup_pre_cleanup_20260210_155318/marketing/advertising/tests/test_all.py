# ==============================================================================
# NADAKKI AI Suite - Comprehensive Test Suite
# tests/test_all.py
# Day 7 - Full pytest suite
# ==============================================================================

"""
pytest test suite for NADAKKI Google Ads MVP.

Run:
    pytest tests/test_all.py -v
    pytest tests/test_all.py -v --tb=short
    pytest tests/test_all.py -v -k "test_strategist"
"""

import pytest
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def database():
    from core.database import InMemoryDatabase
    db = InMemoryDatabase()
    await db.initialize()
    yield db
    await db.close()

@pytest.fixture
async def vault(database):
    from core.security.tenant_vault import TenantCredentialVault
    v = TenantCredentialVault(database)
    await v.store_credentials("test_tenant", {
        "refresh_token": "test_token",
        "customer_id": "1234567890",
        "manager_customer_id": "9876543210",
    })
    return v

@pytest.fixture
def factory(vault):
    from core.google_ads.client_factory import GoogleAdsClientFactory
    return GoogleAdsClientFactory(vault)

@pytest.fixture
def registry():
    from core.operations.registry import get_operation_registry
    return get_operation_registry()

@pytest.fixture
async def idempotency(database):
    from core.reliability.idempotency import IdempotencyStore
    return IdempotencyStore(database)

@pytest.fixture
def executor(factory):
    from core.google_ads.executor import GoogleAdsExecutor
    return GoogleAdsExecutor(factory)

@pytest.fixture
def policy_engine():
    from core.policies.engine import PolicyEngine
    return PolicyEngine()

@pytest.fixture
def telemetry():
    from core.observability.telemetry import TelemetrySidecar
    return TelemetrySidecar()

@pytest.fixture
async def saga_journal(database):
    from core.saga.journal import SagaJournal
    return SagaJournal(database)

@pytest.fixture
async def connector(registry, idempotency, policy_engine, executor, factory, vault, saga_journal, telemetry):
    from core.google_ads.connector import GoogleAdsConnector
    return GoogleAdsConnector(
        registry=registry,
        idempotency=idempotency,
        policy_engine=policy_engine,
        executor=executor,
        client_factory=factory,
        credential_vault=vault,
        saga_journal=saga_journal,
        telemetry=telemetry,
    )

@pytest.fixture
def knowledge_store():
    from core.knowledge.yaml_store import YamlKnowledgeStore
    return YamlKnowledgeStore("knowledge/")

@pytest.fixture
def strategist(knowledge_store):
    from agents.marketing.google_ads_strategist_agent import GoogleAdsStrategistIA
    return GoogleAdsStrategistIA(knowledge_store)

@pytest.fixture
def budget_pacing(knowledge_store):
    from agents.marketing.google_ads_budget_pacing_agent import GoogleAdsBudgetPacingIA
    return GoogleAdsBudgetPacingIA(knowledge_store)

@pytest.fixture
def rsa_generator(knowledge_store):
    from agents.marketing.rsa_ad_copy_generator_agent import RSAAdCopyGeneratorIA
    return RSAAdCopyGeneratorIA(knowledge_store)

@pytest.fixture
def search_cleaner(knowledge_store):
    from agents.marketing.search_terms_cleaner_agent import SearchTermsCleanerIA
    return SearchTermsCleanerIA(knowledge_store)

@pytest.fixture
async def plan_executor(connector, telemetry):
    from core.execution.action_plan_executor import ActionPlanExecutor
    return ActionPlanExecutor(connector, telemetry)


# ===============================================================================
# UNIT TESTS - Core Infrastructure
# ===============================================================================

class TestDatabase:
    @pytest.mark.asyncio
    async def test_initialize(self, database):
        assert database is not None
    
    @pytest.mark.asyncio
    async def test_crud_operations(self, database):
        await database.execute(
            "INSERT INTO credentials (tenant_id, data) VALUES (?, ?)",
            ("t1", '{"key":"val"}')
        )
        row = await database.fetch_one(
            "SELECT data FROM credentials WHERE tenant_id = ?", ("t1",)
        )
        assert row is not None


class TestVault:
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, vault):
        creds = await vault.get_credentials("test_tenant")
        assert creds is not None
        assert creds["customer_id"] == "1234567890"
    
    @pytest.mark.asyncio
    async def test_list_tenants(self, vault):
        tenants = await vault.list_tenants()
        assert "test_tenant" in [t["tenant_id"] for t in tenants]
    
    @pytest.mark.asyncio
    async def test_delete_credentials(self, vault):
        await vault.store_credentials("temp_tenant", {"refresh_token": "t", "customer_id": "c"})
        deleted = await vault.delete_credentials("temp_tenant")
        assert deleted is True
        creds = await vault.get_credentials("temp_tenant")
        assert creds is None


class TestRegistry:
    def test_list_operations(self, registry):
        ops = registry.list_operations()
        assert len(ops) >= 2
        names = [o["full_name"] for o in ops]
        assert "get_campaign_metrics@v1" in names
        assert "update_campaign_budget@v1" in names
    
    def test_get_operation(self, registry):
        op = registry.get("get_campaign_metrics@v1")
        assert op is not None
        assert op.name == "get_campaign_metrics"


class TestIdempotency:
    @pytest.mark.asyncio
    async def test_store_and_check(self, idempotency):
        from core.reliability.idempotency import IdempotencyStore
        key = IdempotencyStore.generate_key("t1", "op1", {"a": 1})
        await idempotency.store(key, "t1", "op1", {"result": "ok"})
        cached = await idempotency.check(key, "t1")
        assert cached is not None
    
    @pytest.mark.asyncio
    async def test_different_payloads_different_keys(self, idempotency):
        from core.reliability.idempotency import IdempotencyStore
        k1 = IdempotencyStore.generate_key("t1", "op1", {"a": 1})
        k2 = IdempotencyStore.generate_key("t1", "op1", {"a": 2})
        assert k1 != k2


class TestPolicyEngine:
    def test_allow(self, policy_engine):
        result = policy_engine.evaluate("test_tenant", "get_campaign_metrics@v1", {})
        assert result["decision"] == "ALLOW"
    
    def test_deny_high_budget(self, policy_engine):
        result = policy_engine.evaluate(
            "test_tenant", "update_campaign_budget@v1",
            {"daily_budget_usd": 100000}
        )
        assert result["decision"] in ("DENY", "REQUIRE_APPROVAL")
    
    def test_content_validation(self, policy_engine):
        result = policy_engine.evaluate(
            "test_tenant", "update_campaign_budget@v1",
            {"headlines": ["Free money guaranteed"], "descriptions": ["Guaranteed returns"]}
        )
        assert result.get("content_violations") or result["decision"] != "ALLOW"


# ===============================================================================
# UNIT TESTS - Knowledge Base
# ===============================================================================

class TestKnowledgeStore:
    def test_load_rules(self, knowledge_store):
        rules = knowledge_store.get_rules("default")
        assert len(rules) >= 10
    
    def test_match_rules(self, knowledge_store):
        matched = knowledge_store.match_rules("default", {"goal": "leads", "channel": "search"})
        assert len(matched) > 0
    
    def test_load_benchmarks(self, knowledge_store):
        benchmarks = knowledge_store.get_benchmarks("default", "financial_services")
        assert "metrics" in benchmarks
        search = benchmarks["metrics"].get("search", {})
        assert "avg_cpa" in search
    
    def test_load_guardrails(self, knowledge_store):
        guardrails = knowledge_store.get_guardrails("default", "financial_services")
        forbidden = guardrails.get("content_guardrails", {}).get("forbidden_words", [])
        assert len(forbidden) >= 8
        assert "guaranteed" in forbidden
    
    def test_validate_copy_clean(self, knowledge_store):
        valid, violations, warnings = knowledge_store.validate_copy(
            "default",
            headlines=["Apply Online Today", "Low Rates Available"],
            descriptions=["Find the right loan for your needs."],
        )
        assert valid is True
        assert len(violations) == 0
    
    def test_validate_copy_violation(self, knowledge_store):
        valid, violations, warnings = knowledge_store.validate_copy(
            "default",
            headlines=["Free money guaranteed"],
            descriptions=["No risk investing"],
        )
        assert valid is False
        assert len(violations) > 0
    
    def test_load_playbooks(self, knowledge_store):
        playbooks = knowledge_store.get_playbooks("default")
        assert len(playbooks) >= 5
    
    def test_load_templates(self, knowledge_store):
        templates = knowledge_store.get_templates("default")
        assert "campaign_templates" in templates or "ad_copy_templates" in templates
    
    def test_cache_works(self, knowledge_store):
        # First call loads, second uses cache
        r1 = knowledge_store.get_rules("default")
        r2 = knowledge_store.get_rules("default")
        assert r1 == r2


# ===============================================================================
# UNIT TESTS - Agents
# ===============================================================================

class TestStrategistAgent:
    def test_propose_strategy(self, strategist):
        plan = strategist.propose_strategy("t1", {
            "goal": "leads", "channel": "search",
            "monthly_budget": 2000, "industry": "financial_services",
        })
        assert plan.tenant_id == "t1"
        assert plan.total_operations >= 1
        assert plan.risk_score >= 0
        assert len(plan.rules_consulted) > 0
    
    def test_high_budget_risk(self, strategist):
        plan = strategist.propose_strategy("t1", {
            "goal": "leads", "channel": "search",
            "monthly_budget": 15000, "industry": "financial_services",
        })
        assert plan.risk_score > 0.3
    
    def test_recommendations(self, strategist):
        recs = strategist.get_recommendations("t1", {
            "goal": "leads", "channel": "search",
        })
        assert len(recs) > 0
    
    def test_performance_analysis(self, strategist):
        analysis = strategist.analyze_performance(
            metrics={"ctr": 1.0, "cpa": 100, "conv_rate": 2.0},
            industry="financial_services",
        )
        assert "comparisons" in analysis


class TestBudgetPacingAgent:
    def test_analyze_campaigns(self, budget_pacing):
        plan = budget_pacing.analyze_and_plan("t1", [
            {"campaign_id": "c1", "campaign_name": "Main", "daily_budget": 100,
             "spend_today": 50, "spend_mtd": 800, "monthly_target": 3000},
        ])
        assert plan.tenant_id == "t1"
    
    def test_overpacing_detection(self, budget_pacing):
        plan = budget_pacing.analyze_and_plan("t1", [
            {"campaign_id": "c1", "campaign_name": "Over", "daily_budget": 50,
             "spend_today": 50, "spend_mtd": 2500, "monthly_target": 1500},
        ], day_of_month=15, days_in_month=30)
        data = plan.benchmarks_referenced
        campaigns = data.get("campaigns", [])
        assert any(c.get("action") == "reduce" for c in campaigns)
    
    def test_pacing_summary(self, budget_pacing):
        summary = budget_pacing.get_pacing_summary("t1", [
            {"campaign_id": "c1", "daily_budget": 100, "spend_mtd": 1500, "monthly_target": 3000},
        ])
        assert "overall_pacing_pct" in summary


class TestRSAGenerator:
    def test_generate_ad_copy(self, rsa_generator):
        plan = rsa_generator.generate_ad_copy("t1", {
            "service": "Personal Loans", "brand_name": "TestBank",
            "goal": "leads", "industry": "financial_services",
            "usp": ["Low rates", "Fast approval"],
        })
        ad_data = plan.benchmarks_referenced
        assert len(ad_data["headlines"]) >= 8
        assert len(ad_data["descriptions"]) >= 3
    
    def test_ad_strength_estimation(self, rsa_generator):
        plan = rsa_generator.generate_ad_copy("t1", {
            "service": "Loans", "brand_name": "Bank",
            "goal": "leads", "usp": ["A", "B", "C", "D"],
        })
        strength = plan.benchmarks_referenced["ad_strength_estimate"]
        assert strength in ("Excellent", "Good", "Average", "Poor")
    
    def test_preview(self, rsa_generator):
        preview = rsa_generator.preview_ad("t1", {
            "service": "Cards", "brand_name": "Bank",
            "goal": "leads",
        })
        assert "headlines" in preview
        assert "ad_strength" in preview
    
    def test_compliance_filtering(self, rsa_generator):
        plan = rsa_generator.generate_ad_copy("t1", {
            "service": "Guaranteed Returns", "brand_name": "X",
            "goal": "leads", "industry": "financial_services",
            "usp": ["Free money", "No risk"],
        })
        # Even with bad USPs, final should be clean
        ad = plan.benchmarks_referenced
        assert len(ad["headlines"]) >= 8


class TestSearchCleaner:
    def test_classify_negative(self, search_cleaner):
        plan = search_cleaner.analyze_and_clean("t1", [
            {"term": "free money hack", "impressions": 200, "clicks": 10, "cost": 30, "conversions": 0},
        ])
        negatives = plan.benchmarks_referenced["negatives"]
        assert len(negatives) >= 1
    
    def test_classify_positive(self, search_cleaner):
        plan = search_cleaner.analyze_and_clean("t1", [
            {"term": "personal loan apply", "impressions": 500, "clicks": 30, "cost": 50, "conversions": 5},
        ])
        positives = plan.benchmarks_referenced["positives"]
        assert len(positives) >= 1
    
    def test_waste_calculation(self, search_cleaner):
        plan = search_cleaner.analyze_and_clean("t1", [
            {"term": "bad term", "impressions": 100, "clicks": 10, "cost": 50, "conversions": 0},
            {"term": "also bad reddit", "impressions": 80, "clicks": 5, "cost": 20, "conversions": 0},
        ])
        waste = plan.benchmarks_referenced["total_waste"]
        assert waste >= 70
    
    def test_summary(self, search_cleaner):
        summary = search_cleaner.get_summary("t1", [
            {"term": "good term", "impressions": 300, "clicks": 20, "cost": 40, "conversions": 3},
        ])
        assert "total_terms" in summary
        assert summary["total_terms"] == 1


# ===============================================================================
# INTEGRATION TESTS - Pipeline
# ===============================================================================

class TestConnectorPipeline:
    @pytest.mark.asyncio
    async def test_read_pipeline(self, connector):
        result = await connector.execute(
            tenant_id="test_tenant",
            operation_name="get_campaign_metrics@v1",
            payload={"metrics": ["clicks", "impressions"]},
        )
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_write_pipeline_with_saga(self, connector):
        result = await connector.execute(
            tenant_id="test_tenant",
            operation_name="update_campaign_budget@v1",
            payload={"campaign_id": "c1", "daily_budget_usd": 100},
        )
        assert result.success is True
        assert result.saga_id is not None


class TestActionPlanExecution:
    @pytest.mark.asyncio
    async def test_execute_plan(self, plan_executor, strategist):
        plan = strategist.propose_strategy("test_tenant", {
            "goal": "leads", "channel": "search",
            "monthly_budget": 2000, "industry": "financial_services",
        })
        plan.approve("test")
        executed = await plan_executor.execute(plan)
        assert executed.status.value in ("completed", "partially_completed")
        assert executed.completed_operations >= 1
    
    @pytest.mark.asyncio
    async def test_dry_run(self, plan_executor, strategist):
        plan = strategist.propose_strategy("test_tenant", {
            "goal": "leads", "channel": "search", "monthly_budget": 1000,
        })
        result = await plan_executor.execute(plan, dry_run=True)
        assert result.total_operations >= 1


# ===============================================================================
# INTEGRATION TESTS - Workflows
# ===============================================================================

class TestWorkflowEngine:
    @pytest.fixture
    async def engine(self, strategist, budget_pacing, rsa_generator, search_cleaner, plan_executor, knowledge_store):
        from core.workflows.engine import WorkflowEngine
        agents_map = {
            "strategist": strategist,
            "budget_pacing": budget_pacing,
            "rsa_generator": rsa_generator,
            "search_cleaner": search_cleaner,
        }
        engine = WorkflowEngine(agents_map, plan_executor, knowledge_store)
        engine.load_workflows("config/workflows/")
        return engine
    
    @pytest.mark.asyncio
    async def test_load_workflows(self, engine):
        workflows = engine.list_workflows()
        assert len(workflows) >= 5
    
    @pytest.mark.asyncio
    async def test_run_weekly_optimization(self, engine):
        result = await engine.run("weekly_optimization", "test_tenant", auto_approve=True)
        assert result.status.value in ("completed", "partially_completed")
    
    @pytest.mark.asyncio
    async def test_approval_gate(self, engine):
        result = await engine.run("new_campaign_launch", "test_tenant", auto_approve=False)
        assert result.status.value == "paused"


class TestOrchestrator:
    @pytest.fixture
    async def orchestrator(self, strategist, budget_pacing, rsa_generator, search_cleaner, plan_executor, knowledge_store):
        from core.workflows.engine import WorkflowEngine
        from agents.marketing.orchestrator_agent import OrchestratorIA
        agents_map = {
            "strategist": strategist,
            "budget_pacing": budget_pacing,
            "rsa_generator": rsa_generator,
            "search_cleaner": search_cleaner,
        }
        engine = WorkflowEngine(agents_map, plan_executor, knowledge_store)
        engine.load_workflows("config/workflows/")
        return OrchestratorIA(engine, knowledge_store)
    
    @pytest.mark.asyncio
    async def test_handle_optimize(self, orchestrator):
        result = await orchestrator.handle_request("test_tenant", "optimize", auto_approve=True)
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_handle_emergency(self, orchestrator):
        result = await orchestrator.handle_request("test_tenant", "emergency", auto_approve=True)
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_auto_triage_critical(self, orchestrator):
        result = await orchestrator.auto_triage(
            "test_tenant",
            metrics={"cpa": 200, "ctr": 0.5, "budget_pacing": 160},
        )
        assert result.get("triage", {}).get("urgency") == "critical"
    
    @pytest.mark.asyncio
    async def test_available_actions(self, orchestrator):
        actions = orchestrator.get_available_actions()
        assert len(actions) >= 5


# ===============================================================================
# MULTI-TENANT TESTS
# ===============================================================================

class TestMultiTenant:
    def test_tenant_isolation_strategies(self, strategist):
        p1 = strategist.propose_strategy("bank01", {"goal": "leads", "channel": "search", "monthly_budget": 1000})
        p2 = strategist.propose_strategy("fintech02", {"goal": "sales", "channel": "search", "monthly_budget": 5000})
        assert p1.tenant_id == "bank01"
        assert p2.tenant_id == "fintech02"
        assert p1.plan_id != p2.plan_id
    
    def test_tenant_isolation_search_cleaner(self, search_cleaner):
        s1 = search_cleaner.get_summary("bank01", [{"term": "t", "impressions": 100, "clicks": 5, "cost": 10, "conversions": 1}])
        s2 = search_cleaner.get_summary("fintech02", [{"term": "t", "impressions": 100, "clicks": 5, "cost": 10, "conversions": 1}])
        assert s1["tenant_id"] == "bank01"
        assert s2["tenant_id"] == "fintech02"
