# NADAKKI AI SUITE - GUÍA DE SETUP PARA NUEVAS TERMINALES

## REQUISITOS PREVIOS
- Git instalado
- Python 3.10+ instalado
- Node.js 18+ instalado (para frontend)
- Acceso al repositorio GitHub

## PASO 1: CLONAR EL REPOSITORIO
```bash
# Backend
git clone https://github.com/csorianoai/nadakki-ai-suite.git
cd nadakki-ai-suite

# Frontend (si es necesario)
git clone https://github.com/csorianoai/nadakki-dashboard.git
```

## PASO 2: CONFIGURAR BACKEND
```bash
cd nadakki-ai-suite

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\activate

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (copiar de .env.example)
copy .env.example .env
```

## PASO 3: EJECUTAR LOCALMENTE
```bash
# Iniciar servidor de desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Verificar en: http://localhost:8000/docs
```

## PASO 4: MANTENER SINCRONIZADO
```bash
# Antes de empezar a trabajar, siempre hacer pull
git pull origin main

# Después de hacer cambios
git add .
git commit -m "descripción del cambio"
git push origin main
```

## VARIABLES DE ENTORNO (.env)
```
DATABASE_URL=sqlite:///./nadakki.db
SECRET_KEY=tu-secret-key
ENVIRONMENT=development
```

## VERIFICAR INSTALACIÓN
```bash
# Test rápido
curl http://localhost:8000/health

# O en PowerShell
Invoke-RestMethod http://localhost:8000/health
```

## PRODUCCIÓN
- Los cambios en main se despliegan automáticamente en Render
- Frontend en Vercel se despliega automáticamente
- Tiempo de deploy: ~2-3 minutos
