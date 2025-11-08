# 📱 WhatsApp Integration Setup Guide

## 🎯 Overview

This guide will help you integrate your Diva Daulti AI chatbot with WhatsApp using Twilio. Once set up, customers can chat directly with your AI bot on WhatsApp!

## ✨ New Features

Your enhanced chatbot now supports:

✅ **WhatsApp Integration** - Customers chat via WhatsApp  
✅ **Image Analysis** - AI can see and analyze outfit images using GPT-4 Vision  
✅ **Pricing & Negotiation** - Bot provides quotes and negotiates (up to 15% discount)  
✅ **Smart Escalation** - Automatically notifies you when human intervention needed  
✅ **Payment Notifications** - Alerts you when customer is ready to buy  
✅ **Conversation Memory** - Bot remembers context within each conversation  

---

## 🚀 Step-by-Step Setup

### Step 1: Sign Up for Twilio

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Verify your phone number
4. You'll get **FREE credits** to test with!

### Step 2: Enable WhatsApp Sandbox

1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Or visit: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
3. Follow instructions to join the sandbox:
   - Send a WhatsApp message to the Twilio number
   - Send the code they provide (e.g., "join <your-code>")
4. Now your WhatsApp is connected to Twilio!

### Step 3: Get Your Twilio Credentials

