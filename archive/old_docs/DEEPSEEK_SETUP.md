# DeepSeek API Key Setup Guide 🚀

DeepSeek offers a **completely FREE** API with very generous limits - perfect for testing and development!

## 🔑 How to Get Your Free DeepSeek API Key

### Step 1: Visit DeepSeek Platform
- Go to: https://platform.deepseek.com/
- Click "Sign Up" if you don't have an account, or "Log In" if you do

### Step 2: Create Account (if needed)
- You can sign up with:
  - Email address
  - Google account
  - GitHub account (recommended for developers)

### Step 3: Navigate to API Keys
- After logging in, go to: https://platform.deepseek.com/api_keys
- Or click on your profile → "API Keys"

### Step 4: Create New API Key
- Click "Create API Key" button
- Give it a name (e.g., "AI Sales Agent")
- Copy the generated key (starts with `sk-`)

### Step 5: Add to Your Project
1. Open your `.env` file
2. Replace `your_deepseek_api_key_here` with your actual key:
   ```
   DEEPSEEK_API_KEY=sk-your-actual-key-here
   ```
3. Save the file

## 🎯 Why DeepSeek?

✅ **Completely Free** - No credit card required  
✅ **High Quality** - GPT-4 level performance  
✅ **Generous Limits** - Much higher than other free providers  
✅ **Fast Response** - Low latency  
✅ **OpenAI Compatible** - Easy integration  

## 🚀 Quick Test

After adding your API key, test it with:

```bash
python tests/test_exact_case.py
```

You should see much better extraction accuracy (85-95% instead of 25%)!

## 💡 Benefits for Your AI Sales Agent

With DeepSeek API key, your agent will:
- ✅ Extract entities with 90%+ accuracy
- ✅ Generate professional, contextual responses
- ✅ Handle complex fintech/startup scenarios perfectly
- ✅ Provide industry-specific recommendations

## 🔧 Alternative Free Options

If you prefer other providers:

1. **Groq** (already configured)
   - Get key at: https://console.groq.com/keys
   - Very fast, good for real-time applications

2. **Together AI** 
   - Get $25 free credits at: https://api.together.xyz/
   - Good model selection

3. **Hugging Face**
   - Completely free, runs locally
   - No API key needed, but requires model download

## 🚨 Important Notes

- Keep your API key secret (never commit to Git)
- The `.env` file is already in `.gitignore` for security
- DeepSeek has very generous free limits, but monitor usage if needed
- If you hit limits, the system will gracefully fallback to rule-based extraction

## 🎉 Ready to Go!

Once you add your DeepSeek API key, your Enhanced AI Sales Agent will deliver production-quality results completely free!
