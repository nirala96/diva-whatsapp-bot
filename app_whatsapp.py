"""
Enhanced Diva Daulti AI WhatsApp Chatbot with:
- WhatsApp integration via Twilio
- Image analysis with GPT-4 Vision
- Pricing and negotiation logic
- Escalation to human when needed
- Payment confirmation handling
"""

import os
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Form, Response
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests

from utils.sheets import append_row

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Diva Daulti AI WhatsApp Chatbot",
    description="AI-powered WhatsApp chatbot with image analysis and pricing",
    version="2.0.0"
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Twilio client
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
ADMIN_WHATSAPP_NUMBER = os.getenv("ADMIN_WHATSAPP_NUMBER")

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Enhanced system prompt
SYSTEM_PROMPT = """
You are Aisha, a warm and knowledgeable sales representative for Diva Daulti, 
a premium fashion brand specializing in traditional and contemporary women's wear.

YOUR CAPABILITIES:
1. Answer questions about products, fabrics, designs, sizing, and occasions
2. Analyze images customers send to provide styling advice and price estimates
3. Provide price quotes and handle price negotiations (within allowed limits)
4. Guide customers through the purchase process
5. Know when to escalate to human assistance

PRICING GUIDELINES:
- Sarees: ₹2,500 - ₹15,000 (avg ₹6,000)
- Lehengas: ₹8,000 - ₹50,000 (avg ₹20,000)
- Suits: ₹2,000 - ₹12,000 (avg ₹5,000)
- Kurtis: ₹800 - ₹3,500 (avg ₹1,500)
- You can offer up to 15% discount for negotiation
- Bulk orders (3+ pieces): mention additional discounts available
- Wedding collections: max 10% discount

WHEN TO ESCALATE (use [ESCALATE: reason]):
1. Custom design or alteration requests
2. Bulk orders over 10 pieces
3. Discount requests above 15%
4. Complaints about previous orders
5. Payment issues
6. Customer asks for manager/owner
7. Complex shipping queries

PAYMENT READY (use [PAYMENT_READY]):
When customer confirms they want to buy, ask for:
- Delivery address
- Preferred payment method (UPI/Bank Transfer/Card)
Then add [PAYMENT_READY] to notify admin

STYLE:
- Warm and professional
- 1-2 emojis max per message
- Keep it concise (2-4 sentences)
- Always helpful
"""

# Conversation memory
conversation_memory = {}


class ChatMessage(BaseModel):
    user: str
    message: str
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    escalate: bool = False
    payment_ready: bool = False


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Diva Daulti AI WhatsApp Chatbot",
        "version": "2.0.0",
        "features": ["WhatsApp", "Image Analysis", "Pricing", "Negotiation"]
    }


