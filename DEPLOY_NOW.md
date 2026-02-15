# Deploy Lean to Railway - RIGHT NOW

## Files Ready ✅
- railway.json ✅
- Procfile ✅  
- requirements.txt ✅

## Deploy Steps (10 minutes)

### 1. Install Railway CLI (if not installed)
```bash
npm i -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Project
```bash
cd ~/clawd/fitness-tracker
railway init
```

### 4. Add Environment Variables
```bash
railway variables set OPENAI_API_KEY="your-key-here"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set FLASK_ENV="production"
```

### 5. Deploy
```bash
railway up
```

### 6. Get Public URL
```bash
railway domain
```

---

## OR: Manual Railway Deployment (No CLI)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub" or "Empty Project"
4. Connect your GitHub or upload files
5. Set environment variables in Railway dashboard:
   - OPENAI_API_KEY
   - SECRET_KEY (generate random string)
   - FLASK_ENV=production
6. Railway auto-deploys
7. Add custom domain or use Railway URL

---

## What Happens After Deploy

- Railway assigns URL: lean-production-xxxx.up.railway.app
- App runs on that URL
- You can add custom domain later
- First deploy takes ~3-5 minutes

---

**READY TO DEPLOY - ALL FILES CONFIGURED**
