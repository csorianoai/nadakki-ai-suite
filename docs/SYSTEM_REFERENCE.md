# NADAKKI AI SUITE - DOCUMENTACIÓN COMPLETA DEL SISTEMA
# Última actualización: 13 de Enero, 2026
# Estado: 100% OPERATIVO

## URLS DE PRODUCCIÓN
| Servicio | URL |
|----------|-----|
| Frontend | https://dashboard.nadakki.com |
| Backend API | https://nadakki-ai-suite.onrender.com |
| API Docs | https://nadakki-ai-suite.onrender.com/docs |

## 35 AGENTES DE MARKETING (NOMBRES EXACTOS)
```
abtestingia, abtestingimpactia, attributionmodelia, audiencesegmenteria,
budgetforecastia, campaignoptimizeria, cashofferfilteria, channelattributia,
competitoranalyzeria, competitorintelligenceia, contactqualityia, contentgeneratoria,
contentperformanceia, conversioncohortia, creativeanalyzeria, customersegmentatonia,
emailautomationia, geosegmentationia, influencermatcheria, influencermatchingia,
journeyoptimizeria, leadscoria, leadscoringia, marketingmixmodelia,
marketingorchestratorea, minimalformia, personalizationengineia, predictiveleadia,
pricingoptimizeria, productaffinityia, retentionpredictorea, retentionpredictoria,
sentimentanalyzeria, sociallisteningia, socialpostgeneratoria
```

## API ENDPOINTS
- /health - Health check
- /agents - Lista agentes
- /cores - Lista cores
- /cores/marketing - Marketing core
- /api/campaigns - Campañas
- /api/segments - Segmentos
- /api/journeys - Journeys
- /api/templates - Templates
- /api/integrations - Integraciones
- /agents/marketing/{id}/execute - Ejecutar agente

## EJECUTAR AGENTE
POST /agents/marketing/{agent_id}/execute
Content-Type: application/json
Body: {"test":"data"}

## 10 WORKFLOWS
lead_qualification, content_generation, campaign_optimization,
social_media_management, email_automation, audience_segmentation,
ab_testing, customer_journey, analytics_reporting, competitive_intelligence
