#!/bin/bash
# AWS ECS Deployment Script

# Variables
CLUSTER_NAME="nadakki-production"
SERVICE_NAME="nadakki-api"
TASK_FAMILY="nadakki-task"
REGION="us-east-1"
ECR_REPO="your-account-id.dkr.ecr.us-east-1.amazonaws.com/nadakki"

# Build y push imagen Docker
docker build -t nadakki-api .
docker tag nadakki-api:latest 
aws ecr get-login-password --region  | docker login --username AWS --password-stdin 
docker push 

# Crear cluster ECS si no existe
aws ecs create-cluster --cluster-name  --region 

# Registrar task definition
aws ecs register-task-definition --region  --cli-input-json file://task-definition.json

# Crear o actualizar servicio
aws ecs create-service \
    --cluster  \
    --service-name  \
    --task-definition  \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
    --region 

echo "Deployment completed. Check ECS console for status."
