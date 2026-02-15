# Quick Start Guide - FitTrack Pro

Get your fitness tracker running in 5 minutes.

## 1. Setup (First Time Only)

```bash
cd ~/clawd/fitness-tracker

# Run automated setup
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Generate SECRET_KEY
- Create .env file

## 2. Configure Stripe

Get your Stripe test keys:

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your keys
3. Edit `.env` file:

```bash
# Open in editor
nano .env  # or: code .env

# Add your keys:
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

Save and close.

## 3. Start the App

```bash
./start.sh
```

Visit **http://localhost:3000** 🎉

## 4. Test It Out

1. **Sign up** for an account
2. **Log some food:**
   - Chicken breast: 200 cal, 40g protein
   - Rice: 200 cal, 45g carbs
3. **Log your weight:** Enter current weight
4. **Test payment** (optional):
   - Go to /pricing
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry, any CVC

## 5. Check Your Data

```bash
# View user data files
ls -la data/

# View users
cat data/users.json
```

Each user gets their own `<user_id>_fitness.json` file.

## Next Steps

### Set Up Webhooks (For Local Testing)

If you want to test subscription webhooks locally:

```bash
# Install ngrok
brew install ngrok

# In terminal 1: Start app
./start.sh

# In terminal 2: Start ngrok
ngrok http 3000

# Copy the ngrok URL (https://abc123.ngrok.io)
# Follow Stripe webhook setup in STRIPE_SETUP.md
```

### Deploy to Production

Ready to launch? See **DEPLOYMENT.md** for:
- Railway.app (easiest)
- Heroku
- Fly.io
- Docker

### Launch Your Product

When ready to go live:
1. Deploy to production
2. Switch Stripe to live mode
3. Set up live webhooks
4. Post on Reddit (see LAUNCH_MATERIALS.md)
5. Tweet thread (templates ready)
6. Share with friends!

## Common Commands

```bash
# Start app
./start.sh

# View logs (while running)
# Press Ctrl+C to stop

# Reset everything
rm -rf venv data/*.json .env
./setup.sh  # Start fresh

# Check what's running
lsof -i :3000  # See what's on port 3000
```

## File Structure

```
fitness-tracker/
├── app_saas.py              # Main app (run this)
├── templates/               # HTML pages
├── data/                    # User data (created on first run)
├── .env                     # Your config (secrets here)
├── requirements.txt         # Python packages
└── *.md                     # Documentation
```

## Troubleshooting

**Port 3000 already in use?**
```bash
# Kill the process
lsof -i :3000
kill -9 <PID>
```

**Module not found error?**
```bash
# Make sure virtual env is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Stripe errors?**
- Check your keys are correct in `.env`
- Make sure you're using test keys (start with `sk_test_` and `pk_test_`)

**Can't access /dashboard?**
- Make sure you're logged in
- Check browser console for errors
- Try signing up again

## Need Help?

1. **Check the docs:**
   - STRIPE_SETUP.md - Stripe configuration
   - DEPLOYMENT.md - Deploy to production
   - TEST_PLAN.md - Testing guide
   - LAUNCH_MATERIALS.md - Marketing copy

2. **Check logs:**
   - Look at terminal output for errors
   - Check Stripe dashboard for payment issues

3. **Start fresh:**
   ```bash
   rm -rf data/*.json
   ./start.sh
   ```

---

**You're ready to go!** Build, test, deploy, launch. 💪
