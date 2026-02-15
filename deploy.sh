#!/bin/bash

# Lean Fitness Tracker - Railway Deployment Script
# Run this after: railway login

set -e  # Exit on error

echo "🚀 Deploying Lean to Railway..."
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Please run: railway login"
    exit 1
fi

echo "✅ Railway CLI authenticated"
echo ""

# Check if project exists, otherwise init
if ! railway status &> /dev/null; then
    echo "📦 Initializing new Railway project..."
    railway init
    echo ""
fi

# Set environment variables
echo "🔧 Setting environment variables..."

# OpenAI API Key
OPENAI_KEY="your-openai-api-key-here"
railway variables set OPENAI_API_KEY="$OPENAI_KEY"

# Generate secret key
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set SECRET_KEY="$SECRET"

# Port (Railway provides $PORT)
railway variables set PORT=3000

echo "✅ Environment variables set"
echo ""

# Deploy
echo "🚢 Deploying application..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""

# Wait a moment for deployment
sleep 5

# Generate domain if not exists
echo "🌐 Setting up public domain..."
railway domain 2>/dev/null || echo "Domain already exists"

echo ""
echo "📋 Getting deployment info..."
railway status

echo ""
echo "🔗 Get your public URL with: railway domain"
echo "📊 View logs with: railway logs --tail"
echo "🎯 Test the app and report back!"
echo ""
echo "✅ Deployment complete!"
