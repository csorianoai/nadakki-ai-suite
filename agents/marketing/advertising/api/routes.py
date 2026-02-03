# ===============================================================================
# NADAKKI AI Suite - API Routes (Day 6)
# api/routes.py
# Day 6 - Complete REST API for all agents, workflows, and orchestrator
# ===============================================================================

"""
REST API endpoints for NADAKKI Google Ads MVP.

Agent Endpoints:
    POST /api/v1/agents/strategist/propose      > Generate campaign strategy
    POST /api/v1/agents/strategist/analyze       > Analyze performance metrics
    POST /api/v1/agents/budget-pacing/analyze    > Analyze budget pacing
    POST /api/v1/agents/rsa-generator/generate   > Generate RSA ad copy
    POST /api/v1/agents/rsa-generator/preview    > Preview ad copy
    POST /api/v1/agents/search-cleaner/analyze   > Analyze search terms
    POST /api/v1/agents/search-cleaner/summary   > Quick summary

Workflow Endpoints:
    GET  /api/v1/workflows                       > List workflows
    GET  /api/v1/workflows/{id}                  > Get workflow details
    POST /api/v1/workflows/{id}/run              > Run a workflow
    GET  /api/v1/workflows/history               > Execution history

Orchestrator Endpoints:
    POST /api/v1/orchestrator/request            > Handle high-level request
    POST /api/v1/orchestrator/triage             > Auto-triage by metrics
    POST /api/v1/orchestrator/schedule           > Handle scheduled trigger
    GET  /api/v1/orchestrator/actions            > Available actions
    GET  /api/v1/orchestrator/stats              > Orchestrator stats

Plan Endpoints:
    GET  /api/v1/plans/history                   > Execution history
    GET  /api/v1/plans/stats                     > Executor stats

Dashboard Endpoint:
    GET  /api/v1/dashboard/{tenant_id}           > Full dashboard data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger("nadakki.api.routes")


def register_day6_routes(app, state):
    """Register all Day 6 API routes on the FastAPI app."""
    
    from fastapi import HTTPException
    from pydantic import BaseModel
    
    # -----------------------------------------------------------------
    # Request Models
    # -----------------------------------------------------------------
    
    class StrategyRequest(BaseModel):
        tenant_id: str
        context: Dict[str, Any]  # goal, channel, monthly_budget, industry, etc.
    
    class PerformanceAnalysisRequest(BaseModel):
        tenant_id: str = "default"
        metrics: Dict[str, float]  # ctr, cpa, conv_rate, quality_score
        industry: str = "financial_services"
    
    class BudgetPacingRequest(BaseModel):
        tenant_id: str
        campaigns: List[Dict[str, Any]]
        industry: str = "financial_services"
        day_of_month: Optional[int] = None
        days_in_month: Optional[int] = None
    
    class RSAGenerateRequest(BaseModel):
        tenant_id: str
        context: Dict[str, Any]  # service, brand_name, goal, industry, usp, tone
    
    class SearchCleanRequest(BaseModel):
        tenant_id: str
        search_terms: List[Dict[str, Any]]
        industry: str = "financial_services"
        custom_negatives: Optional[List[str]] = None
        target_cpa: Optional[float] = None
    
    class WorkflowRunRequest(BaseModel):
        tenant_id: str
        context: Optional[Dict[str, Any]] = None
        dry_run: bool = False
        auto_approve: bool = False
    
    class OrchestratorRequest(BaseModel):
        tenant_id: str
        request_type: str
        context: Optional[Dict[str, Any]] = None
        auto_approve: bool = False
    
    class TriageRequest(BaseModel):
        tenant_id: str
        metrics: Dict[str, float]  # cpa, ctr, budget_pacing
        industry: str = "financial_services"
    
    class ScheduleRequest(BaseModel):
        tenant_id: str
        trigger: str
        context: Optional[Dict[str, Any]] = None
    
    # ===================================================================
    # AGENT ENDPOINTS
    # ===================================================================
    
    # --- Strategist Agent ---------------------------------------------
    
    @app.post("/api/v1/agents/strategist/propose", tags=["Agents"])
    async def strategist_propose(req: StrategyRequest):
        """
        Generate a campaign strategy with ActionPlan.
        
        Required context fields: goal, channel, monthly_budget
        Optional: industry, phase, current_cpa, current_ctr, quality_score
        """
        try:
            plan = state.strategist.propose_strategy(
                tenant_id=req.tenant_id,
                context=req.context,
            )
            return {
                "status": "success",
                "plan": plan.to_dict(),
                "summary": plan.summary(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/agents/strategist/analyze", tags=["Agents"])
    async def strategist_analyze(req: PerformanceAnalysisRequest):
        """
        Analyze current performance metrics against benchmarks.
        
        Metrics: ctr, cpa, conv_rate, quality_score
        """
        try:
            analysis = state.strategist.analyze_performance(
                metrics=req.metrics,
                industry=req.industry,
            )
            return {
                "status": "success",
                "analysis": analysis,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/agents/strategist/recommendations", tags=["Agents"])
    async def strategist_recommendations(req: StrategyRequest):
        """Get recommendations based on context (without generating ActionPlan)."""
        try:
            recs = state.strategist.get_recommendations(
                tenant_id=req.tenant_id,
                context=req.context,
            )
            return {
                "status": "success",
                "recommendations": recs,
                "count": len(recs),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # --- Budget Pacing Agent ------------------------------------------
    
    @app.post("/api/v1/agents/budget-pacing/analyze", tags=["Agents"])
    async def budget_pacing_analyze(req: BudgetPacingRequest):
        """
        Analyze budget pacing for campaigns and generate ActionPlan.
        
        Each campaign needs: campaign_id, campaign_name, daily_budget,
        spend_today, spend_mtd, monthly_target
        """
        try:
            plan = state.budget_pacing.analyze_and_plan(
                tenant_id=req.tenant_id,
                campaigns=req.campaigns,
                industry=req.industry,
                day_of_month=req.day_of_month,
                days_in_month=req.days_in_month,
            )
            return {
                "status": "success",
                "plan": plan.to_dict(),
                "summary": plan.summary(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/agents/budget-pacing/summary", tags=["Agents"])
    async def budget_pacing_summary(req: BudgetPacingRequest):
        """Quick budget pacing summary for dashboard."""
        try:
            summary = state.budget_pacing.get_pacing_summary(
                tenant_id=req.tenant_id,
                campaigns=req.campaigns,
                day_of_month=req.day_of_month,
            )
            return {
                "status": "success",
                "summary": summary,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # --- RSA Ad Copy Generator ----------------------------------------
    
    @app.post("/api/v1/agents/rsa-generator/generate", tags=["Agents"])
    async def rsa_generate(req: RSAGenerateRequest):
        """
        Generate RSA ad copy with validation.
        
        Context: service, brand_name, goal, industry, usp (list), tone
        """
        try:
            plan = state.rsa_generator.generate_ad_copy(
                tenant_id=req.tenant_id,
                context=req.context,
            )
            ad_data = plan.benchmarks_referenced
            return {
                "status": "success",
                "headlines": ad_data.get("headlines", []),
                "descriptions": ad_data.get("descriptions", []),
                "ad_strength": ad_data.get("ad_strength_estimate", "Unknown"),
                "validation": ad_data.get("validation", {}),
                "plan": plan.to_dict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/agents/rsa-generator/preview", tags=["Agents"])
    async def rsa_preview(req: RSAGenerateRequest):
        """Quick preview of ad copy without ActionPlan."""
        try:
            preview = state.rsa_generator.preview_ad(
                tenant_id=req.tenant_id,
                context=req.context,
            )
            return {
                "status": "success",
                **preview,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # --- Search Terms Cleaner -----------------------------------------
    
    @app.post("/api/v1/agents/search-cleaner/analyze", tags=["Agents"])
    async def search_clean_analyze(req: SearchCleanRequest):
        """
        Analyze search terms and generate cleanup ActionPlan.
        
        Each term needs: term, impressions, clicks, cost, conversions
        """
        try:
            plan = state.search_cleaner.analyze_and_clean(
                tenant_id=req.tenant_id,
                search_terms=req.search_terms,
                industry=req.industry,
                custom_negatives=req.custom_negatives,
                target_cpa=req.target_cpa,
            )
            clean_data = plan.benchmarks_referenced
            return {
                "status": "success",
                "negatives": clean_data.get("negatives", []),
                "positives": clean_data.get("positives", []),
                "total_waste": clean_data.get("total_waste", 0),
                "plan": plan.to_dict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/agents/search-cleaner/summary", tags=["Agents"])
    async def search_clean_summary(req: SearchCleanRequest):
        """Quick search terms summary for dashboard."""
        try:
            summary = state.search_cleaner.get_summary(
                tenant_id=req.tenant_id,
                search_terms=req.search_terms,
                industry=req.industry,
            )
            return {
                "status": "success",
                **summary,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # ===================================================================
    # WORKFLOW ENDPOINTS
    # ===================================================================
    
    @app.get("/api/v1/workflows", tags=["Workflows"])
    async def list_workflows():
        """List all available workflow definitions."""
        workflows = state.workflow_engine.list_workflows()
        return {
            "workflows": workflows,
            "count": len(workflows),
        }
    
    @app.get("/api/v1/workflows/{workflow_id}", tags=["Workflows"])
    async def get_workflow(workflow_id: str):
        """Get a workflow definition with full step details."""
        wf = state.workflow_engine.get_workflow(workflow_id)
        if not wf:
            raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
        return {
            "workflow": wf,
        }
    
    @app.post("/api/v1/workflows/{workflow_id}/run", tags=["Workflows"])
    async def run_workflow(workflow_id: str, req: WorkflowRunRequest):
        """
        Run a workflow.
        
        The workflow engine will execute each step using the assigned agents.
        Set auto_approve=true to skip approval gates.
        """
        wf = state.workflow_engine.get_workflow(workflow_id)
        if not wf:
            raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
        
        try:
            execution = await state.workflow_engine.run(
                workflow_id=workflow_id,
                tenant_id=req.tenant_id,
                context=req.context,
                dry_run=req.dry_run,
                auto_approve=req.auto_approve,
            )
            return {
                "status": "success",
                "execution": execution.to_dict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/workflows/history/list", tags=["Workflows"])
    async def workflow_history(tenant_id: str = None, limit: int = 20):
        """Get recent workflow execution history."""
        history = state.workflow_engine.get_execution_history(tenant_id, limit)
        return {
            "history": history,
            "count": len(history),
        }
    
    @app.get("/api/v1/workflows/stats/summary", tags=["Workflows"])
    async def workflow_stats():
        """Get workflow engine statistics."""
        return state.workflow_engine.get_stats()
    
    # ===================================================================
    # ORCHESTRATOR ENDPOINTS
    # ===================================================================
    
    @app.post("/api/v1/orchestrator/request", tags=["Orchestrator"])
    async def orchestrator_request(req: OrchestratorRequest):
        """
        Send a high-level request to the orchestrator.
        
        request_type options: optimize, launch_campaign, adjust_budget,
        emergency, clean_search_terms, cleanup
        """
        try:
            result = await state.orchestrator.handle_request(
                tenant_id=req.tenant_id,
                request_type=req.request_type,
                context=req.context,
                auto_approve=req.auto_approve,
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/orchestrator/triage", tags=["Orchestrator"])
    async def orchestrator_triage(req: TriageRequest):
        """
        Auto-triage: analyze metrics and decide which workflow to run.
        
        Metrics: cpa, ctr, budget_pacing (percentage)
        Returns urgency level (critical/high/normal) and executes the right workflow.
        """
        try:
            result = await state.orchestrator.auto_triage(
                tenant_id=req.tenant_id,
                metrics=req.metrics,
                industry=req.industry,
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/orchestrator/schedule", tags=["Orchestrator"])
    async def orchestrator_schedule(req: ScheduleRequest):
        """
        Handle a scheduled trigger (e.g., from cron job or Lambda).
        
        Triggers: weekly_optimization, schedule_weekly, search_terms_cleanup,
        every_monday, every_wednesday
        """
        try:
            result = await state.orchestrator.handle_schedule(
                tenant_id=req.tenant_id,
                trigger=req.trigger,
                context=req.context,
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/orchestrator/actions", tags=["Orchestrator"])
    async def orchestrator_actions():
        """List all available orchestrator actions and their workflows."""
        actions = state.orchestrator.get_available_actions()
        return {
            "actions": actions,
            "count": len(actions),
        }
    
    @app.get("/api/v1/orchestrator/stats", tags=["Orchestrator"])
    async def orchestrator_stats():
        """Get orchestrator statistics."""
        return state.orchestrator.get_stats()
    
    @app.get("/api/v1/orchestrator/history", tags=["Orchestrator"])
    async def orchestrator_history(tenant_id: str = None, limit: int = 20):
        """Get recent orchestrator request history."""
        history = state.orchestrator.get_request_history(tenant_id, limit)
        return {
            "history": history,
            "count": len(history),
        }
    
    # ===================================================================
    # PLAN EXECUTION ENDPOINTS
    # ===================================================================
    
    @app.get("/api/v1/plans/history", tags=["Plans"])
    async def plan_execution_history(tenant_id: str = None, limit: int = 20):
        """Get ActionPlan execution history."""
        history = state.plan_executor.get_execution_history(tenant_id, limit)
        return {
            "history": history,
            "count": len(history),
        }
    
    @app.get("/api/v1/plans/stats", tags=["Plans"])
    async def plan_execution_stats():
        """Get ActionPlan executor statistics."""
        return state.plan_executor.get_stats()
    
    # ===================================================================
    # KNOWLEDGE BASE ENDPOINTS
    # ===================================================================
    
    @app.get("/api/v1/knowledge/rules", tags=["Knowledge"])
    async def get_rules(tenant_id: str = "default", industry: str = ""):
        """Get all decision rules."""
        rules = state.knowledge_store.get_rules(tenant_id, industry)
        return {"rules": rules, "count": len(rules)}
    
    @app.get("/api/v1/knowledge/benchmarks", tags=["Knowledge"])
    async def get_benchmarks(tenant_id: str = "default", industry: str = "financial_services"):
        """Get industry benchmarks."""
        benchmarks = state.knowledge_store.get_benchmarks(tenant_id, industry)
        return {"benchmarks": benchmarks}
    
    @app.get("/api/v1/knowledge/guardrails", tags=["Knowledge"])
    async def get_guardrails(tenant_id: str = "default", industry: str = "financial_services"):
        """Get content and budget guardrails."""
        guardrails = state.knowledge_store.get_guardrails(tenant_id, industry)
        return {"guardrails": guardrails}
    
    @app.get("/api/v1/knowledge/playbooks", tags=["Knowledge"])
    async def get_playbooks(tenant_id: str = "default", industry: str = ""):
        """Get operational playbooks."""
        playbooks = state.knowledge_store.get_playbooks(tenant_id, industry)
        return {"playbooks": playbooks, "count": len(playbooks)}
    
    @app.get("/api/v1/knowledge/templates", tags=["Knowledge"])
    async def get_templates(tenant_id: str = "default", industry: str = ""):
        """Get ad copy and campaign templates."""
        templates = state.knowledge_store.get_templates(tenant_id, industry)
        return {"templates": templates}
    
    # ===================================================================
    # DASHBOARD ENDPOINT
    # ===================================================================
    
    @app.get("/api/v1/dashboard/{tenant_id}", tags=["Dashboard"])
    async def dashboard(tenant_id: str, industry: str = "financial_services"):
        """
        Full dashboard data for a tenant.
        Returns consolidated view of all system components.
        """
        return {
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "system": {
                "workflow_stats": state.workflow_engine.get_stats(),
                "orchestrator_stats": state.orchestrator.get_stats(),
                "executor_stats": state.plan_executor.get_stats(),
            },
            "workflows": {
                "available": state.workflow_engine.list_workflows(),
                "recent_executions": state.workflow_engine.get_execution_history(tenant_id, 5),
            },
            "orchestrator": {
                "available_actions": state.orchestrator.get_available_actions(),
                "recent_requests": state.orchestrator.get_request_history(tenant_id, 5),
            },
            "knowledge": {
                "rules_count": len(state.knowledge_store.get_rules(tenant_id, industry)),
                "benchmarks": state.knowledge_store.get_benchmarks(tenant_id, industry),
            },
        }
    
    # ===================================================================
    # SYSTEM ENDPOINTS
    # ===================================================================
    
    @app.get("/api/v1/system/health", tags=["System"])
    async def system_health():
        """Comprehensive system health with all components."""
        return {
            "status": "ok",
            "service": "nadakki-google-ads-mvp",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
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
            "stats": {
                "workflows": state.workflow_engine.get_stats(),
                "orchestrator": state.orchestrator.get_stats(),
                "plan_executor": state.plan_executor.get_stats(),
            },
        }
    
    @app.get("/api/v1/system/endpoints", tags=["System"])
    async def list_endpoints():
        """List all available API endpoints."""
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name,
                })
        return {
            "endpoints": sorted(routes, key=lambda r: r["path"]),
            "count": len(routes),
        }
    
    logger.info(f"[OK] Day 6 API routes registered (all agent/workflow/orchestrator endpoints)")
    
    return app
