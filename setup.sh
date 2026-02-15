#!/bin/bash

# FitTrack Pro - Setup Script
echo "🚀 Setting up FitTrack Pro..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Update .env with generated secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
    else
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
    fi
    
    echo "⚠️  Don't forget to add your Stripe keys to .env!"
fi

# Create data directory
mkdir -p data

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Stripe API keys to .env file"
echo "   - Get test keys from: https://dashboard.stripe.com/test/apikeys"
echo "2. Run: ./start.sh"
echo ""
