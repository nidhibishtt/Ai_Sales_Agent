@echo off
REM 🤖 AI Sales Agent - Windows Quick Start
echo 🤖 Starting AI Sales Agent...
echo ================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo 💡 Run setup first: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 💡 Copy .env.example to .env and add your GROQ_API_KEY
    copy .env.example .env
    echo ✅ Created .env file - please add your GROQ_API_KEY
)

REM Start the application using the direct Flask method
echo 🚀 Starting Flask application...
echo 🌐 Access at: http://127.0.0.1:5003
echo ⏹️  Press Ctrl+C to stop
echo ================================

.venv\Scripts\python.exe -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
pause
