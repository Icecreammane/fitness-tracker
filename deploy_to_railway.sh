#!/bin/bash
# Deploy Lean Fitness Tracker to Railway
# Run after: railway login

set -e

echo "=========================================="
echo "Lean Fitness Tracker - Railway Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "Install with: brew install railway"
    exit 1
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Railway${NC}"
    echo "Run: railway login"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI ready${NC}"
echo ""

# Initialize or link project
echo "Step 1: Project Setup"
echo "---------------------"
if [ -f ".railway" ]; then
    echo "Project already linked"
else
    echo "Initializing new Railway project..."
    railway init
fi
echo ""

# Generate SECRET_KEY if not exists
echo "Step 2: Environment Variables"
echo "-----------------------------"
echo "Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set SECRET_KEY="$SECRET_KEY"
echo -e "${GREEN}✅ SECRET_KEY set${NC}"

railway variables set FLASK_ENV="production"
echo -e "${GREEN}✅ FLASK_ENV set${NC}"

# Prompt for OpenAI key
echo ""
read -p "Enter OpenAI API key (or press Enter to skip): " OPENAI_KEY
if [ -n "$OPENAI_KEY" ]; then
    railway variables set OPENAI_API_KEY="$OPENAI_KEY"
    echo -e "${GREEN}✅ OPENAI_API_KEY set${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping OpenAI key - voice logging will not work${NC}"
fi

# Optional Stripe keys
echo ""
read -p "Configure Stripe? (y/N): " configure_stripe
if [[ $configure_stripe =~ ^[Yy]$ ]]; then
    read -p "Stripe Secret Key: " STRIPE_SECRET
    read -p "Stripe Publishable Key: " STRIPE_PUB
    read -p "Stripe Webhook Secret: " STRIPE_WEBHOOK
    
    railway variables set STRIPE_SECRET_KEY="$STRIPE_SECRET"
    railway variables set STRIPE_PUBLISHABLE_KEY="$STRIPE_PUB"
    railway variables set STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK"
    echo -e "${GREEN}✅ Stripe keys set${NC}"
else
    echo "Skipping Stripe configuration"
fi

echo ""
echo "Step 3: Deploy"
echo "-------------"
echo "Deploying to Railway..."
railway up

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Get your public URL:"
echo "   railway domain"
echo ""
echo "2. View logs:"
echo "   railway logs --tail"
echo ""
echo "3. Test health check:"
echo "   curl https://your-app.railway.app/health"
echo ""
echo "4. Open in browser:"
echo "   railway open"
echo ""

# Try to get domain
echo "Fetching public URL..."
DOMAIN=$(railway domain 2>/dev/null || echo "")
if [ -n "$DOMAIN" ]; then
    echo ""
    echo -e "${GREEN}🚀 Your app is live at:${NC}"
    echo "   $DOMAIN"
    echo ""
    echo "Testing health check..."
    sleep 5  # Wait for deployment
    curl -s "$DOMAIN/health" || echo "App still starting up - check in a moment"
fi

echo ""
echo -e "${GREEN}Deployment successful!${NC}"
