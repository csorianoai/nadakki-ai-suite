#!/bin/bash
# Nadakki Enterprise Deployment Script
# Auto-generated deployment automation

echo "🚀 Starting Nadakki Enterprise Deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_enterprise.txt

# Setup environment
echo "🔧 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please configure .env file with your settings"
fi

# Initialize database
echo "🗄️ Initializing database..."
# Add your database initialization commands here

# Start Redis (if not running)
echo "📡 Starting Redis..."
redis-server --daemonize yes 2>/dev/null || echo "Redis already running or not installed"

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

# Start application
echo "🌟 Starting Nadakki Enterprise..."
if [ "$1" = "production" ]; then
    gunicorn main_enterprise:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
    python main_enterprise.py
fi
