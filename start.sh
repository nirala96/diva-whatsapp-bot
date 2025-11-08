#!/bin/bash

# Diva Daulti AI Chatbot - Quick Start Script
# This script activates the virtual environment and starts the FastAPI server

echo "🌟 Starting Diva Daulti AI Chatbot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create .env from .env.example and add your API keys"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your credentials"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment and run the server
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
