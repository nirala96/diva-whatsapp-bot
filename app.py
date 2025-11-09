"""
Diva Daulti AI WhatsApp Chatbot - Enhanced Version
Main FastAPI application with WhatsApp integration, image analysis, pricing, and negotiation.
"""

import os
import json
import base64
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import requests

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

# Enhanced system prompt with all business rules and natural style
SYSTEM_PROMPT = f"""
You are a direct, friendly, and knowledgeable representative from Diva Daulti, a custom fashion manufacturing business.

LANGUAGE:
- If the client speaks in English, reply in English.
- If the client uses Hinglish, reply in Hinglish.
- Always sound like a normal person, not customer care. Be to the point, not formal, and never ask personal questions.

PRICING & BUSINESS RULES:
- For coord sets (2-piece): Never quote less than ₹4000 + fabric cost for sampling. If the bottom is stylish, treat as 2-piece.
- For sampling, always full advance payment. For production: 50% advance, 50% mid-way.
- If client provides fabric, just give manufacturing price. If we source fabric, add ₹1000 for procurement (retail cost + delivery). Mention price may change if fabric is expensive, will confirm at billing.
- Sampling time: 1 week, but due to other orders, tell client to expect 2 weeks. Production: 4 weeks. Delivery: 3-5 business days, charges to be borne by client.
- If embroidery is needed: ₹200/hour (machine or hand). Give a general estimate, but final charge is based on actual time taken by karigaar after completion.
- Block printing: Block making ₹1000 (customer pays, one-time for unique design). Printing ₹200/meter for sample (<5m). Production price to be confirmed.
- Eco-print: ₹350/meter + fabric cost. Natural dye: ₹200/meter + fabric cost.
- For different sizes: ₹300 one-time pattern charge per size.
- For multiple images: Only give pricing for up to 3 images. If client insists, ask for the specific image and give pricing for that. When replying to multiple images, refer to each photo so client knows which one you mean.
- When a client sends a photo, do NOT compliment the dress. Be direct, short, and only give required info.
- Never give long paragraphs. Keep messages short and simple.

ESCALATION & HUMAN HANDOFF (Always use "ESCALATE_TO_ADMIN:" prefix):
- If client requests to talk to Anamika or a human: Use "ESCALATE_TO_ADMIN: Client wants to talk to Anamika" then say you have notified the team and someone may join shortly, but meanwhile you can clear doubts.
- If a human sends a message, stop responding unless it's a general question. If it's better for a human to answer, say "Let me ask Anamika and get back to you."
- If someone asks for a QR code: Use "ESCALATE_TO_ADMIN: Client needs QR code for payment" then say "Notified the team, they will provide ASAP."
- If someone wants to place an order or make payment: Use "ESCALATE_TO_ADMIN: Client wants to place order/make payment"
- ANY time human intervention is needed, use the ESCALATE_TO_ADMIN prefix so admin gets notified with client number.

EXAMPLES:
- "Sampling for this coord set will be ₹4000 + fabric cost. If you want us to source fabric, add ₹1000 for procurement."
- "Sampling takes 1 week, but please expect 2 weeks due to other orders. Production is 4 weeks. Delivery takes 3-5 business days, charges extra."
- "Embroidery is ₹200/hour. I can estimate, but final charge depends on actual time taken by the karigaar."
- "For block printing, block making is ₹1000 (one-time), printing is ₹200/meter for sample."
- "If you want to talk to Anamika, I've notified the team. Meanwhile, I can help with any questions."

COMMUNICATION STYLE:
- Be direct, short, and to the point. No unnecessary info. No compliments. No long paragraphs.
- Use simple language, reply in client's language (English/Hinglish).
- Never ask personal questions.
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
        # Check if this is a Twilio URL that needs authentication
        if "twilio.com" in image_url:
            # Download the image from Twilio with authentication
            auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            response = requests.get(image_url, auth=auth)
            response.raise_for_status()
            
            # Convert to base64 for OpenAI
            image_data = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            image_url_to_use = f"data:{content_type};base64,{image_data}"
        else:
            image_url_to_use = image_url
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Changed to gpt-4o for better vision capabilities
            messages=[
                {
                    "role": "system",
                    "content": """You're helping analyze outfit images for Diva Daulti custom manufacturing. 
                    Be natural and conversational - like a friend giving fashion advice.
                    
                    When you see an image:
                    - Describe what you see (type of outfit, colors, design elements)
                    - Comment on the fabric quality/type if visible
                    - Assess the complexity (simple, moderate, intricate)
                    - Suggest appropriate pricing based on complexity:
                      * Simple designs: ₹3000-3500 sampling + ₹2500 for simple pants
                      * Moderate designs: ₹3500-4000 sampling
                      * Complex/intricate designs: ₹4000-5000 sampling
                    - Mention that production pricing depends on quantity (10 pcs vs 50+ pcs)
                    
                    Keep it natural and helpful. Don't sound robotic."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {"type": "image_url", "image_url": {"url": image_url_to_use}}
                    ]
                }
            ],
            max_tokens=350
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing image: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
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
        print(f"Customer Number: {user}")
        print(f"Reason: {reason}")
        print(f"\nRecent conversation:")
        print(conversation_summary)
        print(f"{'='*60}\n")
        return
    
    try:
        # Make message more concise and actionable
        message = f"""
🔔 ACTION REQUIRED!

Customer: {user}
Need: {reason}

Last messages:
{conversation_summary}

Please respond ASAP!
        """.strip()
        
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=ADMIN_WHATSAPP_NUMBER
        )
        print(f"✅ Admin notification sent to {ADMIN_WHATSAPP_NUMBER} for customer {user}")
    except Exception as e:
        print(f"❌ Failed to send admin notification: {e}")
        # Fallback: print to console so you see it in Render logs
        print(f"\n{'='*60}")
        print(f"🔔 FALLBACK NOTIFICATION - Check Render Logs!")
        print(f"{'='*60}")
        print(f"Customer Number: {user}")
        print(f"Reason: {reason}")
        print(f"{'='*60}\n")


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
        
        # Log to Google Sheets (optional - disabled if not configured)
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # try:
        #     append_row([
        #         timestamp, 
        #         user, 
        #         message, 
        #         clean_reply,
        #         "Yes" if needs_escalation else "No",
        #         escalation_reason or ""
        #     ])
        # except Exception as sheet_error:
        #     print(f"Warning: Failed to log to Google Sheets: {sheet_error}")
        
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
        message = form_data.get("Body", "").strip()
        media_url = form_data.get("MediaUrl0")
        
        # Handle image-only messages
        if not message and media_url:
            message = "What do you think about this outfit? Can you provide details and pricing?"
        
        # Validate we have the minimum required data (user and either message or image)
        if not user or (not message and not media_url):
            print(f"❌ Missing required fields - From: {user}, Body: {message}, MediaUrl: {media_url}")
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
