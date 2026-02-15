# 👨‍💼 FitTrack Pro - Admin Guide

**For**: Ross (and future team members)  
**Purpose**: How to manage users, check revenue, handle support, and maintain the app.

---

## 📊 Daily Operations (2 minutes/day)

### Morning Checklist
1. **Check uptime** - Visit your domain, confirm it loads
2. **Review logs** - Look for errors
   ```bash
   railway logs --tail 50
   # OR
   heroku logs --tail 50
   ```
3. **Check Stripe dashboard** - Any new subscriptions overnight?
4. **Check support email** - Any customer issues?

**Expected**: 0 errors, 0-5 new signups (early days), 0-2 support emails.

---

## 👥 User Management

### View All Users

**Manual (JSON file)**:
```bash
railway run cat data/users.json
# OR
heroku run cat data/users.json
```

**What you'll see**:
```json
{
  "abc123...": {
    "id": "abc123...",
    "email": "user@example.com",
    "subscription_status": "active",
    "created_at": "2026-02-06T10:00:00",
    "trial_end": "2026-02-13T10:00:00"
  }
}
```

**Key Fields**:
- `subscription_status`: `trial`, `active`, `canceled`, `expired`
- `trial_end`: When trial expires
- `stripe_customer_id`: Link to Stripe customer

---

### Find a Specific User

```bash
railway run grep -A 10 "user@example.com" data/users.json
```

Or download the file:
```bash
railway run cat data/users.json > users_backup.json
# Open in text editor
```

---

### Manually Extend Trial

**When**: User requests more time to evaluate.

**Steps**:
1. Download users file:
   ```bash
   railway run cat data/users.json > users.json
   ```

2. Edit locally:
   - Find user by email
   - Change `trial_end` to new date (ISO format: `2026-02-20T10:00:00`)

3. Upload:
   ```bash
   railway run --upload users.json
   # Then manually move to data/ directory
   # (Railway doesn't support direct file editing easily)
   ```

**Better way**: Add admin endpoint (Phase 2).

---

### Cancel Subscription (Manual)

**When**: User requests cancellation outside of Stripe.

**Steps**:
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/customers)
2. Search for user email
3. Click subscription → Cancel subscription
4. Webhook will auto-update user status in app

**User sees**: "Subscription Expired" page, prompted to resubscribe.

---

### Refund User

**When**: User requests refund within 30 days.

**Steps**:
1. Stripe Dashboard → Payments
2. Find payment by email or date
3. Click "Refund"
4. Enter amount (full or partial)
5. Confirm

**Note**: Refunding doesn't auto-cancel subscription. Do that separately.

---

### Delete User Account (GDPR)

**When**: User requests account deletion.

**Steps**:
1. Stripe Dashboard → Cancel subscription (if active)
2. Delete user data:
   ```bash
   # Find user ID from users.json
   railway run rm data/fitness_data_<user_id>.json
   
   # Remove from users.json (manual edit)
   railway run cat data/users.json > users.json
   # Edit locally, remove user entry
   # Upload back (complex, see "Manually Extend Trial" above)
   ```

3. Confirm deletion to user via email

**Phase 2**: Build admin dashboard for this.

---

## 💰 Revenue Tracking

### Stripe Dashboard

