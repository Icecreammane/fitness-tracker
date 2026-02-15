# 🚀 QUICK DEPLOY - LEAN TO RAILWAY

## STATUS: ⚠️ READY TO DEPLOY (Manual Auth Required)

---

## ONE-TIME SETUP (30 seconds)

```bash
cd ~/clawd/fitness-tracker
railway login
```

*Opens browser → Login → Authorize CLI*

---

## DEPLOY (One command, 3-5 minutes)

```bash
./deploy.sh
```

This automatically:
- ✅ Creates Railway project
- ✅ Sets OPENAI_API_KEY
- ✅ Sets SECRET_KEY
- ✅ Deploys Docker container
- ✅ Generates public domain

---

## GET URL

```bash
railway domain
```

Output: `https://lean-production-xxxx.railway.app`

---

## TEST (In browser or curl)

1. **Dashboard:** https://YOUR-URL/
2. **Today's data:** https://YOUR-URL/api/today
3. **Goal calc:** POST to /api/calculate_goals
4. **Voice log:** POST audio to /api/voice_log

---

## IF ISSUES

```bash
railway logs --tail    # View logs
railway status         # Check status
railway variables      # Check env vars
```

---

## REPORT FORMAT

```
✅ DEPLOYED
URL: https://lean-xxx.railway.app
Status: All features tested and working
Issues: [none or list]
```

---

**That's it! Login once, deploy once, done.** 🎯
