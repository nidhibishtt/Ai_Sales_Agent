# Docker Deployment for Enhanced AI Sales Agent

This directory contains all Docker and deployment-related files for the Enhanced AI Sales Agent.

## 📁 Files Overview

### Docker Files
- **`Dockerfile`** - Standard Docker image for development and basic deployment
- **`Dockerfile.production`** - Optimized production Docker image with multi-stage build
- **`docker-compose.prod.yml`** - Docker Compose configuration for production deployment

### Deployment Files
- **`Procfile`** - Heroku deployment configuration

## 🚀 Deployment Options

### 1. Basic Docker Deployment
```bash
# Build the image
docker build -f docker/Dockerfile -t ai-sales-agent .

# Run the container
docker run -p 8000:8000 --env-file .env ai-sales-agent
```

### 2. Production Docker Deployment
```bash
# Build production image (multi-stage, optimized)
docker build -f docker/Dockerfile.production -t ai-sales-agent:prod .

# Run production container
docker run -p 8000:8000 --env-file .env ai-sales-agent:prod
```

### 3. Docker Compose (Recommended for Production)
```bash
# Start the complete stack
docker-compose -f docker/docker-compose.prod.yml up -d

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f

# Stop the stack
docker-compose -f docker/docker-compose.prod.yml down
```

### 4. Heroku Deployment
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-ai-sales-agent

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key_here

# Deploy
git push heroku main
```

## 🔧 Configuration

### Environment Variables
Make sure your `.env` file contains:
```bash
# Required API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...

# Optional Settings
LOG_LEVEL=INFO
LLM_PROVIDER=openai
```

### Port Configuration
- **Development**: Port 8000 (FastAPI)
- **Streamlit**: Port 8501
- **Production**: Configurable via `PORT` environment variable

## 🌐 Cloud Deployment Options

### Google Cloud Run
```bash
# Build and push to Google Container Registry
docker build -f docker/Dockerfile.production -t gcr.io/PROJECT_ID/ai-sales-agent .
docker push gcr.io/PROJECT_ID/ai-sales-agent

# Deploy to Cloud Run
gcloud run deploy ai-sales-agent \
  --image gcr.io/PROJECT_ID/ai-sales-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances
```bash
# Create resource group
az group create --name ai-sales-agent-rg --location eastus

# Deploy container
az container create \
  --resource-group ai-sales-agent-rg \
  --name ai-sales-agent \
  --image your-registry/ai-sales-agent:prod \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your_key
```

### AWS Lambda (Serverless)
Use the `Dockerfile.production` with AWS Lambda Container Images:
```bash
# Build for Lambda
docker build -f docker/Dockerfile.production -t ai-sales-agent:lambda .

# Push to ECR and deploy via AWS Console or CLI
```

## 📊 Health Checks

All Docker configurations include health checks:
- **Endpoint**: `GET /health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## 🔍 Monitoring

Production deployments include:
- Application logs
- Performance metrics
- Error tracking
- Health monitoring

## 🚨 Troubleshooting

### Common Issues:
1. **Port conflicts**: Change port mapping in docker run commands
2. **Environment variables**: Ensure `.env` file is properly configured
3. **API quotas**: Check LLM provider billing and quotas
4. **Memory limits**: Increase container memory for production loads

### Debug Commands:
```bash
# Check container logs
docker logs <container_id>

# Shell into container
docker exec -it <container_id> /bin/bash

# Check health endpoint
curl http://localhost:8000/health
```

## 📝 Notes

- The production Dockerfile uses multi-stage builds for smaller images
- All configurations support hot-reloading for development
- Production deployments include optimized caching and compression
- Health checks ensure container reliability

For more deployment options, see the main project documentation.
