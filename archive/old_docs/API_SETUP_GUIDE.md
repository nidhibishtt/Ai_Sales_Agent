# API Keys Setup Guide

## 🚀 Quick Setup for Premium LLM Providers

To get the best performance from the Enhanced AI Sales Agent, configure one or more premium LLM providers:

### 🥇 **Recommended: OpenAI GPT-4o** 
- **Best for**: Complex reasoning, fintech scenarios, accurate extraction
- **Cost**: ~$0.005 per 1K tokens (very affordable for typical usage)
- **Setup**: 
  1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
  2. Create account and add billing info
  3. Generate new API key
  4. Add to `.env`: `OPENAI_API_KEY=sk-...`

### 🥈 **Alternative: Google AI Gemini**
- **Best for**: Fast responses, good reasoning, Google ecosystem
- **Cost**: Free tier available, then pay-as-you-go
- **Setup**:
  1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
  2. Create/login to Google account
  3. Generate API key
  4. Add to `.env`: `GOOGLE_API_KEY=AI...`

### 🥉 **Alternative: Anthropic Claude**
- **Best for**: Advanced reasoning, safety, detailed responses
- **Cost**: Pay-as-you-go pricing
- **Setup**:
  1. Go to [Anthropic Console](https://console.anthropic.com/settings/keys)
  2. Create account and add billing
  3. Generate API key
  4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### 🆓 **Free Option: Groq**
- **Best for**: Testing, development, fast inference
- **Cost**: Completely free (14,400 tokens/minute)
- **Setup**:
  1. Go to [Groq Console](https://console.groq.com/keys)
  2. Create account (no billing required)
  3. Generate API key
  4. Add to `.env`: `GROQ_API_KEY=gsk_...`

## 🔧 Configuration

1. **Copy example file**: `cp .env.example .env`
2. **Add your keys** to `.env`
3. **Set provider priority** in `.env`: `LLM_PROVIDER=openai`
4. **Test the setup**: `python test_exact_case.py`

## 💡 Expected Results with Real API Keys

With OpenAI/Google/Anthropic configured, your fintech test should show:

```
✅ EXTRACTION VALIDATION:
   Industry (fintech): ✅ PASS - Got: 'fintech'
   Location (Mumbai): ✅ PASS - Got: 'Mumbai'  
   Roles (backend + UI/UX): ✅ PASS - Got: ['backend engineer', 'UI/UX designer']
   Urgency (true): ✅ PASS - Got: 'urgent'

📊 Extraction Score: 4/4 (100.0%)
```

## 🎯 Quick Test

After adding API keys, run:
```bash
python test_exact_case.py
```

Expected output with real LLM:
```
🤖 Agent Response: "Great! I understand you're a fintech startup in Mumbai looking to hire 2 backend engineers and a UI/UX designer urgently. For fintech companies with urgent hiring needs, I'd recommend our Tech Startup Hiring Pack..."
```

## 💰 Cost Estimate

For typical testing/development:
- **OpenAI GPT-4o**: ~$1-5/month for moderate usage
- **Google Gemini**: Free tier covers most testing
- **Anthropic Claude**: ~$2-10/month for moderate usage
- **Groq**: Completely free

Choose the provider that best fits your budget and requirements! 🚀
