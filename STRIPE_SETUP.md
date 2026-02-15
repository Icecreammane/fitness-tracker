# Stripe Setup Guide

Complete guide to setting up Stripe for FitTrack Pro.

## Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Click "Start now" and create an account
3. Complete account setup (you can skip identity verification for testing)

## Step 2: Get Test API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Make sure you're in **TEST MODE** (toggle in top right)
3. Copy these keys:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)

3. Add them to your `.env` file:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
   STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
   ```

## Step 3: Set Up Webhook (After Deployment)

Webhooks notify your app when subscriptions are created or canceled.

### For Local Testing (ngrok)

1. Install ngrok: `brew install ngrok`
2. Run your app: `./start.sh`
3. In another terminal: `ngrok http 3000`
4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Go to https://dashboard.stripe.com/test/webhooks
6. Click "Add endpoint"
7. Webhook URL: `https://abc123.ngrok.io/webhook`
8. Select events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
9. Click "Add endpoint"
10. Copy the **Signing secret** (starts with `whsec_`)
11. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET`
12. Restart your app

### For Production Deployment

1. Deploy your app (Railway/Heroku/Fly.io)
2. Get your production URL (e.g., `https://fittrack.railway.app`)
3. Go to https://dashboard.stripe.com/test/webhooks
4. Click "Add endpoint"
5. Webhook URL: `https://your-app-url.com/webhook`
6. Select events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
7. Click "Add endpoint"
8. Copy the **Signing secret**
9. Set environment variable on your platform:
   ```bash
   railway variables set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   # or
   heroku config:set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
   ```

## Step 4: Test Payment Flow

1. Start your app: `./start.sh`
2. Go to `http://localhost:3000`
3. Sign up for an account
4. Click "Subscribe" or go to `/pricing`
5. Click "Start Free Trial"
6. Use test card details:
   - **Card number:** 4242 4242 4242 4242
   - **Expiry:** Any future date (e.g., 12/25)
   - **CVC:** Any 3 digits (e.g., 123)
   - **ZIP:** Any 5 digits (e.g., 12345)
7. Complete checkout
8. You should be redirected to "Payment Success" page
9. Check Stripe dashboard - you'll see the test payment

## Step 5: Verify Webhook

1. In Stripe dashboard, go to Webhooks
2. Click on your webhook endpoint
3. You should see recent events
4. Click on an event to see the payload
5. Check your app logs - you should see webhook received

## Testing Different Scenarios

### Test Cards

Stripe provides test cards for different scenarios:

**Successful payment:**
- `4242 4242 4242 4242` - Visa
- `5555 5555 5555 4444` - Mastercard

**Failed payment:**
- `4000 0000 0000 0002` - Card declined

**3D Secure required:**
- `4000 0027 6000 3184` - Requires authentication

### Test Subscription Cancellation

1. Go to https://dashboard.stripe.com/test/subscriptions
2. Find your test subscription
3. Click "Cancel subscription"
4. Your webhook should receive `customer.subscription.deleted` event
5. User's subscription status should update to "canceled"

## Going Live

When ready to accept real payments:

1. Complete Stripe account verification
2. Switch to **Live Mode** (toggle in dashboard)
3. Get **Live API keys**: https://dashboard.stripe.com/apikeys
4. Set up **Live Webhook** with production URL
5. Update environment variables with live keys:
   ```bash
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_... (new live webhook secret)
   ```

## Monitoring & Management

### View Payments
- Test: https://dashboard.stripe.com/test/payments
- Live: https://dashboard.stripe.com/payments

### View Subscriptions
- Test: https://dashboard.stripe.com/test/subscriptions
- Live: https://dashboard.stripe.com/subscriptions

### View Customers
- Test: https://dashboard.stripe.com/test/customers
- Live: https://dashboard.stripe.com/customers

## Common Issues

**Issue:** "No such plan" error
- **Fix:** Make sure you're using test keys in test mode

**Issue:** Webhook not receiving events
- **Fix:** Check webhook URL is correct and publicly accessible

**Issue:** "Invalid webhook signature"
- **Fix:** Make sure `STRIPE_WEBHOOK_SECRET` matches the webhook signing secret

**Issue:** Payment succeeds but subscription status not updating
- **Fix:** Check webhook is receiving `checkout.session.completed` event

## Security Checklist

- ✅ Never commit API keys to git
- ✅ Use environment variables for all secrets
- ✅ Use test keys for development
- ✅ Verify webhook signatures
- ✅ Keep Stripe library updated
- ✅ Use HTTPS in production

## Support

- **Stripe Docs:** https://stripe.com/docs
- **API Reference:** https://stripe.com/docs/api
- **Support:** https://support.stripe.com

---

**You're ready to accept payments!** 💳
