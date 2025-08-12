# 🤖 AI Sales Agent for Recruiting Agency

**Enhanced Multi-Agent AI System for Recruitment Services**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%2B%20Llama%203.3--70B-orange.svg)](https://groq.com)
## note: Groq API with llama-3.3-70b-versatile was used for testing due to free access availability. The code is fully compatible with GPT-4, claude and gemini and can be switched by changing .env values and llm provider value.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key (free tier available)

### Installation & Run
```bash
# 1. Clone and setup
git clone <your-repo>
cd Project

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add your GROQ_API_KEY to .env file

# 5. Start the application
python3 main.py

# Alternative: Start using virtual environment directly
.venv/bin/python -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
```

🌐 **Access**: Open http://127.0.0.1:5003 in your browser

###  **Multiple Ways to Start the App:**

1. ** Docker (Recommended for Production):**
   ```bash
   # Development mode
   ./docker-start-dev.sh
   
   # Production mode (with Redis, PostgreSQL, Nginx)
   ./docker-start-prod.sh
   ```

2. **Quick Start Script (Local Development):**
   ```bash
   # macOS/Linux
   ./start_app.sh
   
   # Windows  
   start_app.bat
   ```

2. **Standard Method (Recommended):**
   ```bash
   python3 main.py
   ```

3. **Direct Flask Method (Alternative):**
   ```bash
   .venv/bin/python -c "from ui.flask_app import app, socketio; socketio.run(app, host='0.0.0.0', port=5003, debug=True)"
   ```

4. **Development Mode:**
   ```bash
   source .venv/bin/activate  # Activate virtual environment first
   python3 main.py
   ```

## 💬 How to Use

### Sample Conversations

**Scenario 1: Tech Startup Hiring**
```
User: "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."

Bot: → Extracts requirements → Shows service packages → Generates proposal
```

**Scenario 2: Package Inquiry**
```
User: "Show me your service packages for hiring developers"

Bot: → Displays available packages → Recommends based on needs
```

**Scenario 3: Direct Proposal**
```
User: "Can you prepare a proposal for the Tech Startup package?"

Bot: → Generates customized proposal → Provides next steps
```

##  Architecture

### Core Components

```
📁 PROJECT STRUCTURE
├── 🤖 agents/           # Specialized AI Agents
│   ├── greeter_agent.py      # Welcome & initial interaction
│   ├── extractor_agent.py    # NER & requirement extraction
│   ├── recommender_agent.py  # Service package recommendations
│   ├── writer_agent.py       # Proposal generation
│   ├── follow_up_agent.py    # Follow-up & scheduling
│   └── base_agent.py         # Agent orchestration & routing
├── 🧠 services/        # Business Logic Services
│   ├── llm_service.py        # LLM provider management (Groq/OpenAI/etc)
│   ├── advanced_ner.py       # Named Entity Recognition
│   ├── proposal_generator.py # Few-shot proposal generation
│   ├── recommendation_engine.py # Package recommendation logic
│   └── memory_service.py     # Conversation memory & context
├── 📊 models/          # Data Models
│   └── schemas.py            # Pydantic models for structured data
├── 🎨 ui/              # User Interface
│   ├── flask_app.py          # Flask web application
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, assets
├── 🗃️ data/           # Configuration & Data
│   └── packages.json         # Service package definitions
├── 🔧 utils/          # Utilities
│   └── helpers.py            # Common helper functions
└── 📝 Main Files
    ├── main.py               # Application entry point
    ├── requirements.txt      # Python dependencies
    ├── .env.example         # Environment variables template
    └── README.md           # This file
```

### Agent Flow
```
1.  GREETER → Welcome user, understand initial context
2.  EXTRACTOR → Extract hiring requirements (roles, location, urgency)
3.  RECOMMENDER → Suggest relevant service packages
4.  WRITER → Generate personalized proposals
5.  FOLLOW_UP → Schedule calls, next steps
```

##  Key Features

###  **Advanced AI Capabilities**
- **Multi-Agent Architecture**: 5 specialized agents for different conversation stages
- **Groq Llama 3.3-70B**: Latest high-performance language model
- **Few-Shot Learning**: Template-based proposal generation
- **Advanced NER**: Entity extraction for hiring requirements

###  **Business Logic**
- **Service Packages**: Pre-defined recruitment service tiers
- **Dynamic Pricing**: Context-aware price estimation
- **Timeline Estimation**: Urgency-based delivery timelines
- **Success Metrics**: Package success rates and guarantees

###  **Conversation Management**
- **Memory System**: Context preservation across messages
- **Smart Routing**: Intent-based agent selection
- **Error Handling**: Graceful fallbacks and error recovery
- **Analytics**: Conversation flow and performance metrics

##  Service Packages

The system offers 4 main service packages:

1. ** Tech Startup Hiring Pack** - For startups and tech companies
2. ** Volume Hiring Package** - For large-scale recruitment
3. ** Executive Search Premium** - For senior leadership roles
4. ** Quick Hire Express** - For urgent hiring needs

Each package includes customized features, timelines, and pricing based on client requirements.

##  Configuration

### Environment Variables (.env)
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional LLM Providers
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key

# App Configuration
FLASK_ENV=development
PORT=5003
```

### LLM Provider Priority
1. **Groq** (Primary - free tier available)
2. **OpenAI** (If key provided)
3. **Claude** (If key provided)
4. **Mock** (Fallback for testing)

##  Monitoring & Analytics

Access real-time system status at: `http://localhost:5003/api/system-status`

**Metrics include:**
- Agent performance
- Conversation success rates
- LLM response times
- Memory service status

## 🔧 Development

### Running Tests
```bash
# Run diagnostic tests
python3 -m pytest tests/

# Test specific scenario
python3 test_fintech_scenario.py
```

### Adding New Agents
1. Create agent class in `agents/`
2. Inherit from `BaseAgent`
3. Implement `process()` method
4. Register in `main.py`

### Adding New Service Packages
Edit `data/packages.json` to add new service offerings.

##  API Reference

### Main Endpoints
- `GET /` - Main chat interface
- `POST /api/chat` - Process chat messages
- `GET /api/system-status` - System health check
- `WebSocket /socket.io` - Real-time chat communication

##  UI Features

- **Real-time Chat**: WebSocket-powered instant messaging
- **Typing Indicators**: Show when AI is processing
- **Message History**: Persistent conversation view
- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Theme**: User preference support

##  System Requirements

- **Memory**: 2GB RAM minimum
- **Storage**: 1GB free space
- **Network**: Internet connection for LLM API calls
- **Browser**: Modern browser with WebSocket support

