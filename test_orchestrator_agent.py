import asyncio
from agents.marketing.marketingorchestratorea import (
    MarketingOrchestratorIA, OrchestrationInput, MarketingContext
)

async def test():
    agent = MarketingOrchestratorIA("tn_test_bank_001")
    
    context = MarketingContext(
        total_budget=100000.0,
        campaign_phase="execution",
        primary_goal="increase_retention",
        target_roi=3.5,
        current_challenges=["High churn in month 3", "Low email engagement"],
        available_channels=["email", "social", "paid_ads", "sms"],
        time_horizon_days=90
    )
    
    inp = OrchestrationInput(
        tenant_id="tn_test_bank_001",
        marketing_context=context,
        focus_areas=["retention", "engagement", "optimization"]
    )
    
    result = await agent.execute(inp)
    print("✅ RESULTADO:", result.orchestration_id)
    print("\n" + "="*80)
    print("RESUMEN EJECUTIVO:")
    print("="*80)
    print(result.executive_summary)
    
    print("\n" + "="*80)
    print("ACCIONES ESTRATÉGICAS PRIORIZADAS:")
    print("="*80)
    for i, action_id in enumerate(result.prioritized_initiatives[:5], 1):
        action = next(a for a in result.strategic_actions if a.action_id == action_id)
        print(f"\n{i}. [{action.priority.upper()}] {action.title}")
        print(f"   ROI: {action.expected_roi}x | Costo: ${action.estimated_cost:,.0f}")
        print(f"   Impacto: {action.estimated_impact}")
        print(f"   Agente: {action.recommended_agent}")
    
    print("\n" + "="*80)
    print("INSIGHTS DEL DASHBOARD:")
    print("="*80)
    for insight in result.dashboard_insights:
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🟢"}[insight.severity]
        print(f"\n{emoji} {insight.title}")
        print(f"   {insight.description}")
        if insight.recommended_actions:
            print(f"   Acciones: {insight.recommended_actions[0]}")
    
    print("\n" + "="*80)
    print("ASIGNACIÓN DE PRESUPUESTO:")
    print("="*80)
    for alloc in result.budget_allocation:
        print(f"  {alloc.category}: ${alloc.allocated_amount:,.0f} → ROI esperado: ${alloc.expected_return:,.0f}")
    
    print("\n" + "="*80)
    print("PROYECCIONES KPI:")
    print("="*80)
    for kpi, value in result.kpi_projections.items():
        print(f"  {kpi}: {value:.1f}%")
    
    metrics = agent.get_metrics()
    print(f"\n{'='*80}")
    print(f"MÉTRICAS: {metrics['ok']}/{metrics['total']}, Orchestrations: {metrics['orchestrations']}")
    print("\n✅ MarketingOrchestratorIA funciona - SUPER AGENTE COMPLETO")

asyncio.run(test())