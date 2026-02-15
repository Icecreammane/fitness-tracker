# 🍺 Brewery Launch Checklist - Tomorrow!

Everything you need to launch FitTrack Pro tomorrow at the brewery.

## Before You Leave Home (30 minutes)

### 1. Get Stripe Test Keys (5 min)
- [ ] Go to https://stripe.com
- [ ] Sign up / Log in
- [ ] Go to https://dashboard.stripe.com/test/apikeys
- [ ] Copy both keys:
  - `pk_test_...` (Publishable key)
  - `sk_test_...` (Secret key)
- [ ] Add them to `~/clawd/fitness-tracker/.env`

### 2. Test Locally (10 min)
```bash
cd ~/clawd/fitness-tracker
./start.sh
```

- [ ] Visit http://localhost:3000
- [ ] Sign up: `your-email@gmail.com` / `testpass123`
- [ ] Dashboard loads
- [ ] Log some test food
- [ ] Looks good? ✅

Press Ctrl+C to stop.

### 3. Deploy to Railway (10 min)

**First time setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login
```

**Deploy:**
```bash
cd ~/clawd/fitness-tracker
railway init  # Follow prompts
railway up    # Deploy!
```

**Set environment variables:**
```bash
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
railway variables set STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

**Get your URL:**
```bash
railway domain
# Save this URL! You'll share it.
```

### 4. Set Up Stripe Webhook (5 min)
- [ ] Go to https://dashboard.stripe.com/test/webhooks
- [ ] Click "Add endpoint"
- [ ] URL: `https://your-railway-url.up.railway.app/webhook`
- [ ] Events: Select `checkout.session.completed` and `customer.subscription.deleted`
- [ ] Copy webhook signing secret (starts with `whsec_`)
- [ ] Set it:
```bash
railway variables set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
```

## At the Brewery (30 minutes)

### 5. Final Test on Production (5 min)
- [ ] Open your Railway URL
- [ ] Sign up with a new email
- [ ] Test payment with: `4242 4242 4242 4242` (test card)
- [ ] Verify it works end-to-end
- [ ] Everything working? ✅

### 6. Launch on Reddit (10 min)

**Post to r/fitness:**

Title:
```
I built a dead-simple fitness tracker for people who actually lift ($10/mo, 7-day free trial)
```

Body (from LAUNCH_MATERIALS.md):
```markdown
Hey r/fitness,

I got tired of overcomplicated fitness apps that try to do everything. I just wanted to track my macros, log my lifts, and see my progress. So I built FitTrack Pro.

**What it does:**
- Track daily macros (protein, carbs, fat, calories)
- Log workouts with automatic 1RM calculator
- Weight progress charts
- 7-day macro history
- Clean, fast interface

**What it doesn't do:**
- Social features
- Meal planning
- Recipe databases
- Complicated workout programs
- Try to sell you supplements

It's $10/month with a 7-day free trial (no credit card required).

I built this for myself and have been using it daily for the past month. Figured others might find it useful too.

**Try it:** [YOUR_RAILWAY_URL_HERE]

Open to feedback! What features matter most to you in a fitness tracker?
```

- [ ] Replace `[YOUR_RAILWAY_URL_HERE]` with your actual URL
- [ ] Post to r/fitness
- [ ] Respond to comments

### 7. Tweet Thread (5 min)

Copy from LAUNCH_MATERIALS.md:

**Tweet 1:**
```
I built a fitness tracker for people who don't want BS features they'll never use.

Just macros, workouts, and progress tracking. $10/mo.

7-day free trial, no credit card required.

🧵 Here's why I built it:
```

**Tweet 2-6:** (Copy from LAUNCH_MATERIALS.md)

- [ ] Post thread
- [ ] Add your Railway URL to final tweet

### 8. Share with Friends (5 min)
- [ ] Text 3-5 friends who lift
- [ ] Share on Instagram story
- [ ] Post in any fitness Discord/Slack you're in

### 9. Monitor (Throughout the Day)

Check these occasionally:
- [ ] Railway logs: `railway logs`
- [ ] Stripe dashboard: https://dashboard.stripe.com/test
- [ ] Reddit comments
- [ ] Twitter replies

## Success Metrics (End of Day)

**Day 1 Goals:**
- [ ] 10+ signups
- [ ] 1+ paying customer (even if it's you testing)
- [ ] 3+ comments/replies on Reddit
- [ ] No major bugs reported

**If you hit these, you have a product!** 🎉

## Troubleshooting at the Brewery

**Site won't load:**
```bash
railway logs --tail
# Look for errors
```

**Payment not working:**
- Check Stripe dashboard for errors
- Verify webhook is receiving events
- Check environment variables are set

**Signups not working:**
- Check Railway logs
- Test locally: `./start.sh`
- Verify SECRET_KEY is set

**Need to make quick fix:**
```bash
# Edit file
nano app_saas.py  # or code app_saas.py

# Deploy update
railway up
```

## Emergency Contacts

If you get stuck:
- **Stripe Support:** https://support.stripe.com
- **Railway Docs:** https://docs.railway.app
- **Me (Jarvis):** Just message me! I'll help debug

## After Launch (Next Few Days)

- [ ] Respond to all Reddit comments
- [ ] Reply to tweets
- [ ] Fix any bugs reported
- [ ] Add users to email list (if you set one up)
- [ ] Post update with user count

## Going Live with Real Payments

When you're ready (not tomorrow, but soon):

1. Complete Stripe verification
2. Switch to live mode
3. Get live API keys
4. Update Railway variables
5. Test with real card (refund yourself)
6. Start accepting real money! 💰

---

## Quick Reference

**Your URLs:**
- Production: `https://your-app.up.railway.app` (get with `railway domain`)
- Stripe Dashboard: https://dashboard.stripe.com/test
- Railway Dashboard: https://railway.app

**Test Card:**
- Number: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits

**Common Commands:**
```bash
# View logs
railway logs

# Deploy changes
railway up

# Set environment variable
railway variables set KEY=value

# Open app in browser
railway open
```

---

**You've got this!** Have a beer, launch a product, make some money. 🚀🍺

Tomorrow you'll have:
- ✅ A deployed web app
- ✅ Payment processing working
- ✅ Your first users
- ✅ A real SaaS business

**See you on the other side!** 💪
