FROM python:3.11-slim

# Metadata del proyecto
LABEL maintainer="Nadakki AI Suite <dev@nadakki.com>"
LABEL version="2.0.0"
LABEL description="Multi-tenant Credit Risk AI Platform"

# Variables de entorno por defecto
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV WORKERS=4
ENV TIMEOUT=120
ENV MAX_REQUESTS=1000

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 nadakki && chown -R nadakki:nadakki /app
USER nadakki

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
