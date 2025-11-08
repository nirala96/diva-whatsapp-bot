"""
Diva Daulti AI WhatsApp Chatbot
Main FastAPI application for handling customer conversations using OpenAI GPT-4o-mini.
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from utils.sheets import append_row

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Diva Daulti AI Chatbot",
    description="AI-powered WhatsApp chatbot for Diva Daulti fashion brand",
    version="1.0.0"
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for the AI assistant
SYSTEM_PROMPT = """
You are Aisha, a warm and friendly customer service representative for Diva Daulti, 
a premium fashion brand specializing in traditional and contemporary women's wear.

Your role:
- Greet customers warmly and professionally
- Answer questions about products, fabrics, designs, and sizing
- Help customers find the perfect outfit for their occasions
- Build rapport and make customers feel valued
- Keep responses concise, friendly, and conversational
- Use emojis occasionally to add warmth (but don't overdo it)
- If asked about prices, mention that you'll check with the team and get back to them

Always maintain a helpful, upbeat tone and make customers feel like they're chatting 
with a knowledgeable friend who genuinely cares about their style needs.
"""


class ChatMessage(BaseModel):
    """Request model for incoming chat messages"""
    user: str  # User identifier (phone number or name)
    message: str  # Customer's message


class ChatResponse(BaseModel):
    """Response model for chat replies"""
    reply: str  # AI-generated reply


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Diva Daulti AI Chatbot",
        "version": "1.0.0"
    }


@app.post("/webhook", response_model=ChatResponse)
async def webhook(chat_message: ChatMessage):
    """
    Main webhook endpoint to receive customer messages and generate AI replies.
    
    This endpoint:
    1. Receives a message from a customer
    2. Uses OpenAI GPT-4o-mini to generate a contextual reply as "Aisha"
    3. Logs the conversation to Google Sheets
    4. Returns the AI-generated reply
    
    Args:
        chat_message: ChatMessage object containing user identifier and message
        
    Returns:
        ChatResponse: Contains the AI-generated reply
        
    Raises:
        HTTPException: If OpenAI API fails or Google Sheets logging fails
    """
    try:
        # Generate AI reply using OpenAI ChatCompletion
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chat_message.message}
            ],
            temperature=0.8,  # Slightly creative but still coherent
            max_tokens=200,   # Keep responses concise for WhatsApp
        )
        
        # Extract the reply from OpenAI response
        reply = response.choices[0].message.content.strip()
        
        # Log conversation to Google Sheets
        # Format: [timestamp, user, customer_message, ai_reply]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            append_row([timestamp, chat_message.user, chat_message.message, reply])
        except Exception as sheet_error:
            # Log the error but don't fail the request
            print(f"Warning: Failed to log to Google Sheets: {sheet_error}")
        
        # Return the AI-generated reply
        return ChatResponse(reply=reply)
        
    except Exception as e:
        # Handle any errors and return appropriate HTTP error
        print(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@app.post("/test-chat")
async def test_chat(chat_message: ChatMessage):
    """
    Test endpoint for debugging without logging to Google Sheets.
    Useful for development and testing.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chat_message.message}
            ],
            temperature=0.8,
            max_tokens=200,
        )
        
        reply = response.choices[0].message.content.strip()
        
        return {
            "reply": reply,
            "note": "This is a test response - not logged to Google Sheets"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with hot reload enabled for development
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
