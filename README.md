# 🌟 Diva Daulti AI Chatbot

An AI-powered WhatsApp chatbot for Diva Daulti fashion brand, built with FastAPI and OpenAI's GPT-4o-mini. The bot provides warm, conversational customer service while automatically logging all interactions to Google Sheets for lead tracking and analysis.

## ✨ Features

- 🤖 **AI-Powered Conversations**: Uses OpenAI GPT-4o-mini for natural, context-aware responses
- 💬 **Warm & Professional**: Responds as "Aisha", a friendly customer service representative
- 📊 **Automatic Logging**: All conversations stored in Google Sheets for lead management
- 🚀 **FastAPI Backend**: High-performance, async-ready REST API
- 🔒 **Secure**: Environment-based configuration for API keys and credentials
- 📈 **Scalable**: Ready for future enhancements like price negotiation logic

## 🏗️ Project Structure

```
diva_ai_bot/
├── app.py                      # Main FastAPI application
├── requirements.txt            # Python dependencies
├── .env.example               # Sample environment configuration
├── README.md                  # This file
├── utils/
│   ├── __init__.py
│   └── sheets.py              # Google Sheets integration
└── pricing/
    └── pricing.json           # Product pricing structure (for future use)
```

## 🔧 Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Google Cloud Service Account with Sheets API enabled

### 2. Create Virtual Environment

```bash
# Navigate to the project directory
cd diva_ai_bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account and download the JSON key file
5. Save the JSON file as `service_account.json` in the project root
6. Create a Google Sheet named `DivaDaulti_Leads`
7. Share the sheet with the service account email (found in the JSON file)

### 5. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# OPENAI_API_KEY=sk-your-actual-openai-key
# GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
# SHEET_NAME=DivaDaulti_Leads
```

### 6. Initialize Google Sheet Headers (Optional)

```bash
python -m utils.sheets
```

This will add column headers to your Google Sheet: `Timestamp`, `User`, `Customer Message`, `AI Reply`.

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### 1. Health Check

```bash
GET /
```

**Response:**
```json
{
  "status": "running",
  "service": "Diva Daulti AI Chatbot",
  "version": "1.0.0"
}
```

### 2. Chat Webhook (Main Endpoint)

```bash
POST /webhook
```

**Request Body:**
```json
{
  "user": "+919876543210",
  "message": "Hi! Do you have silk sarees?"
}
```

**Response:**
```json
{
  "reply": "Hello! Yes, we absolutely do! 😊 We have a beautiful collection of silk sarees in various styles..."
}
```

### 3. Test Chat (No Logging)

```bash
POST /test-chat
```

Same request/response format as `/webhook`, but doesn't log to Google Sheets. Useful for testing.

## 🧪 Testing the Bot

### Using cURL

```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "message": "Hello! What kind of outfits do you have?"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/webhook",
    json={
        "user": "+919876543210",
        "message": "Do you have wedding lehengas?"
    }
)

print(response.json()["reply"])
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for automatic interactive API documentation powered by Swagger UI.

## 📊 Google Sheets Integration

All conversations are automatically logged to your Google Sheet with the following columns:

| Timestamp | User | Customer Message | AI Reply |
|-----------|------|------------------|----------|
| 2024-01-01 12:00:00 | +919876543210 | Hi! | Hello! Welcome to Diva Daulti! 😊 |

This allows you to:
- Track all customer interactions
- Analyze common questions
- Follow up with leads
- Monitor bot performance

## 🔮 Future Enhancements

- [ ] **Price Negotiation Logic**: Implement smart pricing using `pricing/pricing.json`
- [ ] **WhatsApp Business API Integration**: Direct integration with WhatsApp
- [ ] **Multi-turn Conversations**: Context-aware conversations using conversation history
- [ ] **Product Catalog Search**: Search and recommend specific products
- [ ] **Order Processing**: Handle orders and payments
- [ ] **Multi-language Support**: Support for Hindi and other regional languages

## 🛠️ Troubleshooting

### "OpenAI API key not found"
- Ensure `.env` file exists and contains `OPENAI_API_KEY`
- Check that the API key is valid and has credits

### "Google Sheets authentication failed"
- Verify `service_account.json` exists and is valid
- Ensure the service account email has edit access to the sheet
- Check that Google Sheets API is enabled in Google Cloud Console

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

## 📝 License

This project is proprietary and confidential to Diva Daulti.

## 👥 Support

For issues or questions, contact the development team.

---

Built with ❤️ for Diva Daulti
