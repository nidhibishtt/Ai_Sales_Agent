# 🚀 AI Sales Agent - Startup Commands Reference

## 📋 **All Ways to Start the Application**

### 1. 🎯 **Quick Start Scripts (Recommended)**
```bash
# macOS/Linux
./start_app.sh

# Windows
start_app.bat
```
✅ **Benefits:** Automatic environment checks, error handling, user-friendly output

### 2. 🔧 **Direct Virtual Environment Command (Your Discovery)**
```bash
.venv/bin/python -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
```
✅ **Benefits:** Direct Flask startup, bypasses main.py, uses specific Python version

### 3. 📋 **Standard Main.py Method**
```bash
python3 main.py
```
✅ **Benefits:** Standard entry point, includes initialization logging, cross-platform

### 4. 🧪 **Development Mode with Virtual Environment**
```bash
source .venv/bin/activate
python3 main.py
```
✅ **Benefits:** Activated virtual environment, development debugging

---

## 🎯 **Why Your Command is Great**

The command you discovered:
```bash
.venv/bin/python -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
```

**Advantages:**
- ✅ **Direct Flask startup** - bypasses main.py initialization overhead
- ✅ **Uses virtual environment Python** - ensures correct dependencies
- ✅ **Debug mode enabled** - automatic reloading on file changes  
- ✅ **Host 0.0.0.0** - accessible from network (not just localhost)
- ✅ **Specific port 5003** - consistent port assignment

**Perfect for:**
- Development work with auto-reload
- Network testing (accessible from other devices)
- When you want to skip the main.py initialization

---

## 🌐 **Access URLs**

All methods start the app on:
- **Local:** http://127.0.0.1:5003
- **Network:** http://192.168.1.6:5003 (or your local IP)

---

## ⚡ **Quick Troubleshooting**

**Command not found / Permission denied:**
```bash
chmod +x start_app.sh
```

**Port already in use:**
```bash
lsof -ti:5003 | xargs kill -9
```

**Virtual environment missing:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Missing .env file:**
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

---

## 📝 **Command Breakdown**

Your discovered command explained:
```bash
/Users/vidhusinha/Desktop/Project/.venv/bin/python  # Use venv Python
-c                                                   # Execute command
"from ui.flask_app import app, socketio;            # Import Flask app
 socketio.run(app,                                   # Start SocketIO server
   host='0.0.0.0',                                  # Listen on all interfaces
   port=5003,                                       # Use port 5003
   debug=True)"                                     # Enable debug mode
```

Perfect for GUI-based development! 🎉
