# Deployment Guide - FitTrack Pro

## Prerequisites

1. **Stripe Account**
   - Sign up at https://stripe.com
   - Get your test API keys from https://dashboard.stripe.com/test/apikeys
   - Set up webhook endpoint (see Stripe Webhooks section below)

2. **Choose Your Platform**
   - Heroku (easiest)
   - Railway.app (recommended)
   - Fly.io
   - Any Docker-compatible host

## Quick Deploy to Railway.app (Recommended)

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy**
   ```bash
   cd ~/clawd/fitness-tracker
   railway init
   railway up
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   railway variables set STRIPE_SECRET_KEY=sk_test_YOUR_KEY
   railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
   railway variables set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   ```

4. **Get Your URL**
   ```bash
   railway domain
   ```

5. **Set up Stripe Webhook** (see below)

## Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   heroku login
   ```

2. **Create App**
   ```bash
   cd ~/clawd/fitness-tracker
   heroku create fittrack-pro-yourname
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   heroku config:set STRIPE_SECRET_KEY=sk_test_YOUR_KEY
   heroku config:set STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
   heroku config:set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   ```

4. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   heroku git:remote -a fittrack-pro-yourname
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

## Deploy to Fly.io

1. **Install Flyctl**
   ```bash
   brew install flyctl
   fly auth login
   ```

2. **Initialize**
   ```bash
   cd ~/clawd/fitness-tracker
   fly launch --no-deploy
   ```

3. **Set Secrets**
   ```bash
   fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   fly secrets set STRIPE_SECRET_KEY=sk_test_YOUR_KEY
   fly secrets set STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
   fly secrets set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

## Stripe Webhook Setup

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL: `https://your-app-url.com/webhook`
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
5. Copy the webhook signing secret
6. Set it as `STRIPE_WEBHOOK_SECRET` environment variable

## Testing Payment Flow

1. Use Stripe test card: `4242 4242 4242 4242`
2. Use any future expiration date
3. Use any 3-digit CVC
4. Use any 5-digit ZIP code

## Going Live

1. **Get Stripe Live Keys**
   - Switch to live mode in Stripe dashboard
   - Get live API keys
   - Set up live webhook endpoint

2. **Update Environment Variables**
   ```bash
   # Replace sk_test_* with sk_live_*
   # Replace pk_test_* with pk_live_*
   railway variables set STRIPE_SECRET_KEY=sk_live_YOUR_KEY
   railway variables set STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
   ```

3. **Update Webhook Secret**
   - Create new webhook for production URL
   - Update `STRIPE_WEBHOOK_SECRET`

4. **Test Everything**
   - Sign up flow
   - Payment flow
   - Subscription management
   - Data isolation

## Monitoring

- **Railway**: View logs with `railway logs`
- **Heroku**: View logs with `heroku logs --tail`
- **Fly.io**: View logs with `fly logs`

## Backup Strategy

User data is stored in JSON files in the `data/` directory. Set up automated backups:

**Railway**:
- Use Railway volumes for persistence
- Set up daily backup script

**Heroku**:
- Consider upgrading to a proper database (PostgreSQL)
- Use Heroku's automated backups

## Security Checklist

- ✅ Use strong `SECRET_KEY`
- ✅ Enable HTTPS (automatic on most platforms)
- ✅ Verify Stripe webhook signatures
- ✅ Keep dependencies updated
- ✅ Don't commit `.env` file
- ✅ Rotate secrets regularly

## Support

For issues, check:
- Application logs
- Stripe dashboard for payment issues
- Platform-specific documentation

---

**Ready to launch!** 🚀
