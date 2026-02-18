# CLAUDE — PHASE 6 (Security + Secrets Rotation) — EXECUTION PACK

## GOAL
Rotate exposed credentials, harden repo against future secret leaks, and lock down runtime security defaults.
Must be safe for SaaS + multi-tenant.

## CONSTRAINTS
- NO secrets in repo (ever).
- All secrets must move to environment variables (Render/Vercel).
- Add automated detection (gitleaks) + CI gate.
- Keep local dev workable via .env (not committed).

---

## P6-1) Inventory secrets (sources of truth)
Search for keys in repo:
- OpenAI
- Anthropic
- Meta/Facebook
- Google Ads / OAuth
- SendGrid
- Any JWT/API keys

Commands:
- ripgrep patterns (sk- , xoxb, SG., EAAB, etc.)
- list files containing "api_key", "secret", "token"

Output:
- SECURITY_REPORT.md with findings (file path + type of secret + action)

---

## P6-2) Rotate credentials (external actions + code updates)
Rotate/regenerate in providers:
- OpenAI API key
- Anthropic API key
- Meta app secret / tokens
- Google OAuth client secret + refresh tokens (if leaked)
- SendGrid API key

Code changes:
- Ensure code reads ONLY from env vars:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - META_ACCESS_TOKEN / META_APP_SECRET
  - GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN
  - SENDGRID_API_KEY

---

## P6-3) Repo hardening (gitignore + env templates)
- Add/verify .gitignore includes:
  .env
  .env.*
  *.key
  *.pem
  *.p12
  secrets/*
  data/audit_logs.jsonl (optional if you want it excluded)
  .claude/settings.local.json

- Add .env.example (NO real values)

---

## P6-4) Add gitleaks
Option A (preferred): pre-commit + CI
- Add .gitleaks.toml config
- Add GitHub Action workflow: gitleaks scan on PR + push to main
- Fail build if secrets found

Also provide local command:
  gitleaks detect --source . --redact --verbose

---

## P6-5) Runtime hardening (already partially done)
Confirm/ensure:
- CORS allowlist (done)
- Rate limiting (done)
- LIVE gate (done)
Add:
- Security headers middleware if applicable (FastAPI middleware)
- Request size limit (optional)
- Log redaction: never log tokens/keys

---

## P6-6) Verification
Deliver curl tests:
- health 200
- execute dry_run 200
- live 403 unless LIVE_ENABLED=true AND role=admin
- audit logs ok

---

## DELIVERABLES
- PR merged to main
- SECURITY_REPORT.md (no secrets, only findings summary)
- .env.example
- gitleaks config + CI workflow
- gitignore updates

