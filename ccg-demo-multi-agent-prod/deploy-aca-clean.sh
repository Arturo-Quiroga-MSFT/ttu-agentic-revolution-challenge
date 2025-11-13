#!/bin/bash

# Multi-Agent Timesheet Assistant - Production Deployment
# Simple, clean deployment script that works for both initial and updates

set -e

echo "🚀 Multi-Agent Timesheet Assistant - PRODUCTION Deployment"
echo "=========================================================="

# Configuration
APP_NAME="ccg-multi-agent-prod"
RESOURCE_GROUP="rg-${APP_NAME}"
LOCATION="eastus"
ACR_NAME="acrccgmultiagentprod"
ENVIRONMENT_NAME="env-${APP_NAME}"
IMAGE_NAME="${APP_NAME}:latest"

# Load environment variables from .env
if [ -f .env ]; then
    echo "📋 Loading configuration from .env file..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
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

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Step 1: Ensure resource group exists
echo ""
echo "📦 Step 1: Resource Group"
az group create --name $RESOURCE_GROUP --location $LOCATION -o none
echo "✅ Resource group ready"

# Step 2: Ensure ACR exists
echo ""
echo "🐳 Step 2: Container Registry"
if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating ACR..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true \
        -o none
fi
echo "✅ Container registry ready"

# Step 3: Build and push image
echo ""
echo "🔨 Step 3: Building container image"
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME \
    --file Dockerfile \
    . \
    --platform linux/amd64 \
    -o table

# Step 4: Get ACR credentials
echo ""
echo "🔑 Step 4: Getting credentials"
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
echo "✅ Credentials retrieved"

# Step 5: Ensure Container Apps environment exists
echo ""
echo "🌍 Step 5: Container Apps Environment"
if ! az containerapp env show --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating environment..."
    az containerapp env create \
        --name $ENVIRONMENT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        -o none
fi
echo "✅ Environment ready"

# Step 6: Deploy Container App (delete and recreate for simplicity)
echo ""
echo "📱 Step 6: Deploying Container App"

# Delete if exists (simplest approach for updates)
if az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Deleting existing app..."
    az containerapp delete \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes \
        -o none
    echo "Waiting for deletion to complete..."
    sleep 10
fi

# Create the app
echo "Creating app..."
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
    -o none

echo "✅ App deployed"

# Step 7: Get app URL
echo ""
echo "🌐 Step 7: Getting application URL"
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo "✅ Deployment Complete!"
echo "=========================================="
echo "🌐 Application URL: https://$APP_URL"
echo "📦 Resource Group: $RESOURCE_GROUP"
echo "🐳 Container Registry: $ACR_NAME"
echo "📱 Container App: $APP_NAME"
echo ""
echo "💡 View logs:"
echo "   az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "🗑️  Delete all resources:"
echo "   az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
