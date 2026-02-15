#!/bin/bash

# FitTrack Pro - Start Script
echo "🚀 Starting FitTrack Pro..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

echo ""
echo "✓ Starting server on http://localhost:3000"
echo "✓ Press Ctrl+C to stop"
echo ""

# Start the app
python app_saas.py
