# Batch de 13 agentes restantes - Guardarlo y ejecutar para generar
# Los agentes son plantillas simplificadas v3.0 que aceptan dict

AGENTS = {
    "leadscoringia": {
        "purpose": "Lead Scoring con Explicabilidad",
        "main_output": ["score", "bucket", "reasons", "recommended_action"]
    },
    "conversioncohortia": {
        "purpose": "Análisis de Cohortes de Conversión", 
        "main_output": ["cohorts", "insights", "recommendations"]
    },
    "influencermatcheria": {
        "purpose": "Matching de Influencers",
        "main_output": ["matches", "fit_scores", "recommendations"]
    },
    "influencermatchingia": {
        "purpose": "Matching Avanzado de Influencers",
        "main_output": ["matches", "audience_overlap", "roi_potential"]
    },
    "personalizationengineia": {
        "purpose": "Motor de Personalización",
        "main_output": ["personalized_content", "segments", "recommendations"]
    },
    "competitorintelligenceia": {
        "purpose": "Inteligencia Competitiva",
        "main_output": ["competitors", "analysis", "opportunities"]
    },
    "competitoranalyzeria": {
        "purpose": "Análisis de Competidores",
        "main_output": ["competitor_profiles", "strengths", "weaknesses"]
    },
    "creativeanalyzeria": {
        "purpose": "Análisis de Creativos",
        "main_output": ["creative_scores", "recommendations", "best_practices"]
    },
    "journeyoptimizeria": {
        "purpose": "Optimización de Customer Journey",
        "main_output": ["journey_map", "bottlenecks", "optimizations"]
    },
    "contactqualityia": {
        "purpose": "Calidad de Contactos",
        "main_output": ["quality_scores", "issues", "recommendations"]
    },
    "marketingorchestratorea": {
        "purpose": "Orquestador de Marketing",
        "main_output": ["orchestrated_actions", "priorities", "timeline"]
    },
    "socialpostgeneratoria": {
        "purpose": "Generador de Posts Sociales",
        "main_output": ["posts", "hashtags", "optimal_timing"]
    },
    "campaignoptimizeria": {
        "purpose": "Optimización de Campañas",
        "main_output": ["optimizations", "budget_reallocation", "expected_lift"]
    }
}
