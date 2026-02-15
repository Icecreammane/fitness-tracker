# Deploy Lean Fitness Tracker to Railway

## Pre-Deployment Checklist

- [x] requirements.txt updated with all dependencies
- [x] Procfile configured for gunicorn
- [x] railway.json configured
- [x] Dockerfile optimized for Railway
- [x] Health check endpoint added (`/health`)
- [x] Production logging configured
- [x] Environment variables documented

---

## Quick Deploy (Railway CLI)

### 1. Login to Railway
```bash
cd ~/clawd/fitness-tracker
railway login
```

### 2. Initialize Project (if needed)
```bash
railway init
```
- Choose: **Create new project**
- Name: `lean-fitness-tracker`

### 3. Link to existing project (if already created)
```bash
railway link
```

### 4. Set Environment Variables
```bash
# Generate and set secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set SECRET_KEY="$SECRET_KEY"

# Set Flask environment
railway variables set FLASK_ENV="production"

# Set OpenAI API key (required for voice logging)
railway variables set OPENAI_API_KEY="sk-proj-your-key-here"
```

### 5. Deploy
```bash
railway up
```

### 6. Get Public URL
```bash
railway domain
```

Or add a custom domain:
```bash
railway domain add leantracker.com
```

---

## Manual Deploy (Railway Dashboard)

### 1. Create New Project
1. Go to https://railway.app/new
2. Click **Deploy from GitHub repo**
3. Authorize Railway to access your repos
4. Select `fitness-tracker` repository
5. Railway will auto-detect Dockerfile

### 2. Configure Service
1. Click on your service
2. Go to **Settings** tab
3. Verify:
   - **Start Command**: Auto-detected from Dockerfile
   - **Health Check Path**: `/health`
   - **Restart Policy**: On Failure

### 3. Set Environment Variables
1. Go to **Variables** tab
2. Click **+ New Variable**
3. Add each variable from `RAILWAY_ENV.md`:
   - `SECRET_KEY`
   - `FLASK_ENV=production`
   - `OPENAI_API_KEY`
   - (Optional) Stripe keys

### 4. Deploy
1. Go to **Deployments** tab
2. Click **Deploy**
3. Watch build logs
4. Wait for "Deployed" status

### 5. Get Public URL
1. Go to **Settings** tab
2. Scroll to **Domains**
3. Click **Generate Domain**
4. Copy the public URL (e.g., `lean-fitness-tracker-production.up.railway.app`)

---

## Post-Deployment Testing

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```
Expected: `{"status":"healthy","timestamp":"..."}`

### 2. Dashboard Access
```bash
open https://your-app.railway.app
```
Should load the main dashboard with no errors.

### 3. Test Features
- [ ] Manual meal logging works
- [ ] Voice logging works (requires OpenAI key)
- [ ] Streak counter displays
- [ ] Weight tracking works
- [ ] Progress cards generate
- [ ] Settings save properly

### 4. Check Logs
```bash
railway logs --tail
```
Watch for errors or warnings.

---

## Database Migration (JSON → PostgreSQL)

For multi-user support, migrate to PostgreSQL:

### 1. Add PostgreSQL Plugin
```bash
railway add postgresql
```

### 2. Update app_pro.py
```python
# Replace JSON file storage with PostgreSQL
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn
```

### 3. Add psycopg2 to requirements.txt
```
psycopg2-binary==2.9.9
```

### 4. Create migration script
See `migrate_to_postgres.py` (to be created)

---

## Troubleshooting

### Build Fails
- Check `railway logs --build`
- Verify Dockerfile syntax
- Ensure all files are committed to git

### App Crashes on Start
- Check `railway logs`
- Verify environment variables are set
- Test locally with: `gunicorn app_pro:app`

### 500 Errors
- Check application logs: `railway logs --tail`
- Verify SECRET_KEY is set
- Check file permissions (data directory writable)

### Voice Logging Fails
- Verify OPENAI_API_KEY is set
- Check OpenAI account has credits
- Review logs for specific OpenAI errors

### Port Binding Issues
- Railway sets $PORT automatically
- Don't hardcode port 3000 in production
- Gunicorn should bind to `0.0.0.0:$PORT`

---

## Performance Optimization

### 1. Increase Workers
Edit `railway.json`:
```json
{
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 4 app_pro:app"
  }
}
```

### 2. Enable Caching
Add Redis:
```bash
railway add redis
```

### 3. Monitor Performance
- Use Railway's built-in metrics
- Check CPU/Memory usage
- Monitor response times

---

## Continuous Deployment

Railway automatically deploys on git push:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will:
1. Detect the push
2. Build new Docker image
3. Run health checks
4. Deploy if successful
5. Rollback if health check fails

---

## Custom Domain Setup

### 1. Via Railway CLI
```bash
railway domain add yourdomain.com
```

### 2. Update DNS Records
Add CNAME record:
```
Type: CNAME
Name: @ (or subdomain)
Value: your-app.railway.app
TTL: Auto
```

### 3. Verify
Wait for DNS propagation (5-60 minutes):
```bash
dig yourdomain.com
```

Railway automatically provisions SSL certificate.

---

## Rollback

If deployment fails:

```bash
# Via CLI
railway rollback

# Or via Dashboard
1. Go to Deployments tab
2. Find working deployment
3. Click "Redeploy"
```

---

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month includes:
  - 500 hours of usage
  - 8GB RAM
  - Shared CPU
  - 100GB bandwidth

- **Pro Plan**: $20/month includes:
  - Unlimited projects
  - 8GB RAM per service
  - Dedicated CPU
  - Priority support

Estimate for Lean tracker:
- **Light usage** (<1000 users): ~$5-10/month
- **Medium usage** (1000-10000 users): ~$20-50/month
- **Heavy usage** (>10000 users): Consider dedicated hosting

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Create issue in repo

---

## Next Steps

After successful deployment:

1. **Test thoroughly** - Run through all features
2. **Set up monitoring** - Enable alerts for errors
3. **Configure backups** - Export data regularly
4. **Update documentation** - Add public URL to README
5. **Launch!** - Share with users

---

## Deployment Log

| Date | Version | Deploy Status | URL | Notes |
|------|---------|---------------|-----|-------|
| TBD  | v1.0    | Pending       | TBD | Initial production deploy |
