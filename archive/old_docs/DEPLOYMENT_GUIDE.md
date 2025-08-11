# AI Sales Agent - Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Docker (Recommended for Development)

**Prerequisites:**
- Docker and Docker Compose installed
- OpenAI API key

**Steps:**
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd Project
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. Deploy with Docker Compose:
   ```bash
   cd deployment
   docker-compose up --build
   ```

4. Access the application:
   - **API**: http://localhost:8000
   - **Web UI**: http://localhost:8501
   - **API Docs**: http://localhost:8000/docs

### Option 2: Heroku (Fastest for Demos)

**Prerequisites:**
- Heroku account
- Heroku CLI installed
- Git

**Steps:**
1. Create Heroku app:
   ```bash
   heroku create your-ai-sales-agent
   ```

2. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   heroku config:set ENVIRONMENT=production
   ```

3. Deploy:
   ```bash
   git add .
   git commit -m "Deploy AI Sales Agent"
   git push heroku main
   ```

4. Scale and open:
   ```bash
   heroku ps:scale web=1
   heroku open
   ```

**Live in ~3 minutes!** 🎉

### Option 3: Google Cloud Run (Production Ready)

**Prerequisites:**
- Google Cloud account with billing enabled
- Google Cloud SDK installed
- OpenAI API key stored in Secret Manager

**Steps:**
1. Setup Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
   ```

2. Store your API key:
   ```bash
   echo -n "your_openai_api_key" | gcloud secrets create openai-api-key --data-file=-
   ```

3. Deploy with Cloud Build:
   ```bash
   gcloud builds submit --config=deployment/cloudbuild.yaml .
   ```

4. Get your service URLs:
   ```bash
   gcloud run services list
   ```

**Auto-scaling, fully managed, pay-per-use!** 💫

### Option 4: AWS Lambda (Serverless)

**Prerequisites:**
- AWS account
- AWS CLI configured
- Node.js (for Serverless Framework)
- OpenAI API key in AWS Secrets Manager

**Steps:**
1. Install Serverless Framework:
   ```bash
   npm install -g serverless
   ```

2. Store your API key in AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret --name ai-sales-agent/openai-api-key --secret-string "your_openai_api_key"
   ```

3. Deploy:
   ```bash
   cd deployment
   serverless deploy
   ```

4. Get your API Gateway endpoint:
   ```bash
   serverless info
   ```

**Serverless, pay-per-request, infinite scale!** ⚡

---

## 🛠 Environment Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=sk-...              # Your OpenAI API key
ENVIRONMENT=production             # Environment (development/production)
LOG_LEVEL=INFO                     # Logging level
```

### Optional Environment Variables
```bash
DATABASE_URL=sqlite:///./data/ai_sales_agent.db  # Database connection
LANGCHAIN_TRACING_V2=true          # Enable LangSmith tracing
LANGCHAIN_API_KEY=ls__...          # LangSmith API key
LANGCHAIN_PROJECT=ai-sales-agent   # LangSmith project name
```

---

## 🔧 Platform-Specific Setup

### Docker Production Setup

**docker-compose.prod.yml:**
```yaml
version: '3.8'
services:
  api:
    build: 
      context: ..
      dockerfile: deployment/Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    restart: unless-stopped
```

**Commands:**
```bash
# Build and run production
docker-compose -f docker-compose.prod.yml up -d

# View logs  
docker-compose logs -f

# Scale services
docker-compose up --scale api=3
```

### Google Cloud Run Advanced

**Custom Domain Setup:**
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service ai-sales-agent \
  --domain api.yourdomain.com \
  --region us-central1

# Setup SSL (automatic)
# DNS configuration required
```

**Monitoring Setup:**
```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create uptime checks
gcloud alpha monitoring uptime create \
  --display-name="AI Sales Agent API" \
  --http-check-path="/health"
```

### AWS Lambda Production

**Custom Domain:**
```yaml
# In serverless.yml
plugins:
  - serverless-domain-manager

custom:
  customDomain:
    domainName: api.yourdomain.com
    stage: production
    certificateName: '*.yourdomain.com'
```

**Deployment:**
```bash
# Create domain
serverless create_domain

# Deploy with custom domain  
serverless deploy --stage production
```

### Heroku Production

**Add-ons for Production:**
```bash
# PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev

# Redis for caching
heroku addons:create heroku-redis:hobby-dev