def analyze_image(image_url: str, user_message: str) -> str:
    """Analyze product images using GPT-4 Vision"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fashion expert for Diva Daulti. Analyze the outfit image: describe it, suggest occasions, estimate quality and price range."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Image analysis error: {e}")
        return "I can see your image! It looks lovely. Let me help you with details."


def get_conversation_context(user: str, limit: int = 5) -> List[dict]:
    """Get recent conversation history"""
    if user not in conversation_memory:
        conversation_memory[user] = []
    return conversation_memory[user][-limit:]


def add_to_conversation(user: str, role: str, content: str):
    """Add message to conversation memory"""
    if user not in conversation_memory:
        conversation_memory[user] = []
    conversation_memory[user].append({"role": role, "content": content})
    if len(conversation_memory[user]) > 10:
        conversation_memory[user] = conversation_memory[user][-10:]


def send_admin_notification(user: str, message: str, reason: str):
    """Send WhatsApp notification to admin"""
    if not twilio_client or not ADMIN_WHATSAPP_NUMBER:
        print(f"Admin notification (no Twilio): {reason} from {user}")
        return
    
    try:
        notification = f"🔔 *{reason}*\n\nFrom: {user}\nMessage: {message}\n\nPlease check and respond!"
        twilio_client.messages.create(
            body=notification,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=ADMIN_WHATSAPP_NUMBER if ADMIN_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{ADMIN_WHATSAPP_NUMBER}"
        )
        print(f"✅ Admin notified: {reason}")
    except Exception as e:
        print(f"Failed to notify admin: {e}")


def generate_ai_response(user: str, message: str, image_url: Optional[str] = None) -> dict:
    """Generate AI response with context and escalation detection"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(get_conversation_context(user))
    
    user_content = message
    if image_url:
        vision_analysis = analyze_image(image_url, message)
        user_content = f"{message}\n\n[Image Analysis: {vision_analysis}]"
    
    messages.append({"role": "user", "content": user_content})
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=250,
        )
        
        reply = response.choices[0].message.content.strip()
        escalate = "[ESCALATE:" in reply
        payment_ready = "[PAYMENT_READY]" in reply
        
        reply_clean = reply.replace("[PAYMENT_READY]", "").strip()
        if "[ESCALATE:" in reply_clean:
            reply_clean = reply_clean.split("[ESCALATE:")[0].strip()
        
        add_to_conversation(user, "user", message)
        add_to_conversation(user, "assistant", reply_clean)
        
        return {
            "reply": reply_clean,
            "escalate": escalate,
            "payment_ready": payment_ready
        }
    except Exception as e:
        print(f"AI error: {e}")
        return {
            "reply": "I apologize, I'm having trouble. Let me connect you with our team.",
            "escalate": True,
            "payment_ready": False
        }


@app.post("/webhook", response_model=ChatResponse)
async def webhook(chat_message: ChatMessage):
    """API webhook for testing"""
    try:
        result = generate_ai_response(chat_message.user, chat_message.message, chat_message.image_url)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            append_row([timestamp, chat_message.user, chat_message.message, result["reply"], 
                       "Yes" if result["escalate"] else "No", "Yes" if result["payment_ready"] else "No"])
        except Exception as e:
            print(f"Sheets logging failed: {e}")
        
        if result["escalate"]:
            send_admin_notification(chat_message.user, chat_message.message, "AI Escalation")
        if result["payment_ready"]:
            send_admin_notification(chat_message.user, f"Ready for payment! Last: {chat_message.message}", "Payment Confirmation")
        
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Twilio WhatsApp webhook"""
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        num_media = int(form_data.get("NumMedia", 0))
        image_url = form_data.get("MediaUrl0") if num_media > 0 else None
        
        print(f"📱 WhatsApp from {from_number}: {message_body}")
        
        result = generate_ai_response(from_number, message_body, image_url)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            append_row([timestamp, from_number, message_body, result["reply"],
                       "Yes" if result["escalate"] else "No", "Yes" if result["payment_ready"] else "No", "WhatsApp"])
        except Exception as e:
            print(f"Sheets logging failed: {e}")
        
        if result["escalate"] or result["payment_ready"]:
            reason = "Payment Ready" if result["payment_ready"] else "Escalation Needed"
            send_admin_notification(from_number, message_body, reason)
        
        resp = MessagingResponse()
        resp.message(result["reply"])
        return Response(content=str(resp), media_type="application/xml")
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        resp = MessagingResponse()
        resp.message("I apologize for the technical issue. Our team will assist you shortly.")
        return Response(content=str(resp), media_type="application/xml")


@app.post("/send-whatsapp")
async def send_whatsapp(to: str, message: str):
    """Send proactive WhatsApp message"""
    if not twilio_client:
        raise HTTPException(status_code=500, detail="Twilio not configured")
    try:
        msg = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        )
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{user}")
async def get_conversation(user: str):
    """Get conversation history"""
    return {"user": user, "messages": conversation_memory.get(user, [])}


@app.post("/clear-conversation/{user}")
async def clear_conversation(user: str):
    """Clear conversation history"""
    if user in conversation_memory:
        del conversation_memory[user]
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_whatsapp:app", host="0.0.0.0", port=8000, reload=True)
