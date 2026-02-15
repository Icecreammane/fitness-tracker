# 📇 FitTrack Pro - Quick Reference Card

**One-page cheat sheet for launching and managing FitTrack Pro**

---

## 🚀 Launch Commands (30 min)

```bash
# 1. Clone/Navigate
cd ~/clawd/fitness-tracker

# 2. Deploy to Railway
railway init
railway up

# 3. Set Environment Variables
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set STRIPE_SECRET_KEY=sk_live_YOUR_KEY
railway variables set STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
railway variables set STRIPE_PRICE_ID=price_YOUR_PRICE_ID
railway variables set STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
railway variables set GA_MEASUREMENT_ID=G-YOUR_ID
railway variables set FLASK_ENV=production

# 4. Get Domain
railway domain

# 5. Test
# Visit your domain, test signup/payment flow
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| **app_production.py** | Production Flask app (USE THIS) |
| **requirements_production.txt** | Production dependencies |
| **templates/landing_optimized.html** | SEO-optimized landing |
| **.env.example** | Environment variable template |
| **START_HERE.md** | Read this first! |
| **PRODUCTION_LAUNCH_CHECKLIST.md** | 30-min deploy guide |

---

## 🔐 Environment Variables

```bash
SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))">
STRIPE_SECRET_KEY=sk_live_...      # From Stripe Dashboard
STRIPE_PUBLISHABLE_KEY=pk_live_... # From Stripe Dashboard
STRIPE_PRICE_ID=price_...          # Create in Stripe
STRIPE_WEBHOOK_SECRET=whsec_...    # Create webhook
GA_MEASUREMENT_ID=G-...            # From Google Analytics
FLASK_ENV=production               # Set to 'production'
```

---

## 💰 Stripe Setup (5 min)

1. Log into [dashboard.stripe.com](https://dashboard.stripe.com)
2. Switch to **LIVE MODE** (toggle top-right)
3. Create product: "FitTrack Pro Monthly" - $9.99/month
4. Copy **Price ID** (starts with `price_`)
5. Get API keys: **Publishable** (pk_live_...) and **Secret** (sk_live_...)
6. Set up webhook: Developers → Webhooks → Add endpoint
   - URL: `https://yourdomain.com/stripe-webhook`
   - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy **Webhook Secret** (whsec_...)

---

## 📊 Google Analytics Setup (3 min)

