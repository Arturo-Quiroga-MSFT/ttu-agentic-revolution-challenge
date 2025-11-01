#!/bin/bash

# Deploy Multi-Agent Timesheet Assistant (PRODUCTION) to Azure Container Apps
# ============================================================================

set -e

echo "🚀 Multi-Agent Timesheet Assistant - PRODUCTION Deployment"
echo "=========================================================="

# Configuration
APP_NAME="ccg-multi-agent-prod"
RESOURCE_GROUP="rg-${APP_NAME}"
LOCATION="eastus"
ACR_NAME="acr${APP_NAME//-/}$(date +%s)"
ENVIRONMENT_NAME="env-${APP_NAME}"
IMAGE_NAME="${APP_NAME}:latest"

# Load environment variables from .env
if [ -f .env ]; then
    echo "📋 Loading configuration from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Please create one based on .env.example"
    exit 1
fi

echo ""
echo "🔧 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  App Name: $APP_NAME"
echo ""

# Prompt for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Step 1: Create resource group
echo ""
echo "📦 Step 1: Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

# Step 2: Create Azure Container Registry
echo ""
echo "🐳 Step 2: Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output table

# Step 3: Build and push image to ACR
echo ""
echo "🔨 Step 3: Building and pushing container image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME \
    --file Dockerfile \
    . \
    --output table

# Step 4: Get ACR credentials
echo ""
echo "🔑 Step 4: Retrieving ACR credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" -o tsv)

echo "  ACR Server: $ACR_SERVER"

# Step 5: Create Container Apps environment
echo ""
echo "🌍 Step 5: Creating Container Apps environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

# Step 6: Create Container App
echo ""
echo "📱 Step 6: Creating Container App..."
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image "${ACR_SERVER}/${IMAGE_NAME}" \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8501 \
    --ingress external \
    --env-vars \
        "USE_AZURE_OPENAI=${USE_AZURE_OPENAI}" \
        "AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}" \
        "AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}" \
        "AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME}" \
        "AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}" \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --output table

# Step 7: Get app URL
echo ""
echo "🌐 Step 7: Retrieving application URL..."
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo "✅ Deployment complete!"
echo "=========================================="
echo "🌐 Application URL: https://$APP_URL"
echo "📦 Resource Group: $RESOURCE_GROUP"
echo "🐳 Container Registry: $ACR_NAME"
echo "📱 Container App: $APP_NAME"
echo ""
echo "💡 To view logs:"
echo "   az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "🗑️  To delete all resources:"
echo "   az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
