# 🚀 Deploy Lean to Railway - Quick Guide

**Status:** Ready to deploy (configuration updated for app_pro.py)

## Prerequisites Complete ✅
- Railway CLI installed
- Dockerfile updated for app_pro.py
- Procfile updated
- railway.json configured
- OpenAI API key available

## Step 1: Login to Railway (MANUAL - Ross needs to do this)

```bash
cd ~/clawd/fitness-tracker
railway login
```

This will open your browser for authentication.

## Step 2: Initialize Project

```bash
railway init
```

When prompted:
- Project name: `lean-fitness-tracker` (or your choice)
- Confirm creation

## Step 3: Set Environment Variables

```bash
# Set OpenAI API key
railway variables set OPENAI_API_KEY="your-openai-api-key-here"

# Set Flask secret (generate new one)
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Set port (Railway provides $PORT automatically)
railway variables set PORT=3000
```

## Step 4: Deploy

```bash
railway up
```

This will:
1. Build Docker image
2. Push to Railway
3. Start the service

## Step 5: Generate Public Domain

```bash
railway domain
```

This generates a public URL like: `https://lean-xxx.railway.app`

## Step 6: Test Features

Test each endpoint:

### Dashboard
```bash
curl https://YOUR-RAILWAY-URL.railway.app/
```

### Voice Logging
```bash
curl -X POST https://YOUR-RAILWAY-URL.railway.app/api/voice_log \
  -F "audio=@test_audio.webm"
```

### Add Meal
```bash
curl -X POST https://YOUR-RAILWAY-URL.railway.app/api/add_meal \
  -H "Content-Type: application/json" \
  -d '{"description":"Chicken breast","calories":300,"protein":50}'
```

### Goal Calculator
```bash
curl -X POST https://YOUR-RAILWAY-URL.railway.app/api/calculate_goals \
  -H "Content-Type: application/json" \
  -d '{"current_weight":240,"goal_weight":200,"timeline_weeks":20}'
```

## Alternative: Deploy via Railway Web UI

If CLI doesn't work:

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Connect your GitHub account
4. Push fitness-tracker to GitHub
5. Select the repo in Railway
6. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
7. Railway auto-deploys from Dockerfile

## Troubleshooting

### Build fails
- Check Dockerfile syntax
- Verify requirements.txt includes all dependencies
- Check Railway build logs: `railway logs`

### App crashes
- Check for missing environment variables
- View runtime logs: `railway logs --tail`
- Verify port binding (Railway uses $PORT)

### Voice logging fails
- Verify OPENAI_API_KEY is set correctly
- Check if OpenAI package is installed
- Test locally first

## Post-Deployment

Once deployed:

1. Save the URL
2. Test all features thoroughly
3. Monitor logs for errors
4. Update DNS if using custom domain

---

**Ready to go!** Just need Ross to run `railway login` then execute the deploy script.
