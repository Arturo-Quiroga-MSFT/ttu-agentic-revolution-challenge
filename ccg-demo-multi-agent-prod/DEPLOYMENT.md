# Deployment Guide - Multi-Agent Timesheet Assistant (PRODUCTION)

## Overview

This guide covers deploying the production version of the Multi-Agent Timesheet Assistant to Azure Container Apps. The production version includes:

- ✅ Approval workflow
- 💾 Write capabilities to timesheet
- 📋 Complete audit logging
- 🔒 Compliance and security features

## Prerequisites

1. **Azure CLI** installed and configured
   ```bash
   az login
   az account set --subscription "your-subscription-name"
   ```

2. **Environment Configuration**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your Azure OpenAI credentials
   nano .env
   ```

3. **Required Azure OpenAI Resources**
   - Azure OpenAI endpoint
   - API key with access
   - GPT-4o or GPT-4.1 deployment

## Deployment Methods

### Option 1: Automated Deployment (Recommended)

Use the provided deployment script:

```bash
cd ccg-demo-multi-agent-prod
./deploy-aca.sh
```

This script will:
1. Create a resource group
2. Create Azure Container Registry (ACR)
3. Build and push container image to ACR
4. Create Container Apps environment
5. Deploy the application
6. Configure ingress and environment variables
7. Output the application URL

**Expected deployment time:** 5-10 minutes

### Option 2: Manual Deployment

#### Step 1: Set Variables
```bash
APP_NAME="ccg-multi-agent-prod"
RESOURCE_GROUP="rg-${APP_NAME}"
LOCATION="eastus"
ACR_NAME="acr${APP_NAME}$(date +%s)"
ENVIRONMENT_NAME="env-${APP_NAME}"
IMAGE_NAME="${APP_NAME}:latest"
```

#### Step 2: Create Resource Group
```bash
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION
```

#### Step 3: Create ACR
```bash
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
```

#### Step 4: Build Image
```bash
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME \
    --file Dockerfile \
    .
```

#### Step 5: Get ACR Credentials
```bash
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" -o tsv)
```

#### Step 6: Create Container Apps Environment
```bash
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

#### Step 7: Deploy Container App
```bash
# Load environment variables
source .env

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
    --max-replicas 3
```

#### Step 8: Get Application URL
```bash
az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv
```

## Post-Deployment

### Access the Application

Navigate to the URL provided after deployment:
```
https://your-app-name.azurecontainerapps.io
```

### Verify Functionality

1. **Analysis Tab**: Test missing time analysis
2. **Approval Workflow**: Approve/reject suggestions
3. **Audit Log**: Verify operations are logged
4. **Manual Entry**: Test direct write capability

### Monitor the Application

View logs:
```bash
az containerapp logs show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --follow
```

View metrics:
```bash
az monitor metrics list \
    --resource $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --resource-type Microsoft.App/containerApps
```

## Security Considerations

### Environment Variables

**Never commit `.env` file to version control.**

The following secrets are configured as environment variables:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL

For production, consider using Azure Key Vault:
```bash
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars \
        "AZURE_OPENAI_API_KEY=secretref:azure-openai-key"
```

### Audit Logging

All write operations are logged in `shared/audit_log.json` with:
- Timestamp
- User attribution
- Complete entry details
- Action type (approve/reject)

**Important:** Configure persistent storage for production:
```bash
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --storage-account-name yourstorage \
    --mount-path /app/shared
```

### Network Security

Restrict access using:
1. **IP Restrictions**: Allow only corporate IPs
2. **Azure AD Authentication**: Require Azure AD login
3. **Private Endpoints**: Deploy to VNet

## Scaling

The app is configured to scale:
- **Min replicas:** 1
- **Max replicas:** 3
- **CPU:** 1.0 cores
- **Memory:** 2.0 GB

Adjust scaling:
```bash
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 2 \
    --max-replicas 5
```

## Cost Optimization

### Resource Cleanup

Delete all resources when no longer needed:
```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

### Estimated Costs

- **Container Apps**: ~$50-100/month (1-3 replicas)
- **Container Registry**: ~$5/month (Basic tier)
- **Azure OpenAI**: Variable based on usage (~$0.01-0.10 per analysis)

**Total estimated cost:** $60-120/month

## Troubleshooting

### Container Won't Start

Check logs:
```bash
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 100
```

Common issues:
- Missing environment variables
- Invalid Azure OpenAI credentials
- Port configuration mismatch

### Application Errors

1. **Import errors**: Verify `requirements.txt` includes all dependencies
2. **Agent initialization fails**: Check Azure OpenAI endpoint and API key
3. **Write operations fail**: Verify file permissions in container

### Performance Issues

Monitor CPU/memory:
```bash
az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].resources"
```

Increase resources if needed:
```bash
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --cpu 2.0 \
    --memory 4.0Gi
```

## Continuous Deployment

### Update Application

Rebuild and redeploy:
```bash
# Build new image
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME \
    --file Dockerfile \
    .

# Update container app (pulls latest image)
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image "${ACR_SERVER}/${IMAGE_NAME}"
```

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]
    paths:
      - 'ccg-demo-multi-agent-prod/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and Push
        run: |
          az acr build \
            --registry ${{ secrets.ACR_NAME }} \
            --image ccg-multi-agent-prod:${{ github.sha }} \
            --file ccg-demo-multi-agent-prod/Dockerfile \
            ccg-demo-multi-agent-prod
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name ccg-multi-agent-prod \
            --resource-group ${{ secrets.RESOURCE_GROUP }} \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/ccg-multi-agent-prod:${{ github.sha }}
```

## Support

For issues or questions:
1. Check logs: `az containerapp logs show`
2. Review architecture: See `diagrams/architecture.md`
3. Test locally: `streamlit run multi_agent_streamlit.py`
4. Verify agents: Check `agents/` directory for agent configurations

## Next Steps

After successful deployment:
1. Configure user authentication (Azure AD)
2. Set up persistent storage for audit logs
3. Configure monitoring and alerts
4. Implement backup strategy for timesheet data
5. Document approval workflow for end users
