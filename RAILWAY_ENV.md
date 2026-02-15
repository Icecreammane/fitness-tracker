# Railway Environment Variables Guide

## Required Environment Variables

Set these in your Railway project settings under **Variables**:

### 1. Flask Configuration
```
SECRET_KEY=<generate-with-python-secrets>
FLASK_ENV=production
```

Generate SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. OpenAI API (for Voice Logging)
```
OPENAI_API_KEY=sk-proj-...
```
Get from: https://platform.openai.com/api-keys

### 3. Stripe (Optional - for payments)
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
Get from: https://dashboard.stripe.com/apikeys

**Note:** Start with test keys (`sk_test_...`) and switch to live keys when ready for production.

---

## Railway Auto-Provided Variables

Railway automatically provides these - **DO NOT SET**:
- `PORT` - Railway assigns the port dynamically
- `RAILWAY_ENVIRONMENT` - Set to "production"
- `RAILWAY_PROJECT_ID` - Your project ID
- `RAILWAY_SERVICE_NAME` - Your service name

---

## Optional Variables

```
DATABASE_PATH=data/users.json  # Default path for data storage
```

---

## Setting Variables in Railway

### Via Railway Dashboard:
1. Go to your project
2. Click on your service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add each variable above

### Via Railway CLI:
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set FLASK_ENV="production"
railway variables set OPENAI_API_KEY="sk-proj-..."
```

---

## Production Checklist

- [ ] SECRET_KEY set (unique, 64+ characters)
- [ ] FLASK_ENV=production
- [ ] OPENAI_API_KEY set (if using voice logging)
- [ ] Stripe keys set (if using payments)
- [ ] Health check endpoint working: `/health`
- [ ] HTTPS enabled (automatic on Railway)
- [ ] Custom domain configured (optional)

---

## Security Notes

1. **Never commit real keys to git** - use `.env` locally, Railway Variables in production
2. **Rotate keys regularly** - especially after team changes
3. **Use environment-specific keys** - test keys for staging, live keys for production
4. **Monitor usage** - watch OpenAI/Stripe dashboards for unexpected charges
5. **Enable webhooks carefully** - verify Stripe webhook signatures in production

---

## Troubleshooting

### App won't start:
- Check Railway logs: `railway logs`
- Verify all required variables are set
- Ensure SECRET_KEY is properly quoted

### Voice logging fails:
- Verify OPENAI_API_KEY is set correctly
- Check OpenAI usage limits/billing
- Review Railway logs for specific errors

### Port binding errors:
- Railway sets PORT automatically - don't override it
- Gunicorn binds to `0.0.0.0:$PORT` (configured in Dockerfile)
