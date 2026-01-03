# Day 5: Testing + CI/CD + Deployment v5.1

## Test Suite
```bash
# All tests
python tests/test_all.py

# With coverage
pytest tests/ --cov=backend --cov-report=html

# Specific
pytest tests/unit -v
pytest tests/integration -v
pytest tests/e2e -v
```

## Linting
```bash
# Check
black --check .
isort --check-only .
flake8 .

# Fix
black .
isort .
```

## Docker
```bash
docker-compose up -d
docker-compose down
```

## PowerShell Aliases
```powershell
. .\scripts\nadakki-aliases.ps1
ndk-test      # Run tests
ndk-test-cov  # Tests + coverage
ndk-lint      # Check format
ndk-run       # Start server
```

## Makefile
```bash
make test
make test-cov
make lint
make docker-up
```