**URL**: [dashboard.stripe.com](https://dashboard.stripe.com)

**Key Metrics**:
- **MRR** (Monthly Recurring Revenue): Home page, top-right
- **New Subscriptions**: Customers → Recent
- **Churn**: Subscriptions → Canceled (monitor weekly)
- **Failed Payments**: Payments → Failed (set up retry campaigns)

---

### Manual Tracking (Spreadsheet)

**Google Sheets Template**:

| Date | New Signups | Trial Conversions | Cancellations | Total Active | MRR |
|------|-------------|-------------------|---------------|--------------|-----|
| 2026-02-06 | 5 | 2 | 0 | 2 | $19.98 |
| 2026-02-07 | 8 | 1 | 0 | 3 | $29.97 |

**Update daily** (2 min):
- New Signups: Check `users.json` or Stripe
- Trial Conversions: Stripe → Subscriptions → Created today
- Cancellations: Stripe → Subscriptions → Canceled today
- MRR: Total Active × $9.99

**Goal**: $3,000 MRR = 300 active subscribers

---

### Revenue Milestones

| MRR | Active Users | Monthly Profit (estimate) | Status |
|-----|--------------|---------------------------|--------|
| $100 | 10 | -$50 (server costs) | Break-even soon |
| $500 | 50 | $400 | Profitable! |
| $1,000 | 100 | $900 | Sustainable |
| $3,000 | 300 | $2,900 | Target! 🎯 |

**Costs**:
- Railway/Heroku: ~$10-50/month (scales with usage)
- Stripe fees: 2.9% + $0.30 per transaction
- Domain: ~$10/year

---

## 📧 Customer Support

### Common Questions

**See**: `SUPPORT_FAQ.md` for copy-paste responses.

**Top 5 Questions**:
1. "How do I cancel?" → Stripe customer portal link
2. "Can I get a refund?" → Yes, within 30 days (Stripe refund)
3. "How do I export my data?" → Manual (send JSON file)
4. "I forgot my password" → Email verification (Phase 2), manual reset now
5. "What's included in the subscription?" → Features list

---

### Handling Support Emails

**Response Time Target**: 24 hours

**Template Structure**:
```
Hi [Name],

Thanks for reaching out!

[Answer their question]

Is there anything else I can help with?

Best,
Ross
FitTrack Pro
support@fittrackpro.com
```

**Tone**: Friendly, helpful, concise.

---

### Password Reset (Manual Process - Phase 2 will automate)

**When**: User forgot password.

**Current Process**:
1. Verify user identity (ask for email, maybe last workout logged)
2. Manually reset password:
   ```bash
   # Generate new password hash
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('NewPassword123'))"
   
   # Update users.json with new hash
   # (Download, edit, upload - see "Manually Extend Trial")
   ```

3. Email new password to user
4. Tell them to change it after login

**Better way**: Build password reset flow (Phase 2).

---

## 📈 Analytics Review (Weekly)

### Google Analytics Dashboard

**URL**: [analytics.google.com](https://analytics.google.com)

**Key Metrics to Check**:

1. **Traffic Sources** (Reports → Acquisition → Traffic acquisition)
   - Where are users coming from?
   - Reddit, Twitter, Product Hunt, Google?

2. **Conversion Rate** (Reports → Engagement → Conversions)
   - Landing page views → Signups
   - Signups → Trial starts
   - Trial starts → Paid subscriptions

3. **User Behavior** (Reports → Engagement → Pages and screens)
   - Which pages get most views?
   - Where do users drop off?

4. **Custom Events** (Reports → Events)
   - "signup" events
   - "trial_start" events
   - "workout_logged" events

**Goal**: 2-5% conversion rate (landing → signup)

---

### Interpreting Data

**Good Signs**:
- Conversion rate increasing week-over-week
- High engagement (users logging workouts daily)
- Low bounce rate on landing page (<50%)

**Red Flags**:
- High bounce rate (>70%) → Landing page not compelling
- Low trial conversions (<1%) → Pricing too high or features unclear
- High churn (>10%/month) → Product not delivering value

**Action**: Adjust copy, features, or pricing based on data.

---

## 🛠️ Maintenance Tasks

### Daily
- [x] Check logs for errors
- [x] Review Stripe for new subs
- [x] Respond to support emails

### Weekly (15 min)
- [x] Review Google Analytics
- [x] Backup data directory
  ```bash
  railway run tar -czf backup-$(date +%Y%m%d).tar.gz data/
  # Download locally
  railway run cat backup-*.tar.gz > local-backup.tar.gz
  ```
- [x] Check for failed payments in Stripe
- [x] Update revenue spreadsheet

### Monthly (1 hour)
- [x] Review churn reasons (exit survey if implemented)
- [x] Analyze conversion funnel (where are drop-offs?)
- [x] Plan feature improvements based on feedback
- [x] Financial review (MRR, costs, profitability)
- [x] Backup rotation (delete old backups, keep last 3 months)

---

## 🚨 Handling Emergencies

### App Down

**Symptoms**: Site not loading, 502/503 errors.

**Steps**:
1. Check Railway/Heroku status page
2. Check logs:
   ```bash
   railway logs --tail 100
   ```
3. Restart if needed:
   ```bash
   railway service restart
   ```
4. If database corrupted, restore from backup

**Prevention**: Set up uptime monitoring (UptimeRobot).

---

### Stripe Webhook Failing

**Symptoms**: Subscriptions created in Stripe but users still show "trial" status in app.

**Steps**:
1. Stripe Dashboard → Webhooks → Check delivery
2. See errors? Click to view payload
3. Test endpoint manually:
   ```bash
   stripe listen --forward-to https://yourdomain.com/stripe-webhook
   ```
4. Fix code if webhook URL changed (redeploy)

---

### Data Loss

**Symptoms**: User reports lost data.

**Steps**:
1. Check if backup exists:
   ```bash
   ls -lh backups/
   ```
2. Restore user file:
   ```bash
   tar -xzf backup-YYYYMMDD.tar.gz
   railway run --upload data/fitness_data_<user_id>.json
   ```
3. Apologize to user, offer free month

**Prevention**: Automate daily backups to cloud storage (Phase 2).

---

## 👨‍💻 Developer Tasks

### Deploying Updates

**Safe deployment process**:

1. **Test locally**:
   ```bash
   cd /Users/clawdbot/clawd/fitness-tracker
   python app_production.py
   # Test at http://localhost:3000
   ```

2. **Commit changes**:
   ```bash
   git add .
   git commit -m "Feature: Add XYZ"
   git push origin main
   ```

3. **Deploy**:
   ```bash
   railway up
   # OR
   git push heroku main
   ```

4. **Test production**:
   - Visit site
   - Test changed feature
   - Check logs for errors

---

### Rolling Back

**If update breaks something**:

```bash
# Railway
railway rollback

# Heroku
heroku releases
heroku rollback v123  # Replace with previous version number
```

---

### Adding Admin Routes (Phase 2)

**Example: View all users via web interface**

Add to `app_production.py`:
```python
@app.route('/admin/users')
@login_required
def admin_users():
    # TODO: Check if current_user is admin
    users = load_users()
    return render_template('admin_users.html', users=users)
```

Create `templates/admin_users.html`:
```html
<!-- Simple table of users -->
<table>
  <tr><th>Email</th><th>Status</th><th>Created</th></tr>
  {% for user in users.values() %}
  <tr>
    <td>{{ user.email }}</td>
    <td>{{ user.subscription_status }}</td>
    <td>{{ user.created_at }}</td>
  </tr>
  {% endfor %}
</table>
```

---

## 📊 Key Performance Indicators (KPIs)

**Track these weekly**:

| Metric | Formula | Target |
|--------|---------|--------|
| **MRR** | Active subs × $9.99 | $3,000 |
| **Churn Rate** | Cancellations / Active subs | <5%/month |
| **Conversion Rate** | Paid subs / Signups | 10-20% |
| **CAC** (Customer Acquisition Cost) | Ad spend / New customers | <$20 |
| **LTV** (Lifetime Value) | $9.99 × Avg months subscribed | >$100 |
| **LTV:CAC Ratio** | LTV / CAC | >3:1 |

**Good business**: LTV:CAC ratio >3:1, Churn <5%, MRR growing >10%/month.

---

## 🎯 Growth Strategies

### When Stuck at $500 MRR

**Tactics**:
- Reddit posts in more fitness subreddits
- Product Hunt launch (get upvotes)
- Offer referral program (give free month for referral)
- Content marketing (blog about fitness tracking)
- Paid ads (Facebook, Instagram) if CAC <$20

---

### When Approaching $3K MRR

**Prepare for scale**:
- Migrate to PostgreSQL (better than JSON files)
- Add Redis for rate limiting (multi-server support)
- Hire support help (part-time)
- Build admin dashboard (manage users without SSH)

---

## 📞 Getting Help

**Stuck?**
- Check `TROUBLESHOOTING.md`
- Stripe support: [support.stripe.com](https://support.stripe.com)
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Heroku docs: [devcenter.heroku.com](https://devcenter.heroku.com)

---

**This guide will grow as the product evolves. Update it after solving novel problems!**

**Last Updated**: 2026-02-06  
**Next Review**: After 100 active users