# Log aggregation
heroku addons:create papertrail:choklad

# Monitoring
heroku addons:create newrelic:wayne
```

**Configuration:**
```bash
# Set production config
heroku config:set NODE_ENV=production
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO

# Scale dynos
heroku ps:scale web=2
heroku ps:type web=standard-1x
```

---

## 📊 Monitoring & Observability

### Health Checks

All deployments include health check endpoints:
- **API**: `GET /health`
- **Response**: `{"status": "healthy", "services": {...}}`

### Logging Setup

**Structured Logging:**
```python
import logging
import json

# Configure JSON logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Log structured data
logger.info(json.dumps({
    "event": "conversation_processed",
    "session_id": "abc123",
    "duration_ms": 1500,
    "tokens_used": 150
}))
```

### Metrics Collection

**Key Metrics to Track:**
- Response time (p50, p95, p99)
- Error rate by endpoint
- Token usage per conversation
- Conversation completion rate
- Session duration

**Sample Monitoring Dashboard:**
- Request volume over time
- Error rate trends
- Response time percentiles
- OpenAI API costs
- User engagement metrics

---

## 🔒 Security Best Practices

### Production Security Checklist

- [ ] **Environment Variables**: All secrets in environment variables, never in code
- [ ] **HTTPS Only**: Force SSL/TLS for all communication
- [ ] **API Rate Limiting**: Implement request rate limiting
- [ ] **Input Validation**: Sanitize all user inputs
- [ ] **Error Handling**: Don't expose internal errors to users
- [ ] **Dependency Updates**: Keep all dependencies updated
- [ ] **Access Logging**: Log all API access for auditing
- [ ] **Resource Limits**: Set memory and CPU limits
- [ ] **Network Security**: Use VPC/private networks where possible
- [ ] **Database Security**: Use connection pooling and encryption

### API Security Headers

**Required Headers:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY  
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/conversations/{session_id}/messages")
@limiter.limit("30/minute")  # 30 requests per minute
async def process_message(request: Request, session_id: str, message: MessageRequest):
    # ... implementation
```

---

## 🧪 Testing Deployments

### Automated Testing

**Health Check Script:**
```bash
#!/bin/bash
# test_deployment.sh

API_URL=${1:-"http://localhost:8000"}

echo "Testing deployment at: $API_URL"

# Health check
echo "1. Health check..."
curl -f "$API_URL/health" || exit 1

# Start conversation
echo "2. Starting conversation..."
SESSION_ID=$(curl -s -X POST "$API_URL/api/conversations" | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# Send test message
echo "3. Sending test message..."
RESPONSE=$(curl -s -X POST "$API_URL/api/conversations/$SESSION_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, we need help with hiring"}')

echo "Response: $RESPONSE"

echo "✅ Deployment test completed successfully!"
```

**Run Tests:**
```bash
# Local testing
./test_deployment.sh http://localhost:8000

# Production testing  
./test_deployment.sh https://your-deployed-app.com
```

### Load Testing

**Simple Load Test:**
```python
import asyncio
import aiohttp
import time

async def test_conversation(session, base_url):
    """Test a single conversation flow"""
    try:
        # Start conversation
        async with session.post(f"{base_url}/api/conversations") as resp:
            data = await resp.json()
            session_id = data["session_id"]
        
        # Send message
        message_data = {"message": "We need to hire 5 developers"}
        async with session.post(
            f"{base_url}/api/conversations/{session_id}/messages",
            json=message_data
        ) as resp:
            response = await resp.json()
            return len(response["response"])
            
    except Exception as e:
        print(f"Error: {e}")
        return 0

async def load_test(base_url, concurrent_users=10, duration_seconds=60):
    """Run load test"""
    print(f"Load testing {base_url} with {concurrent_users} users for {duration_seconds}s")
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = []
        
        while time.time() - start_time < duration_seconds:
            if len(tasks) < concurrent_users:
                task = asyncio.create_task(test_conversation(session, base_url))
                tasks.append(task)
            
            # Clean completed tasks
            tasks = [task for task in tasks if not task.done()]
            await asyncio.sleep(0.1)
        
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# Run load test
# asyncio.run(load_test("https://your-app.com", concurrent_users=5, duration_seconds=30))
```

---

## 💰 Cost Optimization

### Cloud Cost Estimates

