# Azure Container Apps Deployment Guide

## Overview
This guide explains how to deploy the CCG Multi-Agent Time & Expense System to Azure Container Apps (ACA) using Azure Container Registry (ACR) for building container images.

## Prerequisites

1. **Azure CLI** installed and logged in:
   ```bash
   az login
   ```

2. **Azure Subscription** with permissions to:
   - Create resource groups
   - Create Container Apps and environments
   - Build images in ACR (aqr2d2agentframeworkacr007)
   - Assign roles

3. **Azure OpenAI Service** with:
   - Endpoint URL
   - API Key
   - Deployment name (GPT-4 or GPT-4o recommended)

## Deployment Steps

### 1. Navigate to the multi-agent directory
```bash
cd /Users/arturoquiroga/TTU-AGENTIC-REVOLUTION-CHALLENGE/ccg-demo-multi-agent
```

### 2. Ensure .env file exists with your Azure OpenAI credentials
Create or update `.env` file:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
```

### 3. Run the deployment script
```bash
./deploy-aca.sh
```

The script will:
- ✅ Create a new resource group (`rg-ccg-multiagent`)
- ✅ Build the container image in ACR (no local Docker needed)
- ✅ Create a new Container Apps environment
- ✅ Deploy the application with auto-scaling (1-3 replicas)
- ✅ Configure ACR pull permissions
- ✅ Set up Azure OpenAI environment variables
- ✅ Provide the public URL

### 4. Access your application
After successful deployment, the script will display:
```
🌐 Application URL: https://ccg-multiagent-app.xxx.azurecontainerapps.io
```

## Configuration

### Resource Settings
The deployment creates resources in **eastus** with:
- **CPU**: 1.0 cores
- **Memory**: 2 GB
- **Replicas**: 1-3 (auto-scaling)
- **Port**: 8501 (Streamlit default)
- **Ingress**: External (publicly accessible)

### Environment Variables
The following are automatically configured:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`

## Updating the Application

To deploy updates:
```bash
./deploy-aca.sh
```

The script will rebuild the image and update the Container App.

## Monitoring

### View logs in real-time
```bash
az containerapp logs show \
  -n ccg-multiagent-app \
  -g rg-ccg-multiagent \
  --follow
```

### View app details
```bash
az containerapp show \
  -n ccg-multiagent-app \
  -g rg-ccg-multiagent
```

### Check replicas
```bash
az containerapp replica list \
  -n ccg-multiagent-app \
  -g rg-ccg-multiagent
```

## Scaling

### Manual scaling
```bash
az containerapp update \
  -n ccg-multiagent-app \
  -g rg-ccg-multiagent \
  --min-replicas 2 \
  --max-replicas 5
```

### Auto-scaling rules
The app automatically scales between 1-3 replicas based on:
- HTTP request load
- CPU utilization
- Memory pressure

## Troubleshooting

### App not starting
1. Check logs: `az containerapp logs show -n ccg-multiagent-app -g rg-ccg-multiagent --follow`
2. Verify environment variables are set correctly
3. Ensure ACR pull permissions are configured

### Can't access the app
1. Verify ingress is enabled: `az containerapp show -n ccg-multiagent-app -g rg-ccg-multiagent --query properties.configuration.ingress`
2. Check if replicas are running: `az containerapp replica list -n ccg-multiagent-app -g rg-ccg-multiagent`

### Image build fails
1. Verify ACR exists: `az acr show -n aqr2d2agentframeworkacr007`
2. Check ACR permissions: `az acr check-health -n aqr2d2agentframeworkacr007`
3. Review build logs in the Azure Portal

## Cost Management

### View costs
```bash
az consumption usage list \
  --resource-group rg-ccg-multiagent \
  --start-date $(date -u -d '30 days ago' '+%Y-%m-%dT%H:%M:%SZ') \
  --end-date $(date -u '+%Y-%m-%dT%H:%M:%SZ')
```

### Stop the app (0 replicas)
```bash
az containerapp update \
  -n ccg-multiagent-app \
  -g rg-ccg-multiagent \
  --min-replicas 0 \
  --max-replicas 0
```

### Delete all resources
```bash
az group delete -n rg-ccg-multiagent --yes --no-wait
```

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────┐
│  Azure Container Apps               │
│  ┌───────────────────────────────┐  │
│  │  Multi-Agent Streamlit UI     │  │
│  │  - Orchestrator               │  │
│  │  - Calendar Agent             │  │
│  │  - Timesheet Agent            │  │
│  │  - Suggestion Agent           │  │
│  │  - Revenue Agent              │  │
│  └─────────────┬─────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Azure OpenAI Service               │
│  - GPT-4 / GPT-4o                   │
│  - Reasoning & Analysis             │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Sample Data (JSON)                 │
│  - calendar_sample.json             │
│  - timesheet_sample.json            │
└─────────────────────────────────────┘
```

## Security

- ✅ HTTPS enforced for all traffic
- ✅ Managed identity for ACR access
- ✅ Secrets stored as environment variables
- ✅ Network isolation via Container Apps environment
- ✅ No public exposure of source code or credentials

## Support

For issues or questions:
1. Check Azure Container Apps documentation: https://learn.microsoft.com/azure/container-apps/
2. Review deployment logs
3. Contact the development team

---

**Last Updated**: November 1, 2025
