# Enhanced AI Sales Agent for Recruiting Agency

An intelligent AI-powered sales agent specifically designed for recruiting agencies, featuring premium LLM providers (GPT-4o, Gemini, Claude), advanced NER extraction, few-shot proposal generation, and production-ready deployment.

## 🚀 Key Features

### Premium AI Capabilities
- **Multi-LLM Support**: GPT-4o, Gemini 1.5 Flash, Claude 3.5 Sonnet with intelligent fallback
- **Advanced NER**: Hybrid LLM + rule-based entity extraction for recruiting inquiries
- **Few-Shot Learning**: Template-based professional proposal generation
- **Enhanced Memory**: LangChain-powered conversation state management

### Core Functionality
- Conversational client interaction with context awareness
- Automatic extraction of hiring requirements (roles, skills, urgency, budget)
- Intelligent service recommendations based on client needs
- Professional proposal generation with custom pricing
- Multi-session memory with analytics

### Deployment Ready
- Production Docker configurations
- Cloud deployment support (Google Cloud Run, Azure, AWS Lambda)
- Monitoring and logging integration
- Streamlined dependency management

## 📁 Project Structure

```
Project/
├── main.py                    # Enhanced AI Sales Agent (main entry point)
├── app.py                     # Streamlit web interface
├── api.py                     # FastAPI REST API
├── cli.py                     # Command-line interface
├── demo.py                    # Interactive demonstration
│
├── agents/                    # Multi-agent architecture
│   ├── base_agent.py         # Base agent functionality
│   ├── greeter_agent.py      # Initial client interactions
│   ├── extractor_agent.py    # Advanced NER extraction
│   ├── recommender_agent.py  # Service recommendations
│   ├── writer_agent.py       # Few-shot proposal generation
│   └── follow_up_agent.py    # Follow-up management
│
├── services/                  # Enhanced business logic
│   ├── llm_service.py        # Multi-LLM provider management
│   ├── advanced_ner.py       # Hybrid entity extraction
│   ├── proposal_generator.py # Few-shot proposal generation
│   ├── memory_service.py     # LangChain memory integration
│   └── recommendation_engine.py # Service recommendations
│
├── models/                    # Data schemas
│   └── schemas.py            # Pydantic models
│
├── utils/                     # Utility functions
│   └── helpers.py            # Common utilities
│
├── data/                      # Configuration
│   └── service_packages.py   # Service definitions
│
├── tests/                     # Test suite
│   └── test_sales_agent.py   # Comprehensive tests
│
└── docker/                   # Docker & deployment configurations
    ├── Dockerfile            # Standard Docker image
    ├── Dockerfile.production # Optimized production image  
    ├── docker-compose.prod.yml # Production stack
    ├── Procfile             # Heroku deployment
    └── README.md            # Deployment guide
```

## 🔧 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)
- API keys for LLM providers (OpenAI, Google AI, Anthropic)

### Installation
```bash
# Clone and setup
git clone <repository-url>
cd Project

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration
Add your API keys to `.env`:
```bash
# Premium LLM Providers
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Fallback Provider
GROQ_API_KEY=your_groq_api_key_here

# Application Settings
LOG_LEVEL=INFO
DEFAULT_DB_PATH=enhanced_sales_agent.db
```

### Usage Options

#### 1. Interactive Demo
```bash
python demo.py
```

#### 2. Streamlit Web Interface
```bash
streamlit run app.py
```

#### 3. Command Line Interface
```bash
python cli.py --interactive
```

#### 4. REST API
```bash
python api.py
# Access at http://localhost:8000/docs
```

#### 5. Direct Integration
```python
from main import EnhancedAISalesAgent

agent = EnhancedAISalesAgent()
session_id = agent.start_conversation("We need to hire developers")
response = agent.process_message(session_id, "Looking for 3 senior Python engineers")
print(response)
```

## 🏗️ Enhanced Architecture

### Multi-LLM Integration
- **Primary**: GPT-4o for complex reasoning
- **Speed**: Gemini 1.5 Flash for quick responses
- **Advanced**: Claude 3.5 Sonnet for nuanced conversations
- **Fallback**: Groq for high-speed inference

### Advanced NER Extraction
- Hybrid LLM + rule-based approach
- 50+ role pattern recognition
- Industry and location normalization
- Confidence scoring and validation

### Few-Shot Proposal Generation
- Template-based professional proposals
- Dynamic pricing calculations
- Reference number generation
- Custom formatting for different scenarios

### Enhanced Memory Management
- LangChain integration for sophisticated context handling
- SQLite persistence with conversation metrics
- Context-aware stage transitions
- Analytics and insights

## 🚀 Production Deployment

### Docker Deployment
```bash
# Basic deployment
docker build -f docker/Dockerfile -t enhanced-ai-sales-agent .
docker run -p 8000:8000 enhanced-ai-sales-agent

# Production deployment (recommended)
docker-compose -f docker/docker-compose.prod.yml up -d
```

See `docker/README.md` for comprehensive deployment guide.

### Cloud Deployment
The project includes configurations for:
- **Google Cloud Run**: `docker/docker-compose.prod.yml`
- **Azure Container Instances**: `docker/Dockerfile.production`
- **AWS Lambda**: Serverless architecture ready
- **Heroku**: `docker/Procfile` included

### Environment Variables
Production deployment requires:
```bash
# Required API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...

# Optional Settings
LOG_LEVEL=INFO
DEFAULT_DB_PATH=/data/sales_agent.db
MAX_SESSIONS=1000
```

## 📈 System Monitoring

The enhanced agent includes:
- Comprehensive logging with structured formats
- Performance metrics collection
- Error tracking and recovery
- Usage analytics and reporting
- Health check endpoints

## 🧪 Testing

```bash
# Run comprehensive tests
pytest tests/

# Test specific components
python -c "from main import EnhancedAISalesAgent; agent = EnhancedAISalesAgent(); print('✅ Agent initialized successfully')"
```

## 📚 API Documentation

### REST API Endpoints
- `POST /chat` - Process messages
- `GET /sessions/{session_id}/history` - Conversation history
- `GET /analytics` - Usage analytics
- `GET /health` - System status

### Python API
```python
from main import EnhancedAISalesAgent

# Initialize with custom settings
agent = EnhancedAISalesAgent(db_path="custom.db")

# Core methods
session_id = agent.start_conversation(message)
response = agent.process_message(session_id, message)
history = agent.get_conversation_history(session_id)
analytics = agent.get_analytics(days=30)
```

## 🔐 Security & Privacy

- API key encryption and secure storage
- Session-based access control
- Data anonymization options
- GDPR compliance features
- Audit logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the example usage in `demo.py`

---

**Enhanced AI Sales Agent** - Transforming recruiting agencies with intelligent automation and premium AI capabilities.
