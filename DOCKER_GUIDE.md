# 🐳 Docker Deployment Guide

## 🚀 Quick Docker Setup

### Prerequisites
- Docker Desktop installed
- Docker Compose available
- `.env` file with your API keys

### 🎯 Development Mode (Recommended for testing)
```bash
# Quick start
./docker-start-dev.sh

# Manual commands
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

### 🏢 Production Mode (Full stack)
```bash
# Quick start
./docker-start-prod.sh

# Manual commands
docker-compose build
docker-compose up -d
```

---

## 📋 What Gets Deployed

### 🔧 Development Stack (`docker-compose.dev.yml`)
- **AI Sales Agent** (port 5003)
- Live code reload
- Development logging
- Direct access

### 🏭 Production Stack (`docker-compose.yml`)
- **AI Sales Agent** (port 5003)
- **Redis Cache** (port 6379)
- **PostgreSQL Database** (port 5432)
- **Nginx Reverse Proxy** (port 80/443)
- Health checks
- Auto-restart
- Rate limiting

---

## 🌐 Access URLs

### Development Mode
- **Application:** http://localhost:5003
- **System Status:** http://localhost:5003/api/system-status

### Production Mode
- **Application:** http://localhost (via Nginx)
- **Direct Access:** http://localhost:5003
- **System Status:** http://localhost/api/system-status

---

## 🔧 Docker Commands Reference

### Build & Start
```bash
# Development
docker-compose -f docker-compose.dev.yml up --build -d

# Production
docker-compose up --build -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-sales-agent
```

### Stop Services
```bash
# Development
docker-compose -f docker-compose.dev.yml down

# Production
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Scale Application
```bash
# Run multiple instances
docker-compose up -d --scale ai-sales-agent=3
```

---

## 🔍 Health Checks

### Check Service Status
```bash
docker-compose ps
```

### Test Application Health
```bash
curl http://localhost:5003/api/system-status
```

### Check Logs for Issues
```bash
docker-compose logs ai-sales-agent
```

---

## 🗂️ Docker Files Overview

### Core Files
- `Dockerfile` - Main application container
- `docker-compose.yml` - Production stack
- `docker-compose.dev.yml` - Development stack
- `.dockerignore` - Files excluded from build

### Configuration
- `nginx.conf` - Reverse proxy configuration
- `docker-start-dev.sh` - Development startup script
- `docker-start-prod.sh` - Production startup script

---

## 🔐 Environment Variables

Required in `.env` file:
```bash
# Essential
GROQ_API_KEY=your_groq_key_here

# Optional (for enhanced features)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database (auto-configured in Docker)
DATABASE_URL=postgresql://ai_user:ai_secure_password_2024@postgres:5432/ai_sales_agent
REDIS_URL=redis://redis:6379
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
docker-compose down
lsof -ti:5003 | xargs kill -9
```

**2. Build failures:**
```bash
docker system prune -a
docker-compose build --no-cache
```

**3. Permission errors:**
```bash
sudo chown -R $(whoami) storage/ logs/
```

**4. Database connection issues:**
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Clean Reset
```bash
# Stop everything and clean up
docker-compose down -v
docker system prune -a
docker volume prune

# Restart fresh
./docker-start-dev.sh
```

---

## 📊 Monitoring

### View Real-time Logs
```bash
docker-compose logs -f --tail=100
```

### Check Resource Usage
```bash
docker stats
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it ai-postgres psql -U ai_user -d ai_sales_agent

# Connect to Redis
docker exec -it ai-redis redis-cli
```

---

## 🚀 Deployment Checklist

### Before Deployment
- [ ] `.env` file with API keys configured
- [ ] Docker and Docker Compose installed
- [ ] Ports 5003, 6379, 5432, 80 available
- [ ] Sufficient disk space (2GB+)

### After Deployment
- [ ] Application accessible at http://localhost:5003
- [ ] System status returns "operational"
- [ ] Test conversation works correctly
- [ ] Logs show no errors

### Production Readiness
- [ ] SSL certificates configured (in `ssl/` directory)
- [ ] Firewall rules configured
- [ ] Backup strategy for database
- [ ] Monitoring and alerting setup

---

## 🎯 Performance Tips

### Optimize for Production
1. **Enable Redis caching** (included in prod stack)
2. **Use PostgreSQL** instead of SQLite
3. **Configure Nginx caching** for static files
4. **Scale horizontally** with multiple app instances

### Resource Allocation
- **Development:** 2GB RAM, 1 CPU core
- **Production:** 4GB+ RAM, 2+ CPU cores
- **Database:** Additional 1GB RAM for PostgreSQL

---

**🎉 Your AI Sales Agent is now ready for Docker deployment!**
