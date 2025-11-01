#!/bin/bash
# Deploy CCG Multi-Agent Time & Expense System to Azure Container Apps
# This script builds the image in ACR and deploys to a new ACA environment

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="rg-ccg-multiagent"
LOCATION="eastus"
ACR_NAME="aqr2d2agentframeworkacr007"
ACA_ENV_NAME="ccg-multiagent-env"
ACA_APP_NAME="ccg-multiagent-app"
IMAGE_NAME="ccg-multiagent-streamlit"
IMAGE_TAG="latest"

echo "======================================"
echo "CCG Multi-Agent Deployment to Azure"
echo "======================================"
echo ""

# Check if logged in to Azure
echo "📋 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Logged in to Azure"
echo "   Subscription: $SUBSCRIPTION_ID"
echo ""

# Create resource group if it doesn't exist
echo "📦 Creating resource group: $RESOURCE_GROUP"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo "✅ Resource group ready"
echo ""

# Get ACR login server
echo "🔐 Getting ACR details..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo "✅ ACR Login Server: $ACR_LOGIN_SERVER"
echo ""

# Build image in ACR (no local Docker required)
echo "🏗️  Building container image in ACR..."
echo "   This may take a few minutes..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$IMAGE_TAG \
    --file Dockerfile \
    .

echo "✅ Image built successfully: $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"
echo ""

# Create Container Apps environment
echo "🌐 Creating Azure Container Apps environment..."
az containerapp env create \
    --name $ACA_ENV_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo "✅ Container Apps environment created"
echo ""

# Get Azure OpenAI configuration from local .env or prompt user
echo "🔑 Setting up environment variables..."
if [ -f .env ]; then
    echo "   Loading from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Prompt for required values if not in .env
if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    read -p "Enter Azure OpenAI Endpoint: " AZURE_OPENAI_ENDPOINT
fi

if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    read -sp "Enter Azure OpenAI API Key: " AZURE_OPENAI_API_KEY
    echo ""
fi

if [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ] && [ -z "$AZURE_OPENAI_CHAT_DEPLOYMENT_NAME" ]; then
    read -p "Enter Azure OpenAI Deployment Name: " AZURE_OPENAI_DEPLOYMENT_NAME
fi

# Use CHAT_DEPLOYMENT_NAME if DEPLOYMENT_NAME not set
if [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
    AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
fi

echo "✅ Environment variables configured"
echo ""

# Create Container App with ACR image
echo "🚀 Deploying Container App..."
az containerapp create \
    --name $ACA_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ACA_ENV_NAME \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-identity system \
    --target-port 8501 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 1.0 \
    --memory 2Gi \
    --env-vars \
        AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
        AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
    --output none

echo "✅ Container App deployed successfully"
echo ""

# Assign ACR pull permission to the Container App's managed identity
echo "🔐 Configuring ACR access..."
ACA_IDENTITY=$(az containerapp show \
    --name $ACA_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query identity.principalId -o tsv)

ACR_ID=$(az acr show --name $ACR_NAME --query id -o tsv)

az role assignment create \
    --assignee $ACA_IDENTITY \
    --role AcrPull \
    --scope $ACR_ID \
    --output none

echo "✅ ACR access configured"
echo ""

# Get the app URL
APP_URL=$(az containerapp show \
    --name $ACA_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "======================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================"
echo ""
echo "🌐 Application URL: https://$APP_URL"
echo ""
echo "📊 View logs:"
echo "   az containerapp logs show -n $ACA_APP_NAME -g $RESOURCE_GROUP --follow"
echo ""
echo "🔧 Update app:"
echo "   ./deploy-aca.sh"
echo ""
echo "🗑️  Delete resources:"
echo "   az group delete -n $RESOURCE_GROUP --yes --no-wait"
echo ""