1. From Twilio Dashboard, get:
   - **Account SID** (looks like: `ACxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (click to reveal)
   - **WhatsApp Sandbox Number** (e.g., `+1 415 523 8886`)

2. Add these to your `.env` file:
   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ADMIN_WHATSAPP_NUMBER=whatsapp:+919876543210  # Your WhatsApp number
   ```

### Step 4: Expose Your Server to Internet

For WhatsApp to send messages to your bot, Twilio needs a public URL.

**Option A: Use ngrok (Easiest for Testing)**

1. Download ngrok: https://ngrok.com/download
2. Sign up (free) and get your auth token
3. Install and run:
   ```bash
   # Install ngrok
   brew install ngrok  # macOS
   # or download from website
   
   # Authenticate
   ngrok config add-authtoken YOUR_NGROK_TOKEN
   
   # Expose your local server
   ngrok http 8000
   ```
4. You'll get a public URL like: `https://abc123.ngrok.io`

**Option B: Deploy to Cloud**
- Deploy to Heroku, Railway, DigitalOcean, AWS, etc.
- Get a permanent public URL

### Step 5: Configure Twilio Webhook

1. Go to Twilio Console → **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
2. In **"When a message comes in"** field, enter:
   ```
   https://your-ngrok-url.ngrok.io/whatsapp
   ```
   Example: `https://abc123.ngrok.io/whatsapp`
3. Make sure HTTP Method is **POST**
4. Click **Save**

### Step 6: Update Your Admin WhatsApp Number

In `.env`, set your WhatsApp number (where you'll receive notifications):
```bash
ADMIN_WHATSAPP_NUMBER=whatsapp:+919876543210  # Replace with your number
```

Format: `whatsapp:+[country code][number]`  
Example: `whatsapp:+919876543210` for Indian number

### Step 7: Test the Integration!

1. **Start the enhanced server:**
   ```bash
   cd /Users/arunoday.kumar/Desktop/personal/divadaulti_tech/diva_ai_bot
   venv/bin/python3 app_whatsapp.py
   ```

2. **Send a WhatsApp message** to the Twilio sandbox number

3. **The bot should respond!** 🎉

---

## 📋 Testing Checklist

### Test 1: Basic Chat
```
You: Hi! Do you have silk sarees?
Bot: [Should respond warmly with product info]
```

### Test 2: Image Analysis
1. Send a photo of an outfit
2. Bot should analyze it and provide details!

### Test 3: Pricing
```
You: How much for a wedding lehenga?
Bot: [Should provide price range ₹8,000-₹50,000]
```

### Test 4: Negotiation
```
You: That's too expensive. Can you give me a discount?
Bot: [Should offer up to 15% discount]

You: I want 30% off
Bot: [Should escalate to you - you'll get notified!]
```

### Test 5: Payment Ready
```
You: Ok I'll take the red silk saree for ₹5,000
Bot: [Should ask for delivery details and notify you]
```

You should receive a WhatsApp notification when escalation or payment is needed!

---

## 🎮 Available Endpoints

### 1. WhatsApp Webhook (Main)
```
POST /whatsapp
```
Receives messages from WhatsApp via Twilio

### 2. Test Webhook (For API testing)
```
POST /webhook
Content-Type: application/json

{
  "user": "+919876543210",
  "message": "Hello!",
  "image_url": "https://example.com/image.jpg"  // optional
}
```

### 3. Send Proactive Message
```
POST /send-whatsapp?to=+919876543210&message=Hello!
```
Send a WhatsApp message to a customer

### 4. Get Conversation History
```
GET /conversation/whatsapp:+919876543210
```

### 5. Clear Conversation
```
POST /clear-conversation/whatsapp:+919876543210
```

---

## 🤖 How the AI Works

### Automatic Features:

1. **Conversation Memory**
   - Remembers last 10 messages per user
   - Provides context-aware responses

2. **Image Analysis** (GPT-4 Vision)
   - Analyzes outfit photos
   - Suggests occasions and pricing
   - Provides styling advice

3. **Pricing & Negotiation**
   - Knows price ranges for all products
   - Can offer up to 15% discount
   - Knows when to escalate

4. **Smart Escalation**
   Automatically escalates when:
   - Custom design/alteration requests
   - Bulk orders (10+ pieces)
   - Discount > 15%
   - Complaints or issues
   - Payment problems
   - Customer asks for manager
   - Complex shipping queries

5. **Payment Detection**
   When customer says they want to buy, bot:
   - Confirms all details
   - Asks for delivery address
   - Provides payment options
   - Notifies you immediately!

---

## 📊 Notifications You'll Receive

You'll get WhatsApp notifications for:

1. **Escalation Needed**
   ```
   🔔 Escalation Needed
   
   From: whatsapp:+919876543210
   Message: I want 30% discount on 20 sarees
   
   Please check and respond!
   ```

2. **Payment Ready**
   ```
   🔔 Payment Ready
   
   From: whatsapp:+919876543210
   Message: Ready for payment! Last: Yes, I'll take it
   
   Please check and respond!
   ```

---

## 💰 Costs

### Twilio WhatsApp (Production - After Sandbox)
- **Template Messages**: $0.005 per message
- **Session Messages** (24h window): $0.005 per message
- **Free Tier**: Good credits to start

### OpenAI API
- **GPT-4o-mini** (chat): ~$0.15 per 1M tokens (very cheap!)
- **GPT-4o** (vision): ~$2.50 per 1M input tokens
- Typical conversation: < $0.01
- Image analysis: ~$0.01-0.02

**Total per customer chat**: Usually < $0.05

---

## 🔒 Security Best Practices

1. **Never expose your .env file**
   ```bash
   # Already in .gitignore
   .env
   ```

2. **Verify webhook signatures** (for production)
   Add Twilio signature validation in production

3. **Rate limiting** (optional)
   ```bash
   pip install slowapi
   ```

4. **Use HTTPS** (required for production)
   ngrok provides HTTPS automatically

---

## 🚀 Going to Production

### Upgrade from Sandbox

1. **Business Verification**
   - Verify your business with Twilio
   - Get approved for WhatsApp Business API
   - Takes 1-3 days

2. **Get Your Own WhatsApp Number**
   - Purchase a phone number from Twilio
   - Or use your existing business number

3. **Deploy to Cloud**
   ```bash
   # Example: Deploy to Railway
   railway init
   railway up
   ```

4. **Update Webhook URL**
   - Use your production domain
   - Configure in Twilio Console

5. **Create Message Templates**
   - Required for messages outside 24h window
   - Submit for WhatsApp approval

---

## ❓ Troubleshooting

### "Webhook not receiving messages"
1. Check ngrok is running: `ngrok http 8000`
2. Verify webhook URL in Twilio has `/whatsapp` endpoint
3. Check server logs for errors
4. Ensure server is running on port 8000

### "Admin notifications not working"
1. Verify ADMIN_WHATSAPP_NUMBER is set correctly
2. Format must be: `whatsapp:+[country code][number]`
3. Check Twilio credentials are valid
4. Ensure you've joined the sandbox

### "Image analysis failing"
1. GPT-4o (vision) requires valid OpenAI key
2. Check image URL is publicly accessible
3. Verify OpenAI account has credits

### "Bot not remembering context"
1. Conversation memory is in-memory (resets on restart)
2. For production, use Redis or database
3. Each user's context is separate

---

## 📚 Resources

- **Twilio WhatsApp Docs**: https://www.twilio.com/docs/whatsapp
- **ngrok Docs**: https://ngrok.com/docs
- **OpenAI Vision API**: https://platform.openai.com/docs/guides/vision
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

## 🎉 You're All Set!

Your WhatsApp AI chatbot is ready to:
- Chat with customers 24/7
- Analyze outfit images
- Provide pricing and negotiate
- Know when to escalate to you
- Notify you for payment confirmations

**Start testing and refine as needed!** 🚀

---

## 📞 Need Help?

Check the logs:
```bash
tail -f server.log
```

Test without WhatsApp:
```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{"user": "test", "message": "Hello!"}'
```

View API docs:
```
http://localhost:8000/docs
```
