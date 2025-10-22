# Nadakki AI Suite - Dockerfile Optimizado para Fargate
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY credicefi_api.py .
COPY start.sh .
COPY agents/ ./agents/
COPY api/ ./api/
COPY config/ ./config/
COPY core/ ./core/
COPY dashboard/ ./dashboard/
COPY integrations/ ./integrations/
COPY logs/ ./logs/
COPY models/ ./models/
COPY tests/ ./tests/

# Create non-root user for security
RUN useradd -m -u 1000 nadakki && \
    chown -R nadakki:nadakki /app && \
    chmod +x /app/start.sh

# Switch to non-root user
USER nadakki

# Health check for container health monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start command
CMD ["python", "app.py"]