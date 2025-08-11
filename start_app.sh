#!/bin/bash

# 🚀 AI Sales Agent - Quick Start Script
# Usage: ./start_app.sh

echo "🤖 Starting AI Sales Agent..."
echo "================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run setup first: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "💡 Copy .env.example to .env and add your GROQ_API_KEY"
    cp .env.example .env
    echo "✅ Created .env file - please add your GROQ_API_KEY"
fi

# Start the application using the direct Flask method
echo "🚀 Starting Flask application..."
echo "🌐 Access at: http://127.0.0.1:5003"
echo "⏹️  Press Ctrl+C to stop"
echo "================================"

./.venv/bin/python -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
