# Nadakki Marketing UI - Day 2 v3.0

Sistema de gestión de campañas con CI/CD ready.

## Estructura
```
NadakkiMarketingUI/
├── backend/          # FastAPI
├── frontend/         # React
├── tests/            # Unit tests
├── scripts/          # Utils PowerShell
└── logs/             # Logs y resultados
```

## CI/CD Compatible
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps

## Quick Start
```bash
pip install -r requirements.txt
python tests/test_campaigns.py
cd backend && uvicorn main:app --reload
```
