.PHONY: help install test lint format docker-up docker-down clean

help:
    @echo "Nadakki Marketing Suite - Comandos disponibles:"
    @echo "  make install      - Instalar dependencias"
    @echo "  make test         - Ejecutar tests"
    @echo "  make test-cov     - Tests con cobertura"
    @echo "  make lint         - Verificar formato"
    @echo "  make format       - Formatear código"
    @echo "  make docker-up    - Iniciar Docker"
    @echo "  make docker-down  - Detener Docker"
    @echo "  make clean        - Limpiar cache"

install:
    pip install -r requirements.txt
    pip install black flake8 isort pytest-cov

test:
    python tests/test_all.py

test-cov:
    pytest tests/ -v --cov=backend --cov-report=html --cov-report=term

lint:
    @echo "Running Black..."
    black --check . --exclude "venv|__pycache__"
    @echo "Running isort..."
    isort --check-only . --skip venv
    @echo "Running Flake8..."
    flake8 . --max-line-length=120 --exclude=venv,__pycache__

format:
    black . --exclude "venv|__pycache__"
    isort . --skip venv

docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

clean:
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache htmlcov .coverage
