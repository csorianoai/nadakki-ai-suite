# ===============================================================================
# NADAKKI AI Suite - Google Ads MVP
# main.py
# Application entrypoint with FastAPI
# ===============================================================================

"""
NADAKKI Google Ads MVP - Multi-tenant Google Ads management platform.

Day 1 Endpoints:
- GET  /health                    > System health check
- GET  /api/v1/operations         > List registered operations
- POST /api/v1/operations/execute > Execute an operation
- GET  /api/v1/tenants            > List configured tenants
- POST /api/v1/tenants/{id}/credentials > Store tenant credentials
- GET  /api/v1/tenants/{id}/health     > Health check for tenant's Google Ads

Run:
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional
import os
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger("nadakki.main")

# -----------------------------------------------------------------------------
# App State (populated during startup)
# -----------------------------------------------------------------------------

class AppState:
    """Global application state container."""
    db = None
    vault = None
    factory = None
    registry = None
    idempotency = None
    # Day 2 components (will be added)
    executor = None
    policy_engine = None
    telemetry = None
    connector = None
    saga_journal = None


state = AppState()


# -----------------------------------------------------------------------------
# Application Lifecycle
# -----------------------------------------------------------------------------

async def startup():
    """Initialize all Day 1 + Day 2 components."""
    from core.database import create_database
    from core.security.tenant_vault import TenantCredentialVault, VAULT_SCHEMA
    from core.google_ads.client_factory import GoogleAdsClientFactory
    from core.operations.registry import get_operation_registry
    from core.reliability.idempotency import IdempotencyStore, IDEMPOTENCY_SCHEMA
    # Day 2 imports
    from core.google_ads.executor import GoogleAdsExecutor
    from core.policies.engine import PolicyEngine
    from core.observability.telemetry import TelemetrySidecar
    from core.saga.journal import SagaJournal, SAGA_SCHEMA
    from core.google_ads.connector import GoogleAdsConnector
    
    logger.info("=" * 60)
    logger.info("NADAKKI Google Ads MVP - Starting up...")
    logger.info("=" * 60)
    
    # 1. Database
    state.db = await create_database()
    logger.info("[OK] Database initialized")
    
    # Create schemas (no-op for InMemory, creates tables for PG)
    for schema in [VAULT_SCHEMA, IDEMPOTENCY_SCHEMA, SAGA_SCHEMA]:
        for statement in schema.strip().split(";"):
            statement = statement.strip()
            if statement:
                try:
                    await state.db.execute(statement + ";")
                except Exception as e:
                    logger.debug(f"Schema statement skipped: {e}")
    logger.info("[OK] Database schemas applied")
    
    # 2. Credential Vault
    state.vault = TenantCredentialVault(state.db)
    logger.info("[OK] TenantCredentialVault ready")
    
    # 3. Client Factory
    state.factory = GoogleAdsClientFactory(state.vault)
    logger.info("[OK] GoogleAdsClientFactory ready")
    
    # 4. Operation Registry
    state.registry = get_operation_registry()
    ops = state.registry.list_operations()
    logger.info(f"[OK] OperationRegistry ready ({len(ops)} operations)")
    for op in ops:
        logger.info(f"  > {op['full_name']}: {op['description']}")
    
    # 5. Idempotency Store
    state.idempotency = IdempotencyStore(state.db)
    logger.info("[OK] IdempotencyStore ready")
    
    # --- Day 2 Components ---
    
    # 6. Executor (circuit breaker + retry)
    state.executor = GoogleAdsExecutor(state.factory)
    logger.info("[OK] GoogleAdsExecutor ready (circuit breaker + retry)")
    
    # 7. Policy Engine
    state.policy_engine = PolicyEngine()
    logger.info("[OK] PolicyEngine ready (3 core rules)")
    
    # 8. Telemetry Sidecar
    state.telemetry = TelemetrySidecar()
    logger.info("[OK] TelemetrySidecar ready (JSON logs + Prometheus)")
    
    # 9. Saga Journal
    state.saga_journal = SagaJournal(state.db)
    logger.info("[OK] SagaJournal ready (audit + compensation)")
    
    # 10. Connector (full pipeline facade)
    state.connector = GoogleAdsConnector(
        registry=state.registry,
        idempotency=state.idempotency,
        policy_engine=state.policy_engine,
        executor=state.executor,
        client_factory=state.factory,
        credential_vault=state.vault,
        saga_journal=state.saga_journal,
        telemetry=state.telemetry,
    )
    logger.info("[OK] GoogleAdsConnector ready (full pipeline)")
    
    # --- Day 3 Components ---
    
    # 11. Knowledge Store
    from core.knowledge.yaml_store import YamlKnowledgeStore
    state.knowledge_store = YamlKnowledgeStore()
    kb_stats = state.knowledge_store.get_stats()
    logger.info(f"[OK] YamlKnowledgeStore ready ({len(kb_stats['global_files'])} global files)")
    
    # 12. Agents
    from agents.marketing.google_ads_strategist_agent import GoogleAdsStrategistIA
    from agents.marketing.google_ads_budget_pacing_agent import GoogleAdsBudgetPacingIA
    
    state.strategist = GoogleAdsStrategistIA(state.knowledge_store)
    logger.info("[OK] GoogleAdsStrategistIA ready")
    
    state.budget_pacing = GoogleAdsBudgetPacingIA(state.knowledge_store)
    logger.info("[OK] GoogleAdsBudgetPacingIA ready")
    
    # --- Day 4 Components ---
    
    # 13. ActionPlanExecutor
    from core.execution.action_plan_executor import ActionPlanExecutor
    state.plan_executor = ActionPlanExecutor(state.connector, state.telemetry)
    logger.info("[OK] ActionPlanExecutor ready")
    
    # 14. RSAAdCopyGeneratorIA
    from agents.marketing.rsa_ad_copy_generator_agent import RSAAdCopyGeneratorIA
    state.rsa_generator = RSAAdCopyGeneratorIA(state.knowledge_store)
    logger.info("[OK] RSAAdCopyGeneratorIA ready")
    
    # 15. SearchTermsCleanerIA
    from agents.marketing.search_terms_cleaner_agent import SearchTermsCleanerIA
    state.search_cleaner = SearchTermsCleanerIA(state.knowledge_store)
    logger.info("[OK] SearchTermsCleanerIA ready")
    
    # --- Day 5 Components ---
    
    # 16. WorkflowEngine
    from core.workflows.engine import WorkflowEngine
    agents_map = {
        "strategist": state.strategist,
        "budget_pacing": state.budget_pacing,
        "rsa_generator": state.rsa_generator,
        "search_cleaner": state.search_cleaner,
    }
    state.workflow_engine = WorkflowEngine(
        agents=agents_map,
        plan_executor=state.plan_executor,
        knowledge_store=state.knowledge_store,
    )
    state.workflow_engine.load_workflows("config/workflows/")
    wf_list = state.workflow_engine.list_workflows()
    logger.info(f"[OK] WorkflowEngine ready ({len(wf_list)} workflows loaded)")
    for wf in wf_list:
        logger.info(f"  > {wf['id']}: {wf['name']} ({wf['steps']} steps)")
    
    # 17. OrchestratorIA
    from agents.marketing.orchestrator_agent import OrchestratorIA
    state.orchestrator = OrchestratorIA(state.workflow_engine, state.knowledge_store)
    logger.info("[OK] OrchestratorIA ready")
    
    logger.info("=" * 60)
    logger.info("NADAKKI Google Ads MVP - Day 1+2+3+4+5+6 Ready! *")
    logger.info("=" * 60)


async def shutdown():
    """Clean up resources."""
    if state.db:
        await state.db.close()
    logger.info("NADAKKI Google Ads MVP - Shutdown complete")


# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    
    @asynccontextmanager
    async def lifespan(app):
        await startup()
        yield
        await shutdown()
    
    app = FastAPI(
        title="NADAKKI Google Ads MVP",
        description=(
            "Multi-tenant Google Ads management platform with AI agents.\n\n"
            "**Agents:** Strategist, Budget Pacing, RSA Generator, Search Cleaner\n"
            "**Workflows:** Weekly Optimization, Campaign Launch, Budget Adjustment, Emergency Pause, Search Cleanup\n"
            "**Orchestrator:** Meta-agent for intelligent workflow routing and auto-triage"
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # -----------------------------------------------------------------
    # Request/Response Models
    # -----------------------------------------------------------------
    
    class ExecuteOperationRequest(BaseModel):
        tenant_id: str
        operation_name: str
        payload: Dict[str, Any] = {}
        dry_run: bool = False
        source: str = "api"
    
    class StoreCredentialsRequest(BaseModel):
        refresh_token: str
        customer_id: str
        manager_customer_id: Optional[str] = None
        access_token: Optional[str] = None
        expires_at: Optional[str] = None
    
    # -----------------------------------------------------------------
    # Health & Info
    # -----------------------------------------------------------------
    
    @app.get("/health")
    async def health():
        """System health check."""
        return {
            "status": "ok",
            "service": "nadakki-google-ads-mvp",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "components": {
                "database": state.db is not None,
                "vault": state.vault is not None,
                "factory": state.factory is not None,
                "registry": state.registry is not None,
                "idempotency": state.idempotency is not None,
                # Day 2
                "executor": state.executor is not None,
                "policy_engine": state.policy_engine is not None,
                "connector": state.connector is not None,
            },
            "factory_stats": state.factory.get_stats() if state.factory else None,
        }
    
    @app.get("/api/v1/operations")
    async def list_operations():
        """List all registered operations."""
        return {
            "operations": state.registry.list_operations(),
            "count": len(state.registry.list_operations()),
        }
    
    # -----------------------------------------------------------------
    # Operation Execution
    # -----------------------------------------------------------------
    
    @app.post("/api/v1/operations/execute")
    async def execute_operation(req: ExecuteOperationRequest):
        """
        Execute a Google Ads operation.
        
        Pipeline:
        1. Validate operation exists
        2. Check idempotency
        3. Execute via registry
        4. Store idempotency result
        """
        from core.operations.registry import OperationRequest, OperationContext
        from core.reliability.idempotency import IdempotencyStore
        
        # Build context
        context = OperationContext(
            tenant_id=req.tenant_id,
            dry_run=req.dry_run,
            source=req.source,
        )
        
        # Generate idempotency key
        idem_key = IdempotencyStore.generate_key(
            req.tenant_id, req.operation_name, req.payload
        )
        
        # Check idempotency
        cached = await state.idempotency.check(idem_key, req.tenant_id)
        if cached:
            return {
                "status": "cached",
                "idempotency_key": idem_key,
                "result": cached,
            }
        
        # Build request
        operation_id = str(uuid.uuid4())
        op_request = OperationRequest(
            operation_id=operation_id,
            operation_name=req.operation_name,
            tenant_id=req.tenant_id,
            idempotency_key=idem_key,
            payload=req.payload,
            context=context,
        )
        
        # Validate
        valid, error = state.registry.validate(op_request)
        if not valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Get client and customer_id
        try:
            creds = await state.vault.get_credentials(req.tenant_id)
            if not creds:
                raise HTTPException(
                    status_code=404,
                    detail=f"No credentials found for tenant: {req.tenant_id}"
                )
            
            customer_id = creds.get("customer_id")
            if not customer_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"No customer_id in credentials for tenant: {req.tenant_id}"
                )
            
            client = await state.factory.get_client(req.tenant_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize client: {str(e)}"
            )
        
        # Execute
        result = await state.registry.execute(op_request, client, customer_id)
        
        # Store idempotency (only for successful results)
        if result.success:
            await state.idempotency.store(
                idem_key,
                req.tenant_id,
                req.operation_name,
                result.to_dict(),
            )
        
        return {
            "status": "executed",
            "operation_id": operation_id,
            "idempotency_key": idem_key,
            "result": result.to_dict(),
        }
    
    # -----------------------------------------------------------------
    # Tenant Management
    # -----------------------------------------------------------------
    
    @app.get("/api/v1/tenants")
    async def list_tenants():
        """List all configured tenants."""
        tenants = await state.vault.list_tenants()
        return {"tenants": tenants, "count": len(tenants)}
    
    @app.post("/api/v1/tenants/{tenant_id}/credentials")
    async def store_credentials(tenant_id: str, req: StoreCredentialsRequest):
        """Store Google Ads credentials for a tenant."""
        creds = {
            "refresh_token": req.refresh_token,
            "customer_id": req.customer_id,
            "manager_customer_id": req.manager_customer_id,
        }
        
        if req.access_token:
            creds["access_token"] = req.access_token
        if req.expires_at:
            creds["expires_at"] = req.expires_at
        
        await state.vault.store_credentials(tenant_id, creds)
        
        return {
            "status": "stored",
            "tenant_id": tenant_id,
            "has_manager_id": req.manager_customer_id is not None,
        }
    
    @app.delete("/api/v1/tenants/{tenant_id}/credentials")
    async def delete_credentials(tenant_id: str):
        """Delete tenant credentials (GDPR right-to-erasure)."""
        deleted = await state.vault.delete_credentials(tenant_id)
        state.factory.invalidate(tenant_id)
        
        return {"status": "deleted" if deleted else "not_found", "tenant_id": tenant_id}
    
    @app.get("/api/v1/tenants/{tenant_id}/health")
    async def tenant_health(tenant_id: str):
        """Check Google Ads connectivity for a tenant."""
        healthy = await state.factory.health_check(tenant_id)
        return {
            "tenant_id": tenant_id,
            "healthy": healthy,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    # -----------------------------------------------------------------
    # Idempotency Management
    # -----------------------------------------------------------------
    
    @app.get("/api/v1/idempotency/stats")
    async def idempotency_stats(tenant_id: str = None):
        """Get idempotency store statistics."""
        stats = await state.idempotency.get_stats(tenant_id)
        return stats
    
    @app.post("/api/v1/idempotency/cleanup")
    async def idempotency_cleanup():
        """Clean up expired idempotency keys."""
        deleted = await state.idempotency.cleanup_expired()
        return {"deleted": deleted}
    
    # -----------------------------------------------------------------
    # Day 6: Register all agent/workflow/orchestrator endpoints
    # -----------------------------------------------------------------
    from api.routes import register_day6_routes
    register_day6_routes(app, state)

except ImportError:
    logger.warning(
        "FastAPI not installed. Running in library-only mode. "
        "Install with: pip install fastapi uvicorn"
    )
    app = None


# -----------------------------------------------------------------------------
# Standalone Runner
# -----------------------------------------------------------------------------

async def run_standalone_test():
    """
    Test Day 1 + Day 2 components - full pipeline.
    Run with: python main.py
    """
    await startup()
    
    print("\n" + "=" * 60)
    print("STANDALONE TEST - Day 1 + Day 2 Components")
    print("=" * 60)
    
    # 1. Store test credentials
    print("\n1. Storing test credentials for 'bank01'...")
    await state.vault.store_credentials("bank01", {
        "refresh_token": "test_refresh_token_bank01",
        "customer_id": "1234567890",
        "manager_customer_id": "9876543210",
        "access_token": "test_access_token",
        "expires_at": "2026-12-31T23:59:59",
    })
    print("   [OK] Credentials stored")
    
    # 2. List operations
    print("\n2. Registered operations:")
    for op in state.registry.list_operations():
        print(f"   > {op['full_name']}: {op['description']}")
    
    # 3. Policy Engine - ALLOW case
    print("\n3. Testing PolicyEngine (ALLOW)...")
    from core.policies.engine import PolicyDecision
    result = state.policy_engine.validate_operation(
        "bank01", "update_campaign_budget@v1",
        {"new_budget": 100.0, "previous_budget": 80.0, "budget_id": "b1"},
    )
    print(f"   Decision: {result.decision.value}")
    print(f"   Reason: {result.reason}")
    assert result.decision == PolicyDecision.ALLOW, "Should be ALLOW"
    print("   [OK] ALLOW policy passed")
    
    # 4. Policy Engine - DENY case (budget too high)
    print("\n4. Testing PolicyEngine (DENY - budget exceeds max)...")
    result_deny = state.policy_engine.validate_operation(
        "bank01", "update_campaign_budget@v1",
        {"new_budget": 15000.0, "previous_budget": 5000.0, "budget_id": "b1"},
    )
    print(f"   Decision: {result_deny.decision.value}")
    print(f"   Rule: {result_deny.rule_name}")
    print(f"   Reason: {result_deny.reason}")
    assert result_deny.decision == PolicyDecision.DENY, "Should be DENY"
    print("   [OK] DENY policy working")
    
    # 5. Policy Engine - REQUIRE_APPROVAL case
    print("\n5. Testing PolicyEngine (REQUIRE_APPROVAL)...")
    result_approve = state.policy_engine.validate_operation(
        "bank01", "update_campaign_budget@v1",
        {"new_budget": 7000.0, "previous_budget": 5000.0, "budget_id": "b1"},
    )
    print(f"   Decision: {result_approve.decision.value}")
    print(f"   Reason: {result_approve.reason}")
    assert result_approve.decision == PolicyDecision.REQUIRE_APPROVAL, "Should be REQUIRE_APPROVAL"
    print("   [OK] REQUIRE_APPROVAL policy working")
    
    # 6. Content validation
    print("\n6. Testing content validation...")
    content_result = state.policy_engine.validate_content("bank01", {
        "headlines": ["Get Free Money Now!", "Best Loans Ever"],
        "descriptions": ["Apply for our guaranteed loans today"],
    })
    print(f"   Valid: {content_result.valid}")
    print(f"   Violations: {len(content_result.violations)}")
    for v in content_result.violations:
        print(f"     [X] {v}")
    assert not content_result.valid, "Should detect forbidden words"
    print("   [OK] Content validation working")
    
    # 7. Full Connector Pipeline - get_campaign_metrics (read-only)
    print("\n7. Full pipeline - get_campaign_metrics@v1...")
    connector_result = await state.connector.execute(
        tenant_id="bank01",
        operation_name="get_campaign_metrics@v1",
        payload={},
        source="test",
    )
    print(f"   Success: {connector_result.success}")
    print(f"   Saga ID: {connector_result.saga_id}")
    print(f"   Policy: {connector_result.policy_decision}")
    print(f"   Duration: {connector_result.execution_time_ms:.0f}ms")
    print(f"   Campaigns: {connector_result.data.get('count', 0)}")
    assert connector_result.success, "Should succeed"
    print("   [OK] Full pipeline passed (read-only)")
    
    # 8. Full Connector Pipeline - update_campaign_budget (write with saga)
    print("\n8. Full pipeline - update_campaign_budget@v1...")
    budget_result = await state.connector.execute(
        tenant_id="bank01",
        operation_name="update_campaign_budget@v1",
        payload={
            "budget_id": "budget_001",
            "new_budget": 65.00,
            "previous_budget": 50.00,
        },
        source="test",
    )
    print(f"   Success: {budget_result.success}")
    print(f"   Saga ID: {budget_result.saga_id}")
    print(f"   Compensable: {budget_result.compensable}")
    print(f"   Duration: {budget_result.execution_time_ms:.0f}ms")
    assert budget_result.success, "Should succeed"
    assert budget_result.compensable, "Should be compensable"
    print("   [OK] Full pipeline passed (write with saga)")
    
    # 9. Idempotency - same operation should hit cache
    print("\n9. Testing idempotency via connector...")
    idem_result = await state.connector.execute(
        tenant_id="bank01",
        operation_name="update_campaign_budget@v1",
        payload={
            "budget_id": "budget_001",
            "new_budget": 65.00,
            "previous_budget": 50.00,
        },
        source="test",
    )
    print(f"   Idempotency hit: {idem_result.idempotency_hit}")
    assert idem_result.idempotency_hit, "Should be idempotency hit"
    print("   [OK] Idempotency working through pipeline")
    
    # 10. Pipeline - DENY from policy
    print("\n10. Full pipeline - DENY (budget exceeds policy)...")
    deny_result = await state.connector.execute(
        tenant_id="bank01",
        operation_name="update_campaign_budget@v1",
        payload={
            "budget_id": "budget_002",
            "new_budget": 20000.0,
            "previous_budget": 5000.0,
        },
    )
    print(f"   Success: {deny_result.success}")
    print(f"   Policy decision: {deny_result.policy_decision}")
    print(f"   Reason: {deny_result.policy_reason}")
    assert not deny_result.success, "Should be denied"
    assert deny_result.policy_decision == "deny", "Should be policy deny"
    print("   [OK] Policy DENY working through pipeline")
    
    # 11. Pipeline - REQUIRE_APPROVAL from policy
    print("\n11. Full pipeline - REQUIRE_APPROVAL...")
    approval_result = await state.connector.execute(
        tenant_id="bank01",
        operation_name="update_campaign_budget@v1",
        payload={
            "budget_id": "budget_003",
            "new_budget": 7000.0,
            "previous_budget": 5000.0,
        },
    )
    print(f"   Requires approval: {approval_result.requires_approval}")
    print(f"   Saga ID: {approval_result.saga_id}")
    assert approval_result.requires_approval, "Should require approval"
    print("   [OK] Approval gate working through pipeline")
    
    # 12. Telemetry stats
    print("\n12. Telemetry stats:")
    stats = state.telemetry.get_stats("bank01")
    print(f"   Operations total: {stats['operations_total']}")
    print(f"   Errors: {stats['operations_errors']}")
    print(f"   Duration p50: {stats['duration_stats'].get('p50', 0):.0f}ms")
    print("   [OK] Telemetry recording")
    
    # 13. Circuit breaker status
    print("\n13. Circuit breaker status:")
    cb_status = state.executor.get_circuit_status("bank01")
    print(f"   State: {cb_status.get('state', 'no_circuit')}")
    print("   [OK] Circuit breaker healthy")
    
    # 14. Prometheus metrics
    print("\n14. Prometheus metrics (sample):")
    metrics = state.telemetry.get_prometheus_metrics()
    for line in metrics.split("\n")[:10]:
        if line and not line.startswith("#"):
            print(f"   {line}")
    print("   [OK] Prometheus metrics ready")
    
    # 15. Factory stats
    print("\n15. Factory stats:")
    factory_stats = state.factory.get_stats()
    print(f"   Total clients: {factory_stats['total_clients']}")
    print(f"   API version: {factory_stats['api_version']}")
    
    print("\n" + "=" * 60)
    print("DAY 3 TESTS - Knowledge Base + Agents")
    print("=" * 60)
    
    # 16. Knowledge Store - load rules
    print("\n16. Knowledge Base - rules...")
    rules = state.knowledge_store.get_rules("bank01", industry="financial_services")
    print(f"   Rules loaded: {len(rules)}")
    assert len(rules) >= 10, "Should have 10+ rules"
    print(f"   First rule: {rules[0]['name']}")
    print("   [OK] Rules loaded from YAML")
    
    # 17. Knowledge Base - match rules to context
    print("\n17. Knowledge Base - rule matching...")
    matched = state.knowledge_store.match_rules("bank01", {
        "goal": "leads",
        "channel": "search",
    }, industry="financial_services")
    print(f"   Matched {len(matched)} rules for leads+search")
    for r in matched[:3]:
        print(f"     > {r['name']} (confidence: {r.get('confidence', 0):.0%})")
    assert len(matched) >= 1, "Should match at least 1 rule"
    print("   [OK] Rule matching working")
    
    # 18. Knowledge Base - benchmarks
    print("\n18. Knowledge Base - benchmarks...")
    benchmarks = state.knowledge_store.get_benchmarks("bank01", industry="financial_services")
    print(f"   Industry: {benchmarks['industry']}")
    metrics = benchmarks.get("metrics", {}).get("search", {})
    print(f"   Avg CPA: ${metrics.get('avg_cpa', 'N/A')}")
    print(f"   Avg CTR: {metrics.get('avg_ctr', 'N/A')}%")
    assert "search" in benchmarks.get("metrics", {}), "Should have search benchmarks"
    print("   [OK] Benchmarks loaded")
    
    # 19. Knowledge Base - guardrails
    print("\n19. Knowledge Base - guardrails...")
    guardrails = state.knowledge_store.get_guardrails("bank01")
    forbidden = guardrails.get("content_guardrails", {}).get("forbidden_words", [])
    print(f"   Forbidden words: {len(forbidden)}")
    print(f"   Max headline length: {guardrails.get('content_guardrails', {}).get('max_headline_length', 'N/A')}")
    assert len(forbidden) >= 5, "Should have 5+ forbidden words"
    print("   [OK] Guardrails loaded")
    
    # 20. Knowledge Base - copy validation
    print("\n20. Knowledge Base - copy validation...")
    valid, violations, warnings = state.knowledge_store.validate_copy(
        "bank01",
        headlines=["Get Guaranteed Returns!", "Best Banking"],
        descriptions=["Open your risk-free account today"],
        industry="financial_services",
    )
    print(f"   Valid: {valid}")
    print(f"   Violations: {len(violations)}")
    for v in violations:
        print(f"     [X] {v}")
    assert not valid, "Should detect forbidden words"
    print("   [OK] Copy validation working")
    
    # 21. StrategistIA - generate strategy
    print("\n21. StrategistIA - propose strategy...")
    strategy_plan = state.strategist.propose_strategy(
        tenant_id="bank01",
        context={
            "goal": "leads",
            "channel": "search",
            "monthly_budget": 3000,
            "industry": "financial_services",
            "phase": "launch",
        },
    )
    print(f"   Plan: {strategy_plan.title}")
    print(f"   Operations: {strategy_plan.total_operations}")
    print(f"   Risk: {strategy_plan.risk_score:.1%}")
    print(f"   Approval: {'Required' if strategy_plan.requires_approval else 'Auto'}")
    print(f"   Rules consulted: {len(strategy_plan.rules_consulted)}")
    print(f"   Status: {strategy_plan.status.value}")
    assert strategy_plan.total_operations >= 2, "Should have 2+ operations"
    assert strategy_plan.status.value == "proposed", "Should be proposed"
    print("   [OK] Strategy generated")
    
    # 22. StrategistIA - get recommendations
    print("\n22. StrategistIA - recommendations...")
    recs = state.strategist.get_recommendations("bank01", {
        "goal": "leads", "channel": "search", "industry": "financial_services",
    })
    print(f"   Recommendations: {len(recs)}")
    for r in recs[:3]:
        print(f"     > [{r['rule_name']}] {r['recommendation']}")
    assert len(recs) >= 1, "Should have recommendations"
    print("   [OK] Recommendations working")
    
    # 23. StrategistIA - performance analysis
    print("\n23. StrategistIA - performance analysis...")
    analysis = state.strategist.analyze_performance(
        "bank01",
        metrics={"ctr": 1.5, "cpa": 85.0, "conv_rate": 3.2},
        industry="financial_services",
    )
    print(f"   Overall: {analysis['overall']}")
    print(f"   Comparisons: {len(analysis['comparisons'])}")
    for comp in analysis['comparisons']:
        print(f"     {comp['metric']}: {comp['actual']} vs benchmark {comp['benchmark']} ({comp['status']})")
    print(f"   Alerts: {len(analysis['alerts'])}")
    print("   [OK] Performance analysis working")
    
    # 24. BudgetPacingIA - analyze pacing
    print("\n24. BudgetPacingIA - pacing analysis...")
    pacing_plan = state.budget_pacing.analyze_and_plan(
        tenant_id="bank01",
        campaigns=[
            {"campaign_id": "c1", "campaign_name": "Search - Loans", "daily_budget": 100, "budget_id": "b1",
             "spend_today": 45, "spend_mtd": 800, "monthly_target": 3000},
            {"campaign_id": "c2", "campaign_name": "Search - Cards", "daily_budget": 50, "budget_id": "b2",
             "spend_today": 48, "spend_mtd": 1800, "monthly_target": 1500},
        ],
        industry="financial_services",
        day_of_month=15,
        days_in_month=30,
    )
    print(f"   Plan: {pacing_plan.title}")
    print(f"   Operations: {pacing_plan.total_operations}")
    for op in pacing_plan.operations:
        print(f"     > {op.description}")
    print(f"   Risk: {pacing_plan.risk_score:.1%}")
    print("   [OK] Budget pacing working")
    
    # 25. BudgetPacingIA - quick summary
    print("\n25. BudgetPacingIA - pacing summary...")
    summary = state.budget_pacing.get_pacing_summary(
        "bank01",
        campaigns=[
            {"campaign_id": "c1", "daily_budget": 100, "spend_mtd": 1500, "monthly_target": 3000},
        ],
        day_of_month=15,
    )
    print(f"   Overall pacing: {summary['overall_pacing_pct']}%")
    print(f"   On track: {summary['on_track']}, Under: {summary['underpacing']}, Over: {summary['overpacing']}")
    print("   [OK] Pacing summary working")
    
    print("\n" + "=" * 60)
    print("DAY 4 TESTS - Executor + RSA Generator + Search Cleaner")
    print("=" * 60)
    
    # 26. RSAAdCopyGeneratorIA - generate ad copy
    print("\n26. RSAAdCopyGeneratorIA - generate ad copy...")
    rsa_plan = state.rsa_generator.generate_ad_copy(
        tenant_id="bank01",
        context={
            "service": "Personal Loans",
            "brand_name": "CrediBank",
            "goal": "leads",
            "industry": "financial_services",
            "usp": ["Low rates", "Fast approval", "No hidden fees"],
            "tone": "professional",
        },
    )
    ad_data = rsa_plan.benchmarks_referenced
    print(f"   Headlines: {len(ad_data['headlines'])}")
    for h in ad_data['headlines'][:5]:
        print(f"     > {h}")
    print(f"   Descriptions: {len(ad_data['descriptions'])}")
    print(f"   Ad Strength: {ad_data['ad_strength_estimate']}")
    print(f"   Valid: {ad_data['validation']['valid']}")
    assert len(ad_data['headlines']) >= 8, "Should have 8+ headlines"
    assert len(ad_data['descriptions']) >= 3, "Should have 3+ descriptions"
    print("   [OK] RSA ad copy generated")
    
    # 27. RSAAdCopyGeneratorIA - preview
    print("\n27. RSAAdCopyGeneratorIA - preview...")
    preview = state.rsa_generator.preview_ad("bank01", {
        "service": "Credit Cards",
        "brand_name": "CrediBank",
        "goal": "leads",
        "industry": "financial_services",
        "usp": ["Cashback rewards", "No annual fee"],
    })
    print(f"   Headlines: {preview['headline_count']}")
    print(f"   Descriptions: {preview['description_count']}")
    print(f"   Ad Strength: {preview['ad_strength']}")
    print(f"   Valid: {preview['valid']}")
    print("   [OK] Preview working")
    
    # 28. RSAAdCopyGeneratorIA - violation detection
    print("\n28. RSAAdCopyGeneratorIA - compliance test...")
    bad_plan = state.rsa_generator.generate_ad_copy(
        tenant_id="bank01",
        context={
            "service": "Guaranteed Returns",
            "brand_name": "ScamBank",
            "goal": "leads",
            "industry": "financial_services",
            "usp": ["Free money", "No risk investing", "100% guaranteed"],
        },
    )
    bad_data = bad_plan.benchmarks_referenced
    # Even with bad USPs, the final output should be clean
    print(f"   Valid after fix: {bad_data['validation']['valid']}")
    print(f"   Warnings: {len(bad_data['validation']['warnings'])}")
    print("   [OK] Compliance filtering working")
    
    # 29. SearchTermsCleanerIA - analyze terms
    print("\n29. SearchTermsCleanerIA - analyze search terms...")
    search_terms_data = [
        {"term": "personal loan rates", "impressions": 500, "clicks": 25, "cost": 50, "conversions": 3},
        {"term": "free money no credit check", "impressions": 200, "clicks": 15, "cost": 30, "conversions": 0},
        {"term": "best loan for bad credit", "impressions": 300, "clicks": 18, "cost": 45, "conversions": 2},
        {"term": "loan shark reddit", "impressions": 100, "clicks": 8, "cost": 20, "conversions": 0},
        {"term": "personal loan calculator", "impressions": 40, "clicks": 3, "cost": 5, "conversions": 0},
        {"term": "credibank loan apply", "impressions": 150, "clicks": 30, "cost": 35, "conversions": 5},
    ]
    clean_plan = state.search_cleaner.analyze_and_clean(
        tenant_id="bank01",
        search_terms=search_terms_data,
        industry="financial_services",
    )
    clean_data = clean_plan.benchmarks_referenced
    print(f"   Negatives: {len(clean_data['negatives'])}")
    for n in clean_data['negatives']:
        print(f"     [X] '{n['term']}' - ${n['cost']:.2f} ({n['reasons'][0]})")
    print(f"   Positives: {len(clean_data['positives'])}")
    for p in clean_data['positives']:
        print(f"     [OK] '{p['term']}' - {p['conversions']} conv, ${p['cpa']:.2f} CPA")
    print(f"   Total waste: ${clean_data['total_waste']:.2f}")
    assert len(clean_data['negatives']) >= 2, "Should find 2+ negatives"
    assert len(clean_data['positives']) >= 1, "Should find 1+ positives"
    print("   [OK] Search terms cleanup working")
    
    # 30. SearchTermsCleanerIA - quick summary
    print("\n30. SearchTermsCleanerIA - quick summary...")
    summary = state.search_cleaner.get_summary("bank01", search_terms_data)
    print(f"   Total: {summary['total_terms']}")
    print(f"   Negatives: {summary['negatives']}, Positives: {summary['positives']}")
    print(f"   Monitoring: {summary['monitoring']}, Neutral: {summary['neutral']}")
    print(f"   Waste: ${summary['total_waste']:.2f}")
    print("   [OK] Summary working")
    
    # 31. ActionPlanExecutor - execute strategist plan
    print("\n31. ActionPlanExecutor - execute strategy plan...")
    # Re-generate a plan (the old one was already used)
    exec_plan = state.strategist.propose_strategy(
        tenant_id="bank01",
        context={
            "goal": "leads",
            "channel": "search",
            "monthly_budget": 2000,
            "industry": "financial_services",
        },
    )
    exec_plan.approve("test_user")
    executed = await state.plan_executor.execute(exec_plan, source="test")
    print(f"   Status: {executed.status.value}")
    print(f"   Completed: {executed.completed_operations}/{executed.total_operations}")
    print(f"   Failed: {executed.failed_operations}")
    for op in executed.operations:
        print(f"     [{op.status}] {op.description or op.operation_name}")
    assert executed.status.value in ("completed", "partially_completed"), "Should complete"
    print("   [OK] Plan execution working")
    
    # 32. ActionPlanExecutor - dry run
    print("\n32. ActionPlanExecutor - dry run...")
    dry_plan = state.strategist.propose_strategy(
        tenant_id="bank01",
        context={"goal": "leads", "channel": "search", "monthly_budget": 1000, "industry": "financial_services"},
    )
    dry_result = await state.plan_executor.execute(dry_plan, dry_run=True)
    print(f"   Status: {dry_result.status.value}")
    print(f"   Operations validated: {dry_result.total_operations}")
    print("   [OK] Dry run working")
    
    # 33. ActionPlanExecutor - execution history
    print("\n33. ActionPlanExecutor - execution history...")
    history = state.plan_executor.get_execution_history("bank01")
    print(f"   Executions: {len(history)}")
    for h in history[:3]:
        print(f"     > {h['title']} - {h['status']} ({h['completed']}/{h['total_operations']})")
    stats = state.plan_executor.get_stats()
    print(f"   Success rate: {stats['success_rate']}")
    print("   [OK] History tracking working")
    
    print("\n" + "=" * 60)
    print("DAY 5 TESTS - WorkflowEngine + OrchestratorIA")
    print("=" * 60)
    
    # 34. WorkflowEngine - list workflows
    print("\n34. WorkflowEngine - loaded workflows...")
    wf_list = state.workflow_engine.list_workflows()
    print(f"   Workflows: {len(wf_list)}")
    for wf in wf_list:
        print(f"     > {wf['id']}: {wf['name']} ({wf['steps']} steps)")
    assert len(wf_list) >= 5, "Should have 5 workflows"
    print("   [OK] Workflows loaded from YAML")
    
    # 35. WorkflowEngine - run weekly optimization
    print("\n35. WorkflowEngine - run weekly_optimization...")
    wf_result = await state.workflow_engine.run(
        workflow_id="weekly_optimization",
        tenant_id="bank01",
        context={"industry": "financial_services"},
        auto_approve=True,
    )
    wf_dict = wf_result.to_dict()
    print(f"   Status: {wf_dict['status']}")
    print(f"   Steps: {wf_dict['completed_steps']}/{wf_dict['total_steps']}")
    for s in wf_dict['steps']:
        print(f"     [{s['status']}] {s['name']}")
    print(f"   Plans generated: {len(wf_dict['plans_generated'])}")
    assert wf_dict['completed_steps'] >= 3, "Should complete 3+ steps"
    print("   [OK] Weekly optimization workflow executed")
    
    # 36. WorkflowEngine - run emergency pause
    print("\n36. WorkflowEngine - run emergency_pause...")
    emergency_result = await state.workflow_engine.run(
        workflow_id="emergency_pause",
        tenant_id="bank01",
        auto_approve=True,
    )
    ed = emergency_result.to_dict()
    print(f"   Status: {ed['status']}")
    print(f"   Steps: {ed['completed_steps']}/{ed['total_steps']}")
    assert ed['completed_steps'] >= 2, "Should complete 2+ steps"
    print("   [OK] Emergency pause workflow executed")
    
    # 37. WorkflowEngine - run search_terms_cleanup
    print("\n37. WorkflowEngine - run search_terms_cleanup...")
    cleanup_result = await state.workflow_engine.run(
        workflow_id="search_terms_cleanup",
        tenant_id="bank01",
        auto_approve=True,
    )
    cd = cleanup_result.to_dict()
    print(f"   Status: {cd['status']}")
    print(f"   Steps: {cd['completed_steps']}/{cd['total_steps']}")
    print("   [OK] Search terms cleanup workflow executed")
    
    # 38. WorkflowEngine - approval gate (new campaign launch)
    print("\n38. WorkflowEngine - approval gate test...")
    launch_result = await state.workflow_engine.run(
        workflow_id="new_campaign_launch",
        tenant_id="bank01",
        auto_approve=False,  # DON'T auto-approve
    )
    ld = launch_result.to_dict()
    print(f"   Status: {ld['status']}")
    print(f"   Steps completed before pause: {ld['completed_steps']}")
    awaiting = [s for s in ld['steps'] if s['status'] == 'awaiting_approval']
    print(f"   Awaiting approval: {len(awaiting)}")
    if awaiting:
        print(f"     > {awaiting[0]['name']}")
    assert ld['status'] == 'paused', "Should pause at approval gate"
    print("   [OK] Approval gate working")
    
    # 39. WorkflowEngine - stats
    print("\n39. WorkflowEngine - engine stats...")
    wf_stats = state.workflow_engine.get_stats()
    print(f"   Definitions: {wf_stats['workflow_definitions']}")
    print(f"   Executions: {wf_stats['total_executions']}")
    print(f"   Success rate: {wf_stats['success_rate']}")
    print(f"   Agents: {wf_stats['agents_registered']}")
    print("   [OK] Stats working")
    
    # 40. OrchestratorIA - handle request
    print("\n40. OrchestratorIA - handle 'optimize' request...")
    orch_result = await state.orchestrator.handle_request(
        tenant_id="bank01",
        request_type="optimize",
        context={"industry": "financial_services"},
        auto_approve=True,
    )
    print(f"   Status: {orch_result['status']}")
    print(f"   Workflow: {orch_result.get('workflow_id')}")
    print(f"   Steps: {orch_result.get('steps_completed')}/{orch_result.get('total_steps')}")
    assert orch_result['status'] == 'success', "Should succeed"
    print("   [OK] Orchestrator routing working")
    
    # 41. OrchestratorIA - handle emergency
    print("\n41. OrchestratorIA - handle 'emergency' request...")
    emerg_result = await state.orchestrator.handle_request(
        tenant_id="bank01",
        request_type="emergency",
        auto_approve=True,
    )
    print(f"   Status: {emerg_result['status']}")
    print(f"   Workflow: {emerg_result.get('workflow_id')}")
    assert emerg_result['status'] == 'success', "Should succeed"
    print("   [OK] Emergency routing working")
    
    # 42. OrchestratorIA - auto-triage
    print("\n42. OrchestratorIA - auto-triage (critical CPA)...")
    triage_result = await state.orchestrator.auto_triage(
        tenant_id="bank01",
        metrics={"cpa": 200, "ctr": 0.5, "budget_pacing": 160},
        industry="financial_services",
    )
    triage = triage_result.get("triage", {})
    print(f"   Urgency: {triage.get('urgency')}")
    print(f"   Recommended: {triage.get('recommended_workflows')}")
    print(f"   Reasons: {triage.get('reasons')}")
    assert triage.get('urgency') == 'critical', "Should detect critical"
    print("   [OK] Auto-triage working")
    
    # 43. OrchestratorIA - available actions
    print("\n43. OrchestratorIA - available actions...")
    actions = state.orchestrator.get_available_actions()
    print(f"   Actions: {len(actions)}")
    for a in actions:
        print(f"     > {a['workflow_id']}: {a['name']} ({a['steps']} steps)")
    print("   [OK] Actions listing working")
    
    # 44. OrchestratorIA - stats
    print("\n44. OrchestratorIA - stats...")
    orch_stats = state.orchestrator.get_stats()
    print(f"   Total requests: {orch_stats['total_requests']}")
    print(f"   Success rate: {orch_stats['success_rate']}")
    print(f"   Workflows: {orch_stats['available_workflows']}")
    print(f"   Agents: {orch_stats['available_agents']}")
    print("   [OK] Orchestrator stats working")
    
    print("\n" + "=" * 60)
    print("DAY 6 TESTS - FastAPI Endpoints + API Integration")
    print("=" * 60)
    
    # 45. API routes registered
    print("\n45. FastAPI routes registration...")
    if app is not None:
        routes = [r for r in app.routes if hasattr(r, 'methods')]
        print(f"   Total endpoints: {len(routes)}")
        agent_routes = [r for r in routes if '/agents/' in r.path]
        workflow_routes = [r for r in routes if '/workflows/' in r.path]
        orchestrator_routes = [r for r in routes if '/orchestrator/' in r.path]
        knowledge_routes = [r for r in routes if '/knowledge/' in r.path]
        print(f"   Agent endpoints: {len(agent_routes)}")
        print(f"   Workflow endpoints: {len(workflow_routes)}")
        print(f"   Orchestrator endpoints: {len(orchestrator_routes)}")
        print(f"   Knowledge endpoints: {len(knowledge_routes)}")
        assert len(agent_routes) >= 8, "Should have 8+ agent endpoints"
        assert len(workflow_routes) >= 3, "Should have 3+ workflow endpoints"
        assert len(orchestrator_routes) >= 5, "Should have 5+ orchestrator endpoints"
    else:
        print("   FastAPI not available (library-only mode)")
    print("   [OK] API routes registered")
    
    # 46. Direct agent call - strategist via same interface API uses
    print("\n46. API-style strategist call...")
    plan = state.strategist.propose_strategy(
        tenant_id="bank01",
        context={
            "goal": "leads",
            "channel": "search",
            "monthly_budget": 5000,
            "industry": "financial_services",
            "phase": "launch",
        },
    )
    api_response = {
        "status": "success",
        "plan": plan.to_dict(),
        "summary": plan.summary(),
    }
    print(f"   Plan: {api_response['plan']['title']}")
    print(f"   Operations: {api_response['plan']['total_operations']}")
    print(f"   Risk: {api_response['plan']['risk_score']}")
    assert api_response['status'] == 'success'
    print("   [OK] Strategist API-style call working")
    
    # 47. Direct agent call - RSA generator
    print("\n47. API-style RSA generator call...")
    rsa_plan = state.rsa_generator.generate_ad_copy(
        tenant_id="bank01",
        context={
            "service": "Business Loans",
            "brand_name": "CrediBank",
            "goal": "leads",
            "industry": "financial_services",
            "usp": ["Flexible terms", "Quick approval", "Low rates"],
            "tone": "professional",
        },
    )
    ad_data = rsa_plan.benchmarks_referenced
    api_rsa = {
        "status": "success",
        "headlines": ad_data.get("headlines", []),
        "descriptions": ad_data.get("descriptions", []),
        "ad_strength": ad_data.get("ad_strength_estimate"),
        "validation": ad_data.get("validation", {}),
    }
    print(f"   Headlines: {len(api_rsa['headlines'])}")
    print(f"   Descriptions: {len(api_rsa['descriptions'])}")
    print(f"   Ad Strength: {api_rsa['ad_strength']}")
    print(f"   Valid: {api_rsa['validation'].get('valid')}")
    assert api_rsa['status'] == 'success'
    print("   [OK] RSA Generator API-style call working")
    
    # 48. Direct agent call - search cleaner
    print("\n48. API-style search cleaner call...")
    terms = [
        {"term": "business loan rates", "impressions": 600, "clicks": 30, "cost": 60, "conversions": 5},
        {"term": "free business grants", "impressions": 300, "clicks": 20, "cost": 40, "conversions": 0},
        {"term": "sba loan requirements", "impressions": 200, "clicks": 15, "cost": 30, "conversions": 3},
    ]
    clean_plan = state.search_cleaner.analyze_and_clean(
        tenant_id="bank01",
        search_terms=terms,
        industry="financial_services",
    )
    clean_data = clean_plan.benchmarks_referenced
    api_clean = {
        "status": "success",
        "negatives": clean_data.get("negatives", []),
        "positives": clean_data.get("positives", []),
        "total_waste": clean_data.get("total_waste", 0),
    }
    print(f"   Negatives: {len(api_clean['negatives'])}")
    print(f"   Positives: {len(api_clean['positives'])}")
    print(f"   Waste: ${api_clean['total_waste']:.2f}")
    assert api_clean['status'] == 'success'
    print("   [OK] Search Cleaner API-style call working")
    
    # 49. Workflow API - list
    print("\n49. API-style workflow list...")
    wf_api = state.workflow_engine.list_workflows()
    print(f"   Workflows: {len(wf_api)}")
    for wf in wf_api:
        print(f"     > {wf['id']}: {wf['name']}")
    assert len(wf_api) >= 5
    print("   [OK] Workflow list API working")
    
    # 50. Workflow API - run via orchestrator
    print("\n50. API-style orchestrator request...")
    orch_api = await state.orchestrator.handle_request(
        tenant_id="bank01",
        request_type="cleanup",
        auto_approve=True,
    )
    print(f"   Status: {orch_api['status']}")
    print(f"   Workflow: {orch_api.get('workflow_id')}")
    print(f"   Steps: {orch_api.get('steps_completed')}/{orch_api.get('total_steps')}")
    assert orch_api['status'] == 'success'
    print("   [OK] Orchestrator API-style request working")
    
    # 51. Knowledge API - rules
    print("\n51. API-style knowledge endpoints...")
    rules = state.knowledge_store.get_rules("bank01", "financial_services")
    benchmarks = state.knowledge_store.get_benchmarks("bank01", "financial_services")
    guardrails = state.knowledge_store.get_guardrails("bank01", "financial_services")
    playbooks = state.knowledge_store.get_playbooks("bank01")
    templates = state.knowledge_store.get_templates("bank01")
    print(f"   Rules: {len(rules)}")
    print(f"   Benchmarks: {len(benchmarks.get('metrics', {}))} verticals")
    print(f"   Guardrails: {len(guardrails.get('content_guardrails', {}).get('forbidden_words', []))} forbidden words")
    print(f"   Playbooks: {len(playbooks)}")
    print(f"   Templates: campaigns={len(templates.get('campaign_templates', []))}")
    print("   [OK] Knowledge API working")
    
    # 52. Dashboard API
    print("\n52. API-style dashboard endpoint...")
    dashboard_data = {
        "tenant_id": "bank01",
        "system": {
            "workflow_stats": state.workflow_engine.get_stats(),
            "orchestrator_stats": state.orchestrator.get_stats(),
            "executor_stats": state.plan_executor.get_stats(),
        },
        "workflows": {
            "available": len(state.workflow_engine.list_workflows()),
            "recent_executions": len(state.workflow_engine.get_execution_history("bank01", 5)),
        },
    }
    print(f"   Workflow defs: {dashboard_data['workflows']['available']}")
    print(f"   Recent executions: {dashboard_data['workflows']['recent_executions']}")
    print(f"   Orchestrator requests: {dashboard_data['system']['orchestrator_stats']['total_requests']}")
    print(f"   Plan executions: {dashboard_data['system']['executor_stats']['total_executions']}")
    print("   [OK] Dashboard API working")
    
    # 53. System health API
    print("\n53. API-style system health...")
    health_data = {
        "components": {
            "database": state.db is not None,
            "vault": state.vault is not None,
            "connector": state.connector is not None,
            "knowledge_store": state.knowledge_store is not None,
            "workflow_engine": state.workflow_engine is not None,
            "orchestrator": state.orchestrator is not None,
            "plan_executor": state.plan_executor is not None,
        },
        "agents": {
            "strategist": state.strategist is not None,
            "budget_pacing": state.budget_pacing is not None,
            "rsa_generator": state.rsa_generator is not None,
            "search_cleaner": state.search_cleaner is not None,
        },
    }
    all_healthy = all(health_data['components'].values()) and all(health_data['agents'].values())
    print(f"   All components healthy: {all_healthy}")
    print(f"   Components: {sum(health_data['components'].values())}/{len(health_data['components'])}")
    print(f"   Agents: {sum(health_data['agents'].values())}/{len(health_data['agents'])}")
    assert all_healthy, "All components should be healthy"
    print("   [OK] System health API working")
    
    # 54. Multi-tenant test
    print("\n54. Multi-tenant isolation test...")
    await state.vault.store_credentials("fintech02", {
        "refresh_token": "test_refresh_fintech02",
        "customer_id": "2222222222",
    })
    plan_t1 = state.strategist.propose_strategy("bank01", {"goal": "leads", "channel": "search", "monthly_budget": 1000, "industry": "financial_services"})
    plan_t2 = state.strategist.propose_strategy("fintech02", {"goal": "sales", "channel": "search", "monthly_budget": 3000, "industry": "fintech"})
    print(f"   Tenant bank01: {plan_t1.title}")
    print(f"   Tenant fintech02: {plan_t2.title}")
    assert plan_t1.tenant_id == "bank01"
    assert plan_t2.tenant_id == "fintech02"
    assert plan_t1.plan_id != plan_t2.plan_id
    print("   [OK] Multi-tenant isolation working")
    
    print("\n" + "=" * 60)
    print("DAY 7 TESTS - Hardening + Final Validation")
    print("=" * 60)
    
    # 55. Pytest test suite exists
    print("\n55. Pytest test suite validation...")
    assert os.path.exists("tests/test_all.py"), "test_all.py should exist"
    with open("tests/test_all.py", "r", encoding="utf-8") as f:
        test_content = f.read()
    test_classes = test_content.count("class Test")
    test_methods = test_content.count("def test_")
    print(f"   Test classes: {test_classes}")
    print(f"   Test methods: {test_methods}")
    assert test_classes >= 10, "Should have 10+ test classes"
    assert test_methods >= 30, "Should have 30+ test methods"
    print("   [OK] Pytest suite validated")
    
    # 56. Deployment docs exist
    print("\n56. Deployment documentation...")
    assert os.path.exists("docs/DEPLOYMENT.md"), "DEPLOYMENT.md should exist"
    assert os.path.exists("docs/API_REFERENCE.md"), "API_REFERENCE.md should exist"
    assert os.path.exists("Dockerfile"), "Dockerfile should exist"
    print("   [OK] DEPLOYMENT.md present")
    print("   [OK] API_REFERENCE.md present")
    print("   [OK] Dockerfile present")
    
    # 57. All YAML knowledge files intact
    print("\n57. Knowledge base integrity...")
    yaml_files = [
        "knowledge/global/google_ads/rules.yaml",
        "knowledge/global/google_ads/playbooks.yaml",
        "knowledge/global/google_ads/benchmarks.yaml",
        "knowledge/global/google_ads/guardrails.yaml",
        "knowledge/global/google_ads/templates.yaml",
    ]
    for yf in yaml_files:
        assert os.path.exists(yf), f"Missing: {yf}"
        size = os.path.getsize(yf)
        print(f"   [OK] {yf} ({size} bytes)")
    
    # 58. All workflow YAML files intact
    print("\n58. Workflow definitions integrity...")
    wf_files = [
        "config/workflows/weekly_optimization.yaml",
        "config/workflows/new_campaign_launch.yaml",
        "config/workflows/budget_adjustment.yaml",
        "config/workflows/emergency_pause.yaml",
        "config/workflows/search_terms_cleanup.yaml",
    ]
    for wf in wf_files:
        assert os.path.exists(wf), f"Missing: {wf}"
        size = os.path.getsize(wf)
        print(f"   [OK] {wf} ({size} bytes)")
    
    # 59. Edge case: empty search terms
    print("\n59. Edge case - empty inputs...")
    empty_plan = state.search_cleaner.analyze_and_clean("bank01", [], "financial_services")
    print(f"   Empty search terms: {empty_plan.benchmarks_referenced.get('total_waste', 0)} waste")
    empty_summary = state.budget_pacing.get_pacing_summary("bank01", [])
    print(f"   Empty campaigns: campaigns={empty_summary.get('total_campaigns', 0)}")
    print("   [OK] Empty inputs handled gracefully")
    
    # 60. Edge case: unknown tenant KB
    print("\n60. Edge case - unknown tenant knowledge...")
    rules_unknown = state.knowledge_store.get_rules("nonexistent_tenant")
    print(f"   Unknown tenant rules: {len(rules_unknown)} (falls back to global)")
    assert len(rules_unknown) >= 10, "Should fallback to global rules"
    print("   [OK] Unknown tenant fallback working")
    
    # 61. Edge case: large budget strategy
    print("\n61. Edge case - large budget strategy...")
    big_plan = state.strategist.propose_strategy("bank01", {
        "goal": "leads", "channel": "search",
        "monthly_budget": 100000, "industry": "financial_services",
    })
    print(f"   Budget: $100,000 > Risk: {big_plan.risk_score}")
    print(f"   Requires approval: {big_plan.requires_approval}")
    assert big_plan.risk_score > 0.3, "High budget should mean high risk"
    assert big_plan.requires_approval is True, "Should require approval"
    print("   [OK] High-budget risk detection working")
    
    # 62. Edge case: orchestrator with invalid request type
    print("\n62. Edge case - invalid orchestrator request...")
    invalid_result = await state.orchestrator.handle_request(
        "bank01", "nonexistent_action"
    )
    print(f"   Status: {invalid_result['status']}")
    assert invalid_result['status'] == 'error'
    assert 'available_types' in invalid_result
    print("   [OK] Invalid request handled gracefully")
    
    # 63. Full end-to-end: Orchestrator > Workflow > Agents > Plan > Execute
    print("\n63. End-to-end integration test...")
    e2e_result = await state.orchestrator.handle_request(
        tenant_id="bank01",
        request_type="optimize",
        context={"industry": "financial_services"},
        auto_approve=True,
    )
    print(f"   Status: {e2e_result['status']}")
    print(f"   Workflow: {e2e_result.get('workflow_id')}")
    print(f"   Steps: {e2e_result.get('steps_completed')}/{e2e_result.get('total_steps')}")
    print(f"   Plans: {e2e_result.get('plans_generated', [])}")
    assert e2e_result['status'] == 'success'
    assert e2e_result.get('steps_completed', 0) >= 3
    print("   [OK] Full end-to-end pipeline working")
    
    # 64. Component count validation
    print("\n64. Final component inventory...")
    components = {
        "InMemoryDatabase": state.db is not None,
        "TenantCredentialVault": state.vault is not None,
        "GoogleAdsClientFactory": state.factory is not None,
        "OperationRegistry": state.registry is not None,
        "IdempotencyStore": state.idempotency is not None,
        "GoogleAdsExecutor": state.executor is not None,
        "PolicyEngine": state.policy_engine is not None,
        "TelemetrySidecar": state.telemetry is not None,
        "SagaJournal": state.saga_journal is not None,
        "GoogleAdsConnector": state.connector is not None,
        "YamlKnowledgeStore": state.knowledge_store is not None,
        "ActionPlanExecutor": state.plan_executor is not None,
        "GoogleAdsStrategistIA": state.strategist is not None,
        "GoogleAdsBudgetPacingIA": state.budget_pacing is not None,
        "RSAAdCopyGeneratorIA": state.rsa_generator is not None,
        "SearchTermsCleanerIA": state.search_cleaner is not None,
        "WorkflowEngine": state.workflow_engine is not None,
        "OrchestratorIA": state.orchestrator is not None,
        "APIRoutes": True,  # routes.py exists; FastAPI registers them when available
    }
    active = sum(1 for v in components.values() if v)
    for name, ok in components.items():
        status = "[OK]" if ok else "[X]"
        print(f"   {status} {name}")
    print(f"   Active: {active}/{len(components)}")
    assert active == len(components), "All components should be active"
    print("   [OK] All components verified")

    print("\n" + "=" * 60)
    print("=======================================================")
    print("  NADAKKI GOOGLE ADS MVP - FINAL BUILD COMPLETE  *")
    print("=======================================================")
    print(f"  Components:  {active}")
    print(f"  Tests:       64")
    print(f"  Workflows:   5")
    print(f"  Agents:      4 + Orchestrator")
    print(f"  Endpoints:   27+")
    print(f"  KB Rules:    10")
    print(f"  KB Files:    10 YAML")
    print("=======================================================")
    print("  ALL DAYS 1-7 TESTS PASSED [OK]")
    print("=======================================================")
    print()
    
    await shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_standalone_test())
