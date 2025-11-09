"""
Diva Daulti AI WhatsApp Chatbot - Enhanced Version
Main FastAPI application with WhatsApp integration, image analysis, pricing, and negotiation.
"""

import os
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. WhatsApp features will be limited.")

from utils.sheets import append_row

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Diva Daulti AI WhatsApp Chatbot",
    description="AI-powered WhatsApp chatbot with image analysis, pricing, and negotiation",
    version="2.0.0"
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Twilio client (optional, for sending messages)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
ADMIN_WHATSAPP_NUMBER = os.getenv("ADMIN_WHATSAPP_NUMBER")

twilio_client = None
if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load pricing data
with open("pricing/pricing.json", "r") as f:
    PRICING_DATA = json.load(f)

# Enhanced system prompt with pricing and negotiation capabilities
SYSTEM_PROMPT = f"""
You are Aisha, a warm and knowledgeable customer service representative for Diva Daulti, 
a premium fashion brand specializing in traditional and contemporary women's wear.

Your capabilities:
- Greet customers warmly and professionally
- Answer questions about products, fabrics, designs, and sizing
- Analyze images of outfits when customers share them
- Provide pricing information based on product categories
- Handle price negotiations within acceptable limits
- Know when to escalate to human assistance

PRICING GUIDELINES:
{json.dumps(PRICING_DATA["categories"], indent=2)}

NEGOTIATION RULES:
- You can offer discounts up to the "negotiation_floor" percentage
- For example, if negotiation_floor is 0.85, you can go down to 85% of the price
- Always be polite and make customers feel valued during negotiation
- If customer asks for more than acceptable discount, politely say you'll check with the team

ESCALATION TRIGGERS (Request human intervention when):
1. Customer requests a discount below the negotiation floor
2. Customer wants to place an order and make payment
3. Customer has complex customization requests
4. Customer is unhappy or frustrated
5. Technical questions about fabric care or alterations you're unsure about

When escalating, use the phrase: "ESCALATE_TO_ADMIN:" followed by the reason.

Keep responses concise, friendly, and conversational. Use emojis occasionally but don't overdo it.
"""

# Conversation memory (in production, use Redis or database)
conversation_memory = {}


class ChatMessage(BaseModel):
    """Request model for incoming chat messages"""
    user: str
    message: str
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat replies"""
    reply: str
    needs_escalation: bool = False
    escalation_reason: Optional[str] = None


def analyze_image_with_gpt(image_url: str, user_message: str) -> str:
    """Analyze an image using GPT-4 Vision API."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are Aisha from Diva Daulti analyzing outfit images. 
                    Describe the outfit professionally, identify the type (saree/lehenga/suit/etc.),
                    comment on the fabric, color, design, and suggest appropriate occasions.
                    If asked about pricing, provide an estimate based on the category and quality you see."""
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return "I'm having trouble viewing the image right now. Could you describe what you're looking for?"


def get_conversation_context(user: str, limit: int = 5) -> List[dict]:
    """Get recent conversation history for context."""
    if user not in conversation_memory:
        conversation_memory[user] = []
    return conversation_memory[user][-limit:]


def add_to_conversation(user: str, role: str, content: str):
    """Add a message to conversation history"""
    if user not in conversation_memory:
        conversation_memory[user] = []
    conversation_memory[user].append({"role": role, "content": content})
    
    # Keep only last 10 messages to avoid token limits
    if len(conversation_memory[user]) > 10:
        conversation_memory[user] = conversation_memory[user][-10:]


def check_for_escalation(reply: str) -> tuple:
    """Check if the reply contains an escalation trigger."""
    if "ESCALATE_TO_ADMIN:" in reply:
        reason = reply.split("ESCALATE_TO_ADMIN:")[1].strip()
        clean_reply = reply.split("ESCALATE_TO_ADMIN:")[0].strip()
        return True, reason, clean_reply
    return False, None, reply


def send_admin_notification(user: str, reason: str, conversation_summary: str):
    """Send WhatsApp notification to admin when escalation is needed."""
    if not twilio_client or not ADMIN_WHATSAPP_NUMBER:
        print(f"\n{'='*60}")
        print(f"🔔 ESCALATION NEEDED - Admin Intervention Required!")
        print(f"{'='*60}")
        print(f"Customer: {user}")
        print(f"Reason: {reason}")
        print(f"\nRecent conversation:")
        print(conversation_summary)
        print(f"{'='*60}\n")
        return
    
    try:
        message = f"""
🔔 Customer Needs Your Help!

Customer: {user}
Reason: {reason}

Recent conversation:
{conversation_summary}

