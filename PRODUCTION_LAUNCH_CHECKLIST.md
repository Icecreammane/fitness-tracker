# 🚀 FitTrack Pro - Production Launch Checklist

**Goal**: Deploy FitTrack Pro to production in under 30 minutes and start generating revenue.

**Prerequisites**: You have a Railway/Heroku account and a Stripe account.

---

## ⏱️ Pre-Launch (15 minutes)

### 1. Stripe Setup (5 minutes)

- [ ] Log into [Stripe Dashboard](https://dashboard.stripe.com/)
- [ ] Switch to **LIVE MODE** (toggle in top-right corner)
- [ ] Create product: **FitTrack Pro Subscription**
  - Name: "FitTrack Pro Monthly"
  - Price: $9.99/month recurring
  - Copy the **Price ID** (starts with `price_`)
- [ ] Get API keys:
  - [ ] **Publishable key** (starts with `pk_live_`)
  - [ ] **Secret key** (starts with `sk_live_`)
- [ ] Set up webhook:
  - Go to Developers → Webhooks → Add endpoint
  - URL: `https://yourdomain.com/stripe-webhook`
  - Events to listen: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
  - Copy **Webhook Secret** (starts with `whsec_`)

**Checkpoint**: You have 4 Stripe values saved in a text file.

---

### 2. Google Analytics Setup (3 minutes)

- [ ] Go to [Google Analytics](https://analytics.google.com/)
- [ ] Create new property: "FitTrack Pro"
- [ ] Set up GA4 data stream (Web)
- [ ] Copy **Measurement ID** (starts with `G-`)

**Checkpoint**: You have GA Measurement ID.

---

### 3. Generate Secret Key (1 minute)

Run this in terminal:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output. This is your `SECRET_KEY`.

---

### 4. Domain & SSL (5 minutes)

**Option A: Use Railway/Heroku domain (easiest)**
- Railway: `your-app.up.railway.app` (SSL automatic)
- Heroku: `your-app.herokuapp.com` (SSL automatic)

**Option B: Custom domain (recommended for branding)**
- [ ] Buy domain (Namecheap, Google Domains, etc.)
- [ ] Point DNS A record to your Railway/Heroku IP
- [ ] Add domain in Railway/Heroku dashboard
- [ ] SSL automatically provisioned (takes 5-10 min)

**Checkpoint**: You have a domain (custom or platform-provided).

---

## 🚀 Launch (10 minutes)

### 5. Deploy to Railway (Recommended)

**Why Railway?** 
- Easiest deployment
- Free tier ($5/month credit)
- Automatic SSL
- Built-in logging

**Steps**:

1. **Install Railway CLI** (if not already):
   ```bash
   npm install -g @railway/cli
   # OR
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Initialize project**:
   ```bash
   cd /Users/clawdbot/clawd/fitness-tracker
   railway login
   railway init
   ```

3. **Set environment variables**:
   ```bash
   railway variables set SECRET_KEY="<your-secret-key>"
   railway variables set STRIPE_SECRET_KEY="sk_live_..."
   railway variables set STRIPE_PUBLISHABLE_KEY="pk_live_..."
   railway variables set STRIPE_PRICE_ID="price_..."
   railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
   railway variables set GA_MEASUREMENT_ID="G-..."
   railway variables set FLASK_ENV="production"
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Get your URL**:
   ```bash
   railway domain
   ```

**Checkpoint**: App is live! Visit your URL.

---

### Alternative: Deploy to Heroku

1. **Install Heroku CLI** (if not already):
   ```bash
   brew install heroku/brew/heroku
   heroku login
   ```

2. **Create app**:
   ```bash
   cd /Users/clawdbot/clawd/fitness-tracker
   heroku create fittrackpro
   ```

3. **Set config vars**:
   ```bash
   heroku config:set SECRET_KEY="<your-secret-key>"
   heroku config:set STRIPE_SECRET_KEY="sk_live_..."
   heroku config:set STRIPE_PUBLISHABLE_KEY="pk_live_..."
   heroku config:set STRIPE_PRICE_ID="price_..."
   heroku config:set STRIPE_WEBHOOK_SECRET="whsec_..."
   heroku config:set GA_MEASUREMENT_ID="G-..."
   heroku config:set FLASK_ENV="production"
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Production deploy"
   git push heroku main
   ```

5. **Open app**:
   ```bash
   heroku open
   ```

---

## ✅ Post-Launch Testing (5 minutes)

### 6. End-to-End Test

- [ ] **Visit landing page** - Does it load?
- [ ] **Sign up** - Create test account
- [ ] **Dashboard loads** - See empty dashboard
- [ ] **Log a workout** - Add a lift
- [ ] **Log food** - Add a meal
- [ ] **Log weight** - Add weight entry
- [ ] **Check charts** - Data visualizes correctly
- [ ] **Test Stripe** - Go to pricing, start checkout
  - Use test card: `4242 4242 4242 4242`
  - Expiry: Any future date
  - CVC: Any 3 digits
  - [ ] Payment succeeds
  - [ ] Redirected to success page
  - [ ] Subscription active in dashboard

**Checkpoint**: Everything works! 🎉

---

### 7. Stripe Webhook Verification

- [ ] Go to Stripe Dashboard → Developers → Webhooks
- [ ] Find your webhook endpoint
- [ ] Click "Send test webhook"
- [ ] Event: `checkout.session.completed`
- [ ] Check logs to confirm received

**Checkpoint**: Webhooks working.

---

## 📊 Monitoring Setup (5 minutes)

### 8. Set Up Uptime Monitoring

**Option A: UptimeRobot (Free)**
- [ ] Sign up at [uptimerobot.com](https://uptimerobot.com)
- [ ] Add monitor:
  - Type: HTTP(s)
  - URL: `https://yourdomain.com/health`
  - Interval: 5 minutes
- [ ] Add alert email

**Option B: Railway Built-in**
- Health checks automatic
- View logs in Railway dashboard

---

### 9. Google Search Console

- [ ] Go to [search.google.com/search-console](https://search.google.com/search-console)
- [ ] Add property: `https://yourdomain.com`
- [ ] Verify ownership (DNS or HTML file)
- [ ] Submit sitemap: `https://yourdomain.com/sitemap.xml`

**Checkpoint**: Google will start indexing your site.

---

## 📄 Legal Pages (Optional but Recommended)

### 10. Create Terms & Privacy

Use generators:
- [Termly.io](https://termly.io) (free generator)
- [GetTerms.io](https://getterms.io) (free)

Create files:
- [ ] `templates/terms.html`
- [ ] `templates/privacy.html`

Add routes in `app_production.py`:
```python
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
```

Link in footer of landing page.

**Checkpoint**: Legal compliance covered.

---

## 💬 Support Setup

### 11. Set Up Support Email

**Option A: Gmail Alias**
- Create: `support@yourdomain.com` → forwards to your Gmail
- Respond from Gmail

**Option B: Dedicated Support Tool**
- [Help Scout](https://www.helpscout.com/) - Free for 1 user
- [Front](https://front.com/) - Shared inbox

Update in code:
- `templates/500.html` - Change support email
- Landing page footer - Add support link

---

## 🎯 Launch Announcement

### 12. Announce on Social Media

Post on:
- [ ] **Reddit**: r/Fitness, r/weightroom, r/leangains, r/SaaS
  - Use template from MARKETING_GUIDE.md
- [ ] **Twitter**: "Just launched FitTrack Pro! 🚀..."
- [ ] **Product Hunt**: Submit for review
- [ ] **Indie Hackers**: Share launch story
- [ ] **Hacker News**: Post to Show HN

**Template Post**:
```
🚀 Just launched FitTrack Pro - a fitness tracking app for people who want precision.

Track workouts, macros, and progress with clean visualizations.

7-day free trial, no credit card required.
$9.99/month after trial.

Built it in 2 weeks. Would love feedback!

[link]
```

---

## 📈 Revenue Tracking

### 13. Set Up Revenue Dashboard

**Stripe Dashboard**:
- [ ] Bookmark: `https://dashboard.stripe.com/`
- Check daily:
  - New subscriptions
  - MRR (Monthly Recurring Revenue)
  - Churn rate

**Simple Spreadsheet** (optional):
- Track daily:
  - New signups
  - Trial conversions
  - Cancellations
  - MRR

**Goal**: $3,000 MRR = 300 paying customers @ $10/month

---

## 🔄 Ongoing Maintenance

### Daily (2 minutes)
- [ ] Check logs for errors
- [ ] Monitor uptime (email alerts)
- [ ] Check Stripe dashboard for new subs

### Weekly (15 minutes)
- [ ] Review Google Analytics
  - Traffic sources
  - Conversion rates
  - User behavior
- [ ] Respond to support emails
- [ ] Check for failed payments (retry)

### Monthly (1 hour)
- [ ] Backup data directory
  ```bash
  railway run tar -czf backup-$(date +%Y%m%d).tar.gz data/
  railway run curl -X POST -F "file=@backup-$(date +%Y%m%d).tar.gz" https://your-backup-service.com
  ```
- [ ] Review churn reasons (exit surveys)
- [ ] Analyze conversion funnel
- [ ] Plan improvements

---

## 🎉 You're Live!

**Checklist Complete**: You now have:
- ✅ Live production app
- ✅ Stripe payments working
- ✅ Monitoring set up
- ✅ Legal pages (recommended)
- ✅ Support email
- ✅ Announced to the world

**Next Steps**:
1. Drive traffic (see MARKETING_GUIDE.md)
2. Collect feedback
3. Iterate on features
4. Scale to $3K MRR!

---

## 🆘 Troubleshooting

### App won't start
- Check logs: `railway logs` or `heroku logs --tail`
- Verify all env vars set: `railway variables` or `heroku config`

### Payments not working
- Confirm Stripe keys are **live mode** (not test)
- Check webhook URL matches deployed domain
- Test webhook in Stripe dashboard

### Webhook errors
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Check logs for webhook payloads
- Test with Stripe CLI: `stripe listen --forward-to localhost:3000/stripe-webhook`

### Email issues
- Phase 2 - emails not implemented yet
- Users can contact support directly for password resets

---

## 📞 Support

If stuck, check:
- **TROUBLESHOOTING.md** - Common issues
- **ADMIN_GUIDE.md** - How to manage users
- **SUPPORT_FAQ.md** - Customer questions

---

**Estimated Total Time**: 30 minutes (if everything goes smoothly)

**Worst Case**: 1 hour (if DNS/domain setup takes longer)

**You got this! 🚀**
