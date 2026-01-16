"""
NADAKKI AI SUITE - AUTONOMOUS ORCHESTRATOR
Orquestador que coordina la ejecución autónoma de múltiples agentes en workflows.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class WorkflowStatus(Enum):
    """Estados de un workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Paso individual de un workflow"""
    step_id: str
    agent_id: str
    name: str
    input_template: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencias
    depends_on: List[str] = field(default_factory=list)  # Lista de step_ids
    
    # Configuración
    timeout_seconds: int = 300
    retry_on_failure: bool = True
    max_retries: int = 2
    continue_on_failure: bool = False  # Si True, workflow continúa aunque este paso falle
    
    # Estado (se llena durante ejecución)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Definición de un workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    
    # Configuración global
    parallel_execution: bool = False  # Si True, ejecuta pasos sin dependencias en paralelo
    stop_on_first_failure: bool = True
    timeout_seconds: int = 1800  # 30 minutos
    
    # Metadata
    category: str = "general"
    tags: List[str] = field(default_factory=list)


@dataclass
class WorkflowExecution:
    """Ejecución de un workflow"""
    execution_id: str
    workflow_id: str
    tenant_id: str
    
    # Input/Output
    input_data: Dict[str, Any]
    step_results: Dict[str, Dict] = field(default_factory=dict)
    final_output: Optional[Dict] = None
    
    # Estado
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    
    # Errores
    errors: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "tenant_id": self.tenant_id,
            "status": self.status.value,
            "current_step": self.current_step,
            "steps_completed": len([r for r in self.step_results.values() if r.get("success")]),
            "total_steps": len(self.step_results),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "errors": self.errors
        }


class AutonomousOrchestrator:
    """
    Orquestador de workflows autónomos.
    
    FUNCIONALIDADES:
    1. Definir workflows de múltiples agentes
    2. Ejecutar workflows respetando dependencias
    3. Pasar outputs de un agente como inputs del siguiente
    4. Ejecución paralela cuando es posible
    5. Manejo de errores y reintentos
    6. Logging y monitoreo de workflows
    """
    
    def __init__(
        self,
        tenant_id: str,
        agent_executor: Callable
    ):
        self.tenant_id = tenant_id
        self.agent_executor = agent_executor
        
        # Workflows registrados
        self.workflows: Dict[str, WorkflowDefinition] = {}
        
        # Ejecuciones activas
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # Historial
        self.execution_history: List[WorkflowExecution] = []
        self._max_history = 200
        
        # Stats
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_steps_executed": 0
        }
        
        # Cargar workflows por defecto
        self._load_default_workflows()
        
        print(f"🎭 AutonomousOrchestrator inicializado para tenant: {tenant_id}")
        print(f"   {len(self.workflows)} workflows disponibles")
    
    def _load_default_workflows(self):
        """Cargar workflows predefinidos"""
        
        # 1. SOCIAL CAMPAIGN LAUNCH
        self.register_workflow(WorkflowDefinition(
            workflow_id="social_campaign_launch",
            name="Social Campaign Launch",
            description="Lanza una campaña completa en redes sociales",
            category="campaign",
            steps=[
                WorkflowStep(
                    step_id="generate_content",
                    agent_id="contentgeneratoria",
                    name="Generar Contenido",
                    input_template={"task": "create_campaign_content"}
                ),
                WorkflowStep(
                    step_id="segment_audience",
                    agent_id="audiencesegmenteria",
                    name="Segmentar Audiencia",
                    input_template={"task": "identify_target_audience"}
                ),
                WorkflowStep(
                    step_id="optimize_timing",
                    agent_id="contentperformanceia",
                    name="Optimizar Timing",
                    depends_on=["generate_content"],
                    input_template={"task": "find_best_posting_time"}
                ),
                WorkflowStep(
                    step_id="publish_posts",
                    agent_id="socialpostgeneratoria",
                    name="Publicar en Redes",
                    depends_on=["generate_content", "segment_audience", "optimize_timing"],
                    input_template={"task": "publish_campaign"}
                ),
                WorkflowStep(
                    step_id="monitor_sentiment",
                    agent_id="sentimentanalyzeria",
                    name="Monitorear Sentimiento",
                    depends_on=["publish_posts"],
                    input_template={"task": "monitor_reactions"}
                )
            ],
            parallel_execution=True,
            tags=["social", "campaign", "content"]
        ))
        
        # 2. LEAD NURTURING WORKFLOW
        self.register_workflow(WorkflowDefinition(
            workflow_id="lead_nurturing",
            name="Lead Nurturing Automático",
            description="Proceso completo de nurturing de leads",
            category="leads",
            steps=[
                WorkflowStep(
                    step_id="score_lead",
                    agent_id="leadscoringia",
                    name="Calificar Lead",
                    input_template={"task": "score_and_qualify"}
                ),
                WorkflowStep(
                    step_id="predict_conversion",
                    agent_id="predictiveleadia",
                    name="Predecir Conversión",
                    depends_on=["score_lead"],
                    input_template={"task": "predict_conversion_probability"}
                ),
                WorkflowStep(
                    step_id="personalize_journey",
                    agent_id="personalizationengineia",
                    name="Personalizar Journey",
                    depends_on=["score_lead", "predict_conversion"],
                    input_template={"task": "create_personalized_journey"}
                ),
                WorkflowStep(
                    step_id="send_email",
                    agent_id="emailautomationia",
                    name="Enviar Email",
                    depends_on=["personalize_journey"],
                    input_template={"task": "send_nurturing_email"}
                ),
                WorkflowStep(
                    step_id="optimize_journey",
                    agent_id="journeyoptimizeria",
                    name="Optimizar Journey",
                    depends_on=["send_email"],
                    input_template={"task": "analyze_and_optimize"}
                )
            ],
            parallel_execution=True,
            tags=["leads", "email", "nurturing"]
        ))
        
        # 3. COMPETITIVE ANALYSIS
        self.register_workflow(WorkflowDefinition(
            workflow_id="competitive_analysis",
            name="Análisis Competitivo Completo",
            description="Análisis profundo de competencia",
            category="analytics",
            steps=[
                WorkflowStep(
                    step_id="analyze_competitors",
                    agent_id="competitoranalyzeria",
                    name="Analizar Competidores",
                    input_template={"task": "competitor_overview"}
                ),
                WorkflowStep(
                    step_id="intelligence_deep_dive",
                    agent_id="competitorintelligenceia",
                    name="Inteligencia Profunda",
                    depends_on=["analyze_competitors"],
                    input_template={"task": "deep_competitive_intelligence"}
                ),
                WorkflowStep(
                    step_id="social_listening",
                    agent_id="sociallisteningia",
                    name="Escucha Social",
                    input_template={"task": "monitor_competitor_mentions"}
                ),
                WorkflowStep(
                    step_id="pricing_analysis",
                    agent_id="pricingoptimizeria",
                    name="Análisis de Precios",
                    depends_on=["intelligence_deep_dive"],
                    input_template={"task": "compare_pricing_strategies"}
                ),
                WorkflowStep(
                    step_id="content_gap",
                    agent_id="contentperformanceia",
                    name="Análisis Content Gap",
                    depends_on=["analyze_competitors"],
                    input_template={"task": "identify_content_gaps"}
                )
            ],
            parallel_execution=True,
            tags=["analytics", "competitive", "intelligence"]
        ))
        
        # 4. CAMPAIGN OPTIMIZATION
        self.register_workflow(WorkflowDefinition(
            workflow_id="campaign_optimization",
            name="Optimización de Campaña",
            description="Optimiza una campaña activa",
            category="campaign",
            steps=[
                WorkflowStep(
                    step_id="analyze_performance",
                    agent_id="contentperformanceia",
                    name="Analizar Rendimiento",
                    input_template={"task": "analyze_campaign_metrics"}
                ),
                WorkflowStep(
                    step_id="ab_testing",
                    agent_id="abtestingia",
                    name="Análisis A/B",
                    depends_on=["analyze_performance"],
                    input_template={"task": "evaluate_variants"}
                ),
                WorkflowStep(
                    step_id="attribution",
                    agent_id="attributionmodelia",
                    name="Análisis de Atribución",
                    depends_on=["analyze_performance"],
                    input_template={"task": "channel_attribution"}
                ),
                WorkflowStep(
                    step_id="budget_reallocation",
                    agent_id="budgetforecastia",
                    name="Reasignar Presupuesto",
                    depends_on=["ab_testing", "attribution"],
                    input_template={"task": "optimize_budget_allocation"}
                ),
                WorkflowStep(
                    step_id="optimize_campaign",
                    agent_id="campaignoptimizeria",
                    name="Aplicar Optimizaciones",
                    depends_on=["budget_reallocation"],
                    input_template={"task": "apply_optimizations"}
                )
            ],
            parallel_execution=True,
            tags=["campaign", "optimization", "ab_testing"]
        ))
        
        # 5. RETENTION PREVENTION
        self.register_workflow(WorkflowDefinition(
            workflow_id="retention_prevention",
            name="Prevención de Churn",
            description="Detecta y previene churn de clientes",
            category="retention",
            steps=[
                WorkflowStep(
                    step_id="predict_churn",
                    agent_id="retentionpredictoria",
                    name="Predecir Churn",
                    input_template={"task": "identify_at_risk_customers"}
                ),
                WorkflowStep(
                    step_id="analyze_retention",
                    agent_id="retentionpredictorea",
                    name="Analizar Causas",
                    depends_on=["predict_churn"],
                    input_template={"task": "analyze_churn_causes"}
                ),
                WorkflowStep(
                    step_id="personalize_offer",
                    agent_id="personalizationengineia",
                    name="Personalizar Oferta",
                    depends_on=["analyze_retention"],
                    input_template={"task": "create_retention_offer"}
                ),
                WorkflowStep(
                    step_id="product_recommendation",
                    agent_id="productaffinityia",
                    name="Recomendar Productos",
                    depends_on=["analyze_retention"],
                    input_template={"task": "suggest_relevant_products"}
                ),
                WorkflowStep(
                    step_id="send_winback",
                    agent_id="emailautomationia",
                    name="Enviar Win-Back",
                    depends_on=["personalize_offer", "product_recommendation"],
                    input_template={"task": "send_retention_email"}
                )
            ],
            parallel_execution=True,
            tags=["retention", "churn", "email"]
        ))
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Registrar un workflow"""
        self.workflows[workflow.workflow_id] = workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Obtener definición de workflow"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self, category: str = None) -> List[Dict]:
        """Listar workflows disponibles"""
        workflows = self.workflows.values()
        
        if category:
            workflows = [w for w in workflows if w.category == category]
        
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "description": w.description,
                "category": w.category,
                "steps_count": len(w.steps),
                "tags": w.tags
            }
            for w in workflows
        ]
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_id: str = None
    ) -> WorkflowExecution:
        """
        Ejecutar un workflow completo.
        
        Args:
            workflow_id: ID del workflow a ejecutar
            input_data: Datos de entrada
            execution_id: ID de ejecución (se genera si no se proporciona)
        
        Returns:
            WorkflowExecution con resultados
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow no encontrado: {workflow_id}")
        
        # Crear ejecución
        if not execution_id:
            execution_id = f"exec_{workflow_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            tenant_id=self.tenant_id,
            input_data=input_data,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )
        
        self.active_executions[execution_id] = execution
        
        print(f"\n🎬 Ejecutando workflow: '{workflow.name}'")
        print(f"   Pasos: {len(workflow.steps)}")
        
        try:
            # Crear copia de pasos para esta ejecución
            steps = {s.step_id: WorkflowStep(**s.__dict__) for s in workflow.steps}
            
            # Ejecutar pasos
            if workflow.parallel_execution:
                await self._execute_parallel(execution, steps, input_data)
            else:
                await self._execute_sequential(execution, steps, input_data)
            
            # Determinar estado final
            failed_steps = [s for s in steps.values() if s.status == WorkflowStatus.FAILED]
            
            if failed_steps and workflow.stop_on_first_failure:
                execution.status = WorkflowStatus.FAILED
            elif all(s.status == WorkflowStatus.COMPLETED for s in steps.values()):
                execution.status = WorkflowStatus.COMPLETED
                self.stats["successful_executions"] += 1
            else:
                execution.status = WorkflowStatus.COMPLETED  # Parcialmente completado
            
            # Compilar output final
            execution.final_output = self._compile_final_output(steps)
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append({
                "type": "workflow_error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            self.stats["failed_executions"] += 1
        
        # Finalizar
        execution.completed_at = datetime.utcnow().isoformat()
        execution.duration_ms = (
            datetime.fromisoformat(execution.completed_at) -
            datetime.fromisoformat(execution.started_at)
        ).total_seconds() * 1000
        
        # Mover a historial
        del self.active_executions[execution_id]
        self.execution_history.append(execution)
        if len(self.execution_history) > self._max_history:
            self.execution_history = self.execution_history[-self._max_history:]
        
        self.stats["total_executions"] += 1
        
        # Log resultado
        status_icon = "✅" if execution.status == WorkflowStatus.COMPLETED else "❌"
        print(f"\n{status_icon} Workflow '{workflow.name}' {execution.status.value}")
        print(f"   Duración: {execution.duration_ms:.0f}ms")
        
        return execution
    
    async def _execute_sequential(
        self,
        execution: WorkflowExecution,
        steps: Dict[str, WorkflowStep],
        input_data: Dict
    ):
        """Ejecutar pasos secuencialmente"""
        accumulated_results = {"input": input_data}
        
        for step in steps.values():
            execution.current_step = step.step_id
            await self._execute_step(step, accumulated_results, execution)
            
            if step.status == WorkflowStatus.COMPLETED:
                accumulated_results[step.step_id] = step.result
            elif not step.continue_on_failure:
                break
    
    async def _execute_parallel(
        self,
        execution: WorkflowExecution,
        steps: Dict[str, WorkflowStep],
        input_data: Dict
    ):
        """Ejecutar pasos en paralelo respetando dependencias"""
        accumulated_results = {"input": input_data}
        pending = set(steps.keys())
        completed = set()
        
        while pending:
            # Encontrar pasos listos para ejecutar
            ready = [
                step_id for step_id in pending
                if all(dep in completed for dep in steps[step_id].depends_on)
            ]
            
            if not ready:
                # Deadlock o dependencias circulares
                print("   ⚠️ No hay pasos listos para ejecutar")
                break
            
            # Ejecutar pasos listos en paralelo
            tasks = []
            for step_id in ready:
                step = steps[step_id]
                execution.current_step = step_id
                tasks.append(self._execute_step(step, accumulated_results, execution))
            
            await asyncio.gather(*tasks)
            
            # Actualizar estado
            for step_id in ready:
                step = steps[step_id]
                pending.discard(step_id)
                
                if step.status == WorkflowStatus.COMPLETED:
                    completed.add(step_id)
                    accumulated_results[step_id] = step.result
                elif step.continue_on_failure:
                    completed.add(step_id)  # Continuar aunque falló
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        accumulated_results: Dict,
        execution: WorkflowExecution
    ):
        """Ejecutar un paso individual"""
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.utcnow().isoformat()
        
        print(f"   ▶️ {step.name} ({step.agent_id})")
        
        retries = 0
        while retries <= step.max_retries:
            try:
                # Preparar input combinando template con resultados previos
                step_input = {
                    **step.input_template,
                    **accumulated_results.get("input", {}),
                    "previous_results": accumulated_results,
                    "step_id": step.step_id,
                    "tenant_id": self.tenant_id
                }
                
                # Ejecutar agente con timeout
                result = await asyncio.wait_for(
                    self.agent_executor(step.agent_id, step_input),
                    timeout=step.timeout_seconds
                )
                
                # Procesar resultado
                step.result = result.to_dict() if hasattr(result, 'to_dict') else {"result": result}
                step.status = WorkflowStatus.COMPLETED
                step.completed_at = datetime.utcnow().isoformat()
                
                execution.step_results[step.step_id] = step.result
                self.stats["total_steps_executed"] += 1
                
                print(f"      ✅ Completado")
                break
                
            except asyncio.TimeoutError:
                step.error = f"Timeout después de {step.timeout_seconds}s"
                retries += 1
                
            except Exception as e:
                step.error = str(e)
                retries += 1
        
        # Si todos los reintentos fallaron
        if step.status != WorkflowStatus.COMPLETED:
            step.status = WorkflowStatus.FAILED
            step.completed_at = datetime.utcnow().isoformat()
            
            execution.errors.append({
                "step_id": step.step_id,
                "error": step.error,
                "retries": retries - 1
            })
            
            print(f"      ❌ Falló: {step.error}")
    
    def _compile_final_output(self, steps: Dict[str, WorkflowStep]) -> Dict:
        """Compilar output final del workflow"""
        return {
            "steps_completed": sum(1 for s in steps.values() if s.status == WorkflowStatus.COMPLETED),
            "steps_failed": sum(1 for s in steps.values() if s.status == WorkflowStatus.FAILED),
            "results": {
                step_id: step.result
                for step_id, step in steps.items()
                if step.result
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        return {
            "tenant_id": self.tenant_id,
            "workflows_registered": len(self.workflows),
            "active_executions": len(self.active_executions),
            "stats": self.stats,
            "recent_executions": len(self.execution_history)
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de ejecuciones"""
        return [e.to_dict() for e in self.execution_history[-limit:]]
