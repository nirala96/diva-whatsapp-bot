# 🚀 Quick Start Guide - Diva Daulti AI Chatbot

## ⚡ TL;DR - Get Started in 5 Minutes

### 1. Set up environment
```bash
cd diva_ai_bot
source venv/bin/activate  # Virtual environment already created!
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Set up Google Sheets
Follow the detailed guide in `GOOGLE_SHEETS_SETUP.md` or skip for now (bot will still work, just won't log to sheets).

### 4. Start the server
```bash
./start.sh
# OR
python app.py
```

### 5. Test the bot
```bash
# In a new terminal
source venv/bin/activate
python test_bot.py
```

---

## 📁 Project Structure

```
diva_ai_bot/
├── app.py                      # ⭐ Main FastAPI application
├── requirements.txt            # 📦 Python dependencies (already installed!)
├── .env.example               # 🔑 Sample environment configuration
├── .env                       # 🔒 Your actual credentials (create this!)
├── .gitignore                 # 🚫 Git ignore rules
├── README.md                  # 📖 Full documentation
├── GOOGLE_SHEETS_SETUP.md     # 📊 Google Sheets setup guide
├── start.sh                   # 🚀 Quick start script
├── test_bot.py                # 🧪 Test script
├── venv/                      # 🐍 Virtual environment (already set up!)
├── utils/
│   ├── __init__.py
│   └── sheets.py              # 📊 Google Sheets integration
└── pricing/
    └── pricing.json           # 💰 Pricing data (for future use)
```

---

## 🎯 Key Features

✅ **Ready to Use**: Virtual environment and dependencies already installed  
✅ **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent responses  
✅ **Conversation Logging**: Automatically logs to Google Sheets  
✅ **Easy Testing**: Includes test script and interactive docs  
✅ **Production Ready**: Includes error handling and best practices  

---

## 🔧 Essential Commands

### Start the server
```bash
./start.sh
```

### Run tests
```bash
python test_bot.py
```

### Test Google Sheets connection
```bash
python -m utils.sheets
```

### Start server manually
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Important URLs

- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Chat Webhook**: http://localhost:8000/webhook
- **Test Endpoint**: http://localhost:8000/test-chat

---

## 📝 Sample API Request

```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "+919876543210",
    "message": "Hi! Do you have wedding lehengas?"
  }'
```

**Response:**
```json
{
  "reply": "Hello! Yes, absolutely! 😊 We have a stunning collection of wedding lehengas..."
}
```

---

## ⚙️ Configuration (.env file)

```bash
# Required for AI responses
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required for conversation logging
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
SHEET_NAME=DivaDaulti_Leads
```

---

## 🎨 How the Bot Works

1. **Receives Message**: Customer sends a message via POST /webhook
2. **AI Processing**: OpenAI GPT-4o-mini generates a warm, conversational response
3. **Logs Conversation**: Saves to Google Sheets (timestamp, user, message, reply)
4. **Returns Reply**: Sends AI-generated response back to customer

---

## 🔮 Future Enhancements

The project is structured to support:
- ✨ Price negotiation logic (using `pricing/pricing.json`)
- ✨ WhatsApp Business API integration
- ✨ Multi-turn conversations with context
- ✨ Product catalog search
- ✨ Order processing

---

## 🆘 Need Help?

1. **Server not starting?**
   - Check if .env file exists with valid OpenAI API key
   - Make sure virtual environment is activated

2. **Google Sheets not working?**
   - Follow `GOOGLE_SHEETS_SETUP.md` carefully
   - Most common issue: Forgot to share sheet with service account

3. **AI responses failing?**
   - Verify OpenAI API key is correct and has credits
   - Check internet connection

4. **Want to test without logging?**
   - Use `/test-chat` endpoint instead of `/webhook`

---

## 📞 Testing Tips

1. Start with `/test-chat` to test AI responses without logging
2. Once working, switch to `/webhook` for full functionality
3. Check Google Sheets after each test to verify logging
4. Use the interactive docs at `/docs` for easy testing

---

## 🎉 You're All Set!

The project is ready to use. Just add your OpenAI API key to `.env` and start the server!

```bash
./start.sh
```

Then visit http://localhost:8000/docs to start testing! 🚀