**Monthly Costs by Usage Level:**

| Platform | Low (100 conv/month) | Medium (1K conv/month) | High (10K conv/month) |
|----------|---------------------|----------------------|---------------------|
| Heroku   | $7 (hobby)          | $25-50              | $100-200            |
| GCP Run  | $5-15               | $25-50              | $100-200            |
| AWS Lambda| $3-10              | $15-30              | $75-150             |
| Digital Ocean | $5 (droplet)   | $10-20              | $40-80              |

*Excludes OpenAI API costs (~$0.002-0.02 per conversation)*

### Cost Optimization Tips

1. **Choose Right Instance Size**: Start small, monitor, scale as needed
2. **Use Caching**: Cache frequent responses to reduce LLM calls
3. **Optimize Prompts**: Shorter prompts = lower token costs
4. **Request Batching**: Process multiple messages together when possible
5. **Auto-scaling**: Set appropriate min/max instances
6. **Region Selection**: Choose regions closest to users
7. **Reserved Capacity**: Use reserved instances for predictable loads

---

## 🚨 Troubleshooting

### Common Issues & Solutions

**"Service Unavailable" Errors:**
```bash
# Check logs
docker-compose logs api
heroku logs --tail
gcloud logs read --service=ai-sales-agent
aws logs tail /aws/lambda/ai-sales-agent
```

**OpenAI API Failures:**
- Verify API key is correct
- Check account billing status  
- Monitor rate limits
- Implement retry logic with exponential backoff

**High Response Times:**
- Check database connection pooling
- Monitor memory usage
- Scale horizontally (add instances)
- Optimize prompt sizes

**Memory Issues:**
- Increase container memory limits
- Implement conversation cleanup
- Use streaming for large responses
- Monitor for memory leaks

### Debugging Commands

**Docker:**
```bash
# Check container status
docker ps -a

# Access container shell
docker exec -it <container-id> bash

# View resource usage
docker stats
```

**Heroku:**
```bash
# Check dyno status
heroku ps

# Scale up
heroku ps:scale web=2

# Run one-off command
heroku run python -c "from main import AISalesAgent; print(AISalesAgent().health_check())"
```

**Google Cloud:**
```bash
# Check service status
gcloud run services describe ai-sales-agent --region=us-central1

# View logs
gcloud logs tail "resource.type=cloud_run_revision"

# Debug deployment
gcloud run revisions list
```

---

## 📈 Scaling Guidelines

### Horizontal Scaling

**Auto-scaling Configuration:**

**Docker Swarm:**
```yaml
services:
  api:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

**Kubernetes:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-sales-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-sales-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Performance Monitoring

**Key Performance Indicators:**
- **Response Time**: < 2s for 95% of requests
- **Availability**: > 99.5% uptime
- **Error Rate**: < 1% of requests
- **Throughput**: Requests per second capacity
- **Resource Utilization**: CPU < 80%, Memory < 85%

### Database Scaling

**From SQLite to PostgreSQL:**
```python
# Update DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost/ai_sales_agent

# Migration script
python scripts/migrate_sqlite_to_postgres.py
```

**Redis Caching:**
```python
# Add Redis for session caching
REDIS_URL=redis://localhost:6379/0

# Implement caching layer
from redis import Redis
cache = Redis.from_url(os.getenv('REDIS_URL'))
```

---

That completes our comprehensive AI Sales Agent project! 🎉

## 📋 Final Deliverables Summary

✅ **1. End-to-end AI Sales Agent System**
- Multi-agent architecture with specialized roles
- LLM integration (OpenAI GPT-4)
- Memory management and persistence
- NER extraction and service recommendations
- Proposal generation and follow-up capabilities

✅ **2. Complete Documentation**
- Detailed README with setup instructions
- Architecture documentation
- API reference with examples
- Testing guide and troubleshooting

✅ **3. Sample Conversations & Demo**
- 3 detailed conversation scenarios
- Interactive demo script
- Real-world use case examples
- Performance analytics

✅ **4. Bonus: Cloud Deployment Configurations**
- Docker containerization
- Google Cloud Platform (Cloud Run)
- Amazon Web Services (Lambda) 
- Microsoft Azure configurations
- Heroku quick-deploy
- Production-ready monitoring and security

The AI Sales Agent is now ready for production deployment with comprehensive documentation, testing, and multiple deployment options! 🚀