Please respond to this customer soon!
        """.strip()
        
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=ADMIN_WHATSAPP_NUMBER
        )
        print(f"✅ Admin notification sent for {user}")
    except Exception as e:
        print(f"❌ Failed to send admin notification: {e}")


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    twilio_configured = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
    
    return {
        "status": "running",
        "service": "Diva Daulti AI WhatsApp Chatbot",
        "version": "2.0.0",
        "features": ["whatsapp", "image_analysis", "pricing", "negotiation", "escalation"],
        "openai_configured": openai_configured,
        "twilio_configured": twilio_configured
    }


@app.post("/webhook", response_model=ChatResponse)
async def webhook(chat_message: ChatMessage):
    """
    Main webhook endpoint for programmatic access.
    Handles: Text messages, Image analysis, Pricing queries, Negotiation, Escalation to admin
    """
    try:
        user = chat_message.user
        message = chat_message.message
        image_url = chat_message.image_url
        
        # Get conversation context
        context = get_conversation_context(user)
        
        # Build messages for OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(context)
        
        # Handle image if provided
        if image_url:
            image_analysis = analyze_image_with_gpt(image_url, message)
            message = f"{message}\n\n[Image Analysis: {image_analysis}]"
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Generate AI reply
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=300,
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Check for escalation
        needs_escalation, escalation_reason, clean_reply = check_for_escalation(reply)
        
        # Add to conversation history
        add_to_conversation(user, "user", message)
        add_to_conversation(user, "assistant", clean_reply)
        
        # Log to Google Sheets
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            append_row([
                timestamp, 
                user, 
                message, 
                clean_reply,
                "Yes" if needs_escalation else "No",
                escalation_reason or ""
            ])
        except Exception as sheet_error:
            print(f"Warning: Failed to log to Google Sheets: {sheet_error}")
        
        # Send admin notification if escalation needed
        if needs_escalation:
            conversation_summary = "\n".join([
                f"{msg['role']}: {msg['content'][:100]}..." 
                for msg in context[-3:]
            ])
            send_admin_notification(user, escalation_reason, conversation_summary)
        
        return ChatResponse(
            reply=clean_reply,
            needs_escalation=needs_escalation,
            escalation_reason=escalation_reason
        )
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp webhook endpoint.
    Receives messages from WhatsApp via Twilio.
    """
    if not TWILIO_AVAILABLE:
        return {"error": "Twilio not configured"}
    
    try:
        form_data = await request.form()
        
        # Debug: print all form data
        print(f"📥 Received form data: {dict(form_data)}")
        
        # Extract message details
        user = form_data.get("From", "").replace("whatsapp:", "")
        message = form_data.get("Body", "")
        media_url = form_data.get("MediaUrl0")
        
        # Validate we have the minimum required data
        if not user or not message:
            print(f"❌ Missing required fields - From: {user}, Body: {message}")
            resp = MessagingResponse()
            resp.message("Sorry, I couldn't process your message. Please try again!")
            return Response(content=str(resp), media_type="application/xml")
        
        print(f"📱 WhatsApp message from {user}: {message}")
        if media_url:
            print(f"📷 Image received: {media_url}")
        
        # Process the message
        chat_message = ChatMessage(
            user=user,
            message=message,
            image_url=media_url
        )
        
        result = await webhook(chat_message)
        
        # Create Twilio response
        resp = MessagingResponse()
        resp.message(result.reply)
        
        if result.needs_escalation:
            resp.message(f"\n\n✨ I've notified my team about your request. Someone will get back to you soon!")
        
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        import traceback
        print(f"Error in WhatsApp webhook: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        resp = MessagingResponse()
        resp.message("Sorry, I'm having trouble right now. Please try again in a moment!")
        return Response(content=str(resp), media_type="application/xml")


@app.post("/test-chat")
async def test_chat(chat_message: ChatMessage):
    """Test endpoint for debugging without logging to Google Sheets."""
    try:
        context = get_conversation_context(chat_message.user)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(context)
        
        if chat_message.image_url:
            image_analysis = analyze_image_with_gpt(chat_message.image_url, chat_message.message)
            chat_message.message = f"{chat_message.message}\n\n[Image Analysis: {image_analysis}]"
        
        messages.append({"role": "user", "content": chat_message.message})
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=300,
        )
        
        reply = response.choices[0].message.content.strip()
        needs_escalation, escalation_reason, clean_reply = check_for_escalation(reply)
        
        return {
            "reply": clean_reply,
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
            "note": "This is a test response - not logged to Google Sheets"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@app.get("/conversation/{user}")
async def get_conversation(user: str):
    """Get conversation history for a user"""
    return {
        "user": user,
        "messages": conversation_memory.get(user, []),
        "count": len(conversation_memory.get(user, []))
    }


@app.delete("/conversation/{user}")
async def clear_conversation(user: str):
    """Clear conversation history for a user"""
    if user in conversation_memory:
        del conversation_memory[user]
    return {"message": f"Conversation cleared for {user}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
