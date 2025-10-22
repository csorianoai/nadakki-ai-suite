# 🚀 Nadakki AI Collections - Multi-Tenant Credit Evaluation Platform

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Multi-Tenant](https://img.shields.io/badge/multi--tenant-ready-brightgreen.svg)]()
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda%20Ready-orange.svg)]()

> Enterprise-grade AI-powered credit evaluation system for financial institutions across LATAM, designed for scalability, compliance, and multi-tenant architecture.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Multi-Tenant Configuration](#multi-tenant-configuration)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Nadakki AI Collections** is a comprehensive SaaS platform providing 350+ specialized AI agents for financial institutions including banks, credit unions, fintechs, and insurance companies. Built with enterprise-grade security, compliance, and multi-jurisdictional support.

### 💼 Ideal For:
- **Banks & Credit Unions** - Credit risk assessment and portfolio management
- **Fintechs** - Rapid credit decisions with AI-powered evaluation
- **Insurance Companies** - Risk scoring and underwriting automation
- **Investment Firms** - Credit analysis and market intelligence

---

## ✨ Features

### 🤖 AI Agent Ecosystem (350+ Agents)

The platform includes **21 specialized cores** with 350+ AI agents:

#### **Core Modules:**
- 🔍 **Originación Inteligente** (4 agents) - Predictive risk analysis, credit profiling
- 🧠 **Decisión Cuántica** (4 agents) - Hybrid similarity engine, instant approvals
- 📊 **Vigilancia Continua** (4 agents) - Portfolio monitoring, early warning systems
- 💸 **Recuperación Máxima** (4 agents) - Collections optimization, legal pathways
- 🛡️ **Compliance Supremo** (4 agents) - Regulatory monitoring, audit automation
- 📈 **Marketing Intelligence** (40 agents) - Lead scoring, campaign optimization
- 📚 **Legal Suite** (33 agents) - Contract analysis, regulatory compliance
- 💰 **Contabilidad** (29+ agents) - Financial reporting, IFRS compliance
- 🚚 **Logística** (23 agents) - Supply chain optimization
- 💼 **RRHH** (10 agents) - Talent acquisition, performance analytics
- ... and 11 more specialized cores

### 🏗️ Enterprise Architecture

- ✅ **Multi-Tenant by Design** - Isolated data, custom configurations per institution
- ✅ **Hybrid Similarity Engine** - Cosine + Euclidean + Jaccard algorithms
- ✅ **AWS Lambda Ready** - Serverless deployment with auto-scaling
- ✅ **Circuit Breaker Pattern** - Resilient microservices architecture
- ✅ **Compliance First** - GDPR, CCPA, AML/KYC ready
- ✅ **Multi-Jurisdictional** - Support for LATAM, US, EU regulations

### 🔒 Security & Compliance

- 🔐 JWT Authentication with role-based access control (RBAC)
- 🛡️ PII Detection and data masking
- 📝 Complete audit trail for all operations
- 🔍 Real-time compliance monitoring
- 📊 Explainable AI decisions for regulatory requirements

---

## 🏗️ Architecture

\\\
nadakki-ai-collections/
├── agents/                    # 350+ AI agents organized by ecosystem
│   ├── marketing/            # 40 agents - Lead scoring, campaigns
│   ├── legal/                # 33 agents - Contract analysis
│   ├── contabilidad/         # 29 agents - Financial reporting
│   ├── originacion/          # Credit origination agents
│   ├── decision/             # Decision engine agents
│   ├── vigilancia/           # Monitoring agents
│   ├── compliance/           # Compliance agents
│   └── [15+ more cores]      # Additional specialized agents
│
├── core/                      # Enterprise core components
│   ├── credit_engine.py      # Main credit evaluation engine
│   ├── hybrid_similarity_engine.py  # Similarity algorithms
│   ├── billing_system.py     # Usage tracking & billing
│   ├── authentication/       # JWT auth & RBAC
│   ├── tenant/               # Multi-tenant management
│   └── similarity/           # Advanced similarity algorithms
│
├── api/                       # REST API endpoints
│   ├── powerbi_api.py        # Power BI integration
│   └── powerbi_endpoints.py  # BI data endpoints
│
├── config/                    # Multi-tenant configurations
│   └── tenants/              # 15 institution configs
│       ├── banreservas.json
│       ├── credicefi.json
│       ├── popular.json
│       └── [12 more...]
│
├── app.py                     # Flask application entry point
├── credicefi_api.py          # Main API implementation
└── requirements.txt           # Python dependencies
\\\

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (3.12 recommended)
- **pip** or **poetry** for dependency management
- **PostgreSQL 14+** (production) or SQLite (development)
- **Redis 7+** (optional, for caching)

### Installation

\\\ash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/nadakki-ai-collections.git
cd nadakki-ai-collections

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Run the application
python app.py
\\\

The application will be available at **http://localhost:5000**

### Docker Quick Start

\\\ash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
curl http://localhost:5000/api/v1/health
\\\

---

## 🏢 Multi-Tenant Configuration

### Adding a New Institution

1. **Create tenant configuration** in \config/tenants/\:

\\\json
{
  "tenant_id": "my_institution",
  "name": "My Financial Institution",
  "region": "latam",
  "risk_thresholds": {
    "reject_auto": 0.90,
    "high_risk": 0.80,
    "medium_risk": 0.50
  },
  "features": {
    "credit_evaluation": true,
    "marketing_agents": true,
    "compliance_monitoring": true
  }
}
\\\

2. **Request evaluation** with tenant header:

\\\ash
curl -X POST http://localhost:5000/api/v1/evaluate \\
  -H "Content-Type: application/json" \\
  -H "X-Tenant-ID: my_institution" \\
  -d '{
    "profile": {
      "income": 50000,
      "credit_score": 750,
      "debt_to_income": 0.3
    }
  }'