1. Go to [analytics.google.com](https://analytics.google.com)
2. Create property: "FitTrack Pro"
3. Set up GA4 data stream (Web)
4. Copy **Measurement ID** (G-...)

---

## 📈 Daily Checklist (2 min/day)

- [ ] Check logs: `railway logs --tail 50`
- [ ] Check Stripe: New subscriptions?
- [ ] Check email: Support requests?
- [ ] Visit site: Still working?

---

## 📅 Weekly Checklist (15 min/week)

- [ ] Review Google Analytics (traffic, conversions)
- [ ] Backup data: `railway run tar -czf backup.tar.gz data/`
- [ ] Check failed payments (Stripe dashboard)
- [ ] Update revenue spreadsheet

---

## 🚨 Emergency Commands

### App Down
```bash
railway logs --tail 100        # Check what went wrong
railway service restart        # Restart app
```

### Rollback Deploy
```bash
railway rollback              # Go back to previous version
```

### View Users
```bash
railway run cat data/users.json
```

### Backup Data
```bash
railway run tar -czf backup.tar.gz data/
# Then download locally
```

---

## 💬 Support Quick Responses

### "How do I cancel?"
> Go to your Stripe customer portal: [link]. Click "Cancel subscription". Confirm.

### "Can I get a refund?"
> Yes, within 30 days. Refund processed - will appear in 5-7 business days.

### "I forgot my password"
> Email me your account email. I'll reset it manually. (Auto-reset in Phase 2)

### "How do I log a meal?"
> Dashboard → Log Food → Enter description, calories, protein, carbs, fat → Save.

---

## 📣 Marketing Checklist (Day 1)

- [ ] Reddit: r/Fitness, r/SaaS, r/SideProject (use template from MARKETING_GUIDE.md)
- [ ] Product Hunt: Submit at 12:01am PST
- [ ] Twitter: Tweet with #FitnessTech #SaaS #IndieHacker
- [ ] Indie Hackers: Share launch story

---

## 🎯 Key Metrics to Track

| Metric | Where to Check | Target |
|--------|----------------|--------|
| **Signups** | Stripe Dashboard or `data/users.json` | 50+ (Month 1) |
| **Trial → Paid** | Stripe Dashboard | 10-20% |
| **MRR** | Stripe Dashboard (top-right) | $3,000 (goal) |
| **Churn** | Stripe → Subscriptions → Canceled | <5%/month |
| **Uptime** | UptimeRobot | 99.9% |
| **Traffic** | Google Analytics | 1,000+/month |

---

## 🛠️ Common Issues

### "Payments not working"
- ✅ Using **live mode** keys? (not test mode)
- ✅ Webhook URL matches deployed domain?
- ✅ STRIPE_WEBHOOK_SECRET correct?

### "App won't start"
- ✅ All env vars set? (`railway variables`)
- ✅ Python syntax valid? (`python3 app_production.py` locally)
- ✅ Check logs: `railway logs --tail 100`

### "No traffic after launch"
- ✅ Posted on Reddit?
- ✅ Launched on Product Hunt?
- ✅ Shared on Twitter?
- ✅ SEO takes 1-2 weeks to kick in

---

## 📚 Documentation Quick Links

| Topic | File |
|-------|------|
| **Getting Started** | START_HERE.md |
| **Deploy in 30 min** | PRODUCTION_LAUNCH_CHECKLIST.md |
| **What Changed** | PRODUCTION_OPTIMIZATION_SUMMARY.md |
| **Manage Users** | ADMIN_GUIDE.md |
| **Market & Grow** | MARKETING_GUIDE.md |
| **Customer Support** | SUPPORT_FAQ.md |
| **Email Sequences** | EMAIL_TEMPLATES.md |
| **Security Info** | SECURITY_AUDIT_REPORT.md |
| **Performance** | PERFORMANCE_BENCHMARKS.md |

---

## 🎯 Revenue Milestones

| MRR | Users | Monthly Profit | Action |
|-----|-------|----------------|--------|
| $100 | 10 | -$50 | Break-even soon |
| $500 | 50 | $400 | Profitable! 🎉 |
| $1,000 | 100 | $900 | Sustainable |
| **$3,000** | **300** | **$2,900** | **🎯 GOAL!** |

**Costs**: ~$10-50/month (Railway) + 2.9% + $0.30 (Stripe fees)

---

## 🧪 Test Payment (Stripe Test Mode)

**Card**: 4242 4242 4242 4242  
**Expiry**: Any future date  
**CVC**: Any 3 digits  
**ZIP**: Any 5 digits

---

## 📞 Support Contacts

- **Stripe Support**: [support.stripe.com](https://support.stripe.com)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Google Analytics Help**: [support.google.com/analytics](https://support.google.com/analytics)

---

## ✅ Pre-Launch Verification

Run this to check everything is ready:

```bash
python3 verify_production_ready.py
```

Should output: `✅ All checks passed! (24/24)`

---

## 🚀 Launch Day Timeline

| Time | Task | Duration |
|------|------|----------|
| 9:00 AM | Deploy to Railway | 15 min |
| 9:15 AM | Test end-to-end | 10 min |
| 9:25 AM | Post on Reddit | 30 min |
| 10:00 AM | Launch Product Hunt | 1 hour |
| 11:00 AM | Tweet announcement | 15 min |
| 11:15 AM | Monitor & respond | Ongoing |

---

## 💡 Pro Tips

1. **Respond to ALL comments** on Reddit/Product Hunt (first 24 hours)
2. **Be humble** - Ask for feedback, don't oversell
3. **Track everything** - Google Analytics is your friend
4. **Iterate fast** - Fix bugs within hours, not days
5. **Email users** - Personal touch converts trials to paid

---

## 🎉 When You Hit $3K MRR

1. **Celebrate!** 🎉 You built a profitable SaaS
2. **Scale up** - Migrate to PostgreSQL, add team features
3. **Hire help** - Part-time support, marketing VA
4. **Raise prices** - $14.99/month with grandfathered pricing
5. **Build features** - Mobile app, meal plans, coaching

---

**Print this page. Keep it by your desk. You'll need it! 💪**

**Last Updated**: 2026-02-06  
**Version**: 1.0.0
