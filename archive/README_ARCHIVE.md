# 📁 Archive Contents

This folder contains files that were moved during project cleanup on August 11, 2025.

## 📋 What's Archived

### 🧪 `/archive/old_tests/`
**Test files and demos that are no longer actively used:**
- `test_*.py` - Various test scenarios and unit tests
- `demo*.py` - Demo scripts and examples
- `simple_demo.py` - Simple demo implementation
- `quick_test.py` - Diagnostic test script

### 📚 `/archive/old_docs/`
**Documentation files that are outdated or replaced:**
- `API_SETUP_GUIDE.md` - API setup instructions
- `DEEPSEEK_SETUP.md` - DeepSeek model setup
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `GROQ_SETUP.md` - Groq API setup
- `HOW_TO_RUN.md` - Old running instructions
- `MODEL_UPDATE_SUCCESS.md` - Model update documentation
- `PROJECT_AUDIT.md` - Project audit results
- `REQUIREMENTS_COVERAGE.md` - Requirements coverage analysis
- `sample_conversations.md` - Sample conversation examples

### 🤖 `/archive/broken_agents/`
**Agent files that had issues or were replaced:**
- `greeter_agent_broken.py` - Broken version of greeter agent
- `greeter_agent_fixed.py` - Fixed version (now integrated)

### 🚀 `/archive/` (Root Level)
**Deployment and alternative entry points:**
- `docker/` - Docker configuration files
- `deployment/` - Deployment scripts and configs
- `app.py` - Alternative Flask app entry point
- `cli.py` - Command line interface
- `api.py` - API-only entry point
- `launch_ui.py` - UI launcher script
- `docker-compose.prod.yml` - Production Docker compose
- `Dockerfile.prod` - Production Dockerfile
- `requirements.prod.txt` - Production requirements
- `.pytest_cache/` - Pytest cache files
- `sales_agent.log` - Old log files

## 🔄 Why These Were Archived

1. **Reduce Complexity**: Keep only essential, working files in main directory
2. **Eliminate Duplicates**: Multiple entry points and test files were confusing
3. **Focus on Core**: Maintain focus on the working Flask application
4. **Preserve History**: Keep old files for reference without cluttering

## 📝 Current Clean Structure

After cleanup, the main project contains only:
- ✅ **Working agents** (5 core agents)
- ✅ **Core services** (LLM, NER, proposals, etc.)
- ✅ **Main entry point** (`main.py`)
- ✅ **UI system** (Flask app with templates)
- ✅ **Essential configs** (.env, requirements.txt)
- ✅ **Clean documentation** (README_CLEAN.md)

## 🔙 Restoring Files

If you need any archived file back in the main project:
```bash
# Example: Restore a test file
cp archive/old_tests/test_fintech_scenario.py ./

# Example: Restore Docker setup
cp -r archive/docker/ ./
```

## 🗑️ Safe to Delete

These archived files can be safely deleted if you're confident you won't need them:
- Most test files (unless you want to run specific tests)
- Old documentation (replaced by README_CLEAN.md)
- Broken agent versions
- Old deployment configs (unless deploying to production)

---
*Archive created: August 11, 2025*