\\\

### Supported Institutions

Currently configured for **15 institutions**:
- 🏦 Banco de Reservas (Dominican Republic)
- 🏦 Banco Popular (Dominican Republic)
- 🏦 Scotiabank
- 🏦 CrediFace
- 🏦 COFACI
- ... and 10 more

---

## 📚 API Reference

### Base URL
\\\
Production: https://api.nadakki.com/v1
Development: http://localhost:5000/api/v1
\\\

### Authentication
\\\ash
# All requests require tenant identification
X-Tenant-ID: your_tenant_id
Authorization: Bearer your_jwt_token
\\\

### Core Endpoints

#### Health Check
\\\ash
GET /api/v1/health
\\\

#### Credit Evaluation
\\\ash
POST /api/v1/evaluate
Content-Type: application/json
X-Tenant-ID: tenant_id

{
  "profile": {
    "income": 50000,
    "credit_score": 750,
    "age": 35,
    "employment_type": "full_time",
    "debt_to_income": 0.3
  }
}
\\\

**Response:**
\\\json
{
  "decision": "APPROVED",
  "risk_level": "LOW_RISK",
  "similarity_score": 0.42,
  "confidence": 0.95,
  "recommendations": ["Standard terms approved"],
  "response_time_ms": 302
}
\\\

For complete API documentation, see [API.md](docs/API.md)

---

## 🚀 Deployment

### AWS Lambda Deployment

The platform is optimized for serverless deployment on AWS:

\\\ash
# Package for Lambda
pip install -r requirements.txt -t package/
cd package && zip -r ../deployment.zip . && cd ..
zip -g deployment.zip app.py credicefi_api.py

# Deploy to AWS Lambda
aws lambda update-function-code \\
  --function-name nadakki-credit-evaluator \\
  --zip-file fileb://deployment.zip
\\\

### Production Deployment (AWS ECS/Fargate)

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide including:
- Infrastructure as Code (Terraform)
- CI/CD pipeline setup
- Monitoring and observability
- Auto-scaling configuration

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

\\\ash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linters
flake8 agents/ core/ api/
black agents/ core/ api/
\\\

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Key Differentiators

| Feature | Nadakki AI Collections | Traditional Solutions |
|---------|----------------------|----------------------|
| **AI Agents** | 350+ specialized agents | 3-5 generic models |
| **Multi-Tenant** | Built-in from day 1 | Retrofitted add-on |
| **Latency** | <300ms average | >1000ms typical |
| **Compliance** | GDPR, CCPA, AML, KYC ready | Manual compliance |
| **Explainability** | Full audit trail | Black box decisions |
| **Jurisdictions** | LATAM, US, EU | Single region |

---

## 📞 Support & Contact

- **Documentation**: [docs.nadakki.com](https://docs.nadakki.com)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/nadakki-ai-collections/issues)
- **Email**: support@nadakki.com
- **Website**: [nadakki.com](https://nadakki.com)

---

## 🙏 Acknowledgments

Built with ❤️ by the Nadakki team for financial institutions worldwide.

**Tech Stack:**
- Python 3.12 | Flask 3.1 | AWS Lambda | PostgreSQL | Redis
- Scikit-learn | NumPy | Pandas | JWT | SQLAlchemy

---

<div align="center">
  <strong>⭐ Star this repository if you find it useful!</strong>
</div>
