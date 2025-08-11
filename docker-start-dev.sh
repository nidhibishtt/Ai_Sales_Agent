#!/bin/bash

# 🐳 AI Sales Agent - Docker Development Startup Script
# Usage: ./docker-start-dev.sh

echo "🐳 Starting AI Sales Agent in Docker (Development Mode)"
echo "========================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "💡 Copy .env.example to .env and add your API keys"
    cp .env.example .env
    echo "✅ Created .env file - please add your GROQ_API_KEY"
    echo "📝 Edit .env file and then run this script again"
    exit 1
fi

# Create necessary directories
mkdir -p storage logs

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose -f docker-compose.dev.yml build

echo "🚀 Starting AI Sales Agent..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if application is running
if curl -s http://localhost:5003/api/system-status > /dev/null; then
    echo "✅ AI Sales Agent is running successfully!"
    echo "🌐 Access the application at: http://localhost:5003"
    echo "📊 View logs: docker-compose -f docker-compose.dev.yml logs -f"
    echo "⏹️  Stop: docker-compose -f docker-compose.dev.yml down"
else
    echo "❌ Application failed to start properly"
    echo "📋 Check logs: docker-compose -f docker-compose.dev.yml logs"
fi

echo "========================================================"
