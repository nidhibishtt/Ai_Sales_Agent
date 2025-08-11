#!/bin/bash

# 🐳 AI Sales Agent - Docker Production Startup Script
# Usage: ./docker-start-prod.sh

echo "🐳 Starting AI Sales Agent in Docker (Production Mode)"
echo "======================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "💡 Copy .env.example to .env and add your API keys"
    exit 1
fi

# Create necessary directories
mkdir -p storage logs ssl

# Build and start all services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting all services (App + Redis + PostgreSQL + Nginx)..."
docker-compose up -d

# Wait for all services to start
echo "⏳ Waiting for all services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

if docker-compose ps | grep -q "Up.*healthy"; then
    echo "✅ All services are running successfully!"
    echo "🌐 Access the application at:"
    echo "   - http://localhost (via Nginx)"
    echo "   - http://localhost:5003 (direct access)"
    echo ""
    echo "📊 Service URLs:"
    echo "   - Application: http://localhost"
    echo "   - Redis: localhost:6379"
    echo "   - PostgreSQL: localhost:5432"
    echo ""
    echo "🔧 Management Commands:"
    echo "   - View logs: docker-compose logs -f"
    echo "   - Stop all: docker-compose down"
    echo "   - Scale app: docker-compose up -d --scale ai-sales-agent=3"
else
    echo "⚠️  Some services may not be fully ready yet"
    echo "📋 Check service status: docker-compose ps"
    echo "📋 Check logs: docker-compose logs"
fi

echo "======================================================="
