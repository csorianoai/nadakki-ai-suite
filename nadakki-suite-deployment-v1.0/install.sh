#!/bin/bash

echo "🚀 Iniciando instalación de Nadakki AI Suite..."

# 1. Crear namespaces
kubectl create namespace credicefi
kubectl create namespace cofaci
kubectl create namespace confisa

# 2. Desplegar Helm charts para los tenants
helm upgrade --install credicefi-runtime ./runtime/helm/nadakki-runtime --set image.tag=latest --namespace credicefi
helm upgrade --install cofaci-runtime ./runtime/helm/nadakki-runtime --set image.tag=latest --namespace cofaci
helm upgrade --install confisa-runtime ./runtime/helm/nadakki-runtime --set image.tag=latest --namespace confisa

# 3. Iniciar mock API server (en background)
echo "🧠 Levantando servidor API simulado para tenants..."
cd mock_api_server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# 4. Mensaje final
echo "✅ Nadakki AI Suite desplegado con éxito."
echo "🌐 Accede al tester visual en sandbox_ui/index.html"
