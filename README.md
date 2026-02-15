# Lean - Smart Calorie Tracking

**Frictionless meal tracking with AI-powered insights**

## Features

### 🎤 Voice Logging
- Hold button → speak your meal → instant log
- Whisper AI transcription + GPT-4o macro estimation
- Zero typing required

### 📸 Photo Meal Scanning
- Snap food photo → AI analyzes → one-tap confirm
- GPT-4o Vision recognizes food & estimates macros
- Fastest logging method available

### 🎯 Science-Based Goal Calculator
- Enter current weight, goal, timeline
- Mifflin-St Jeor BMR calculation
- Activity-adjusted TDEE
- Personalized calorie & protein targets
- Safety warnings for aggressive rates

### 📊 Smart Dashboard
- 14-day calorie graph with target line
- Goal projection (on pace / slipping / off track)
- Deficit tracking & banking
- Streak counter
- Progress photos with date/weight

### 🍽️ Meal Prep Generator
- Analyzes your eating history
- Generates 7-day plans from proven meals
- Auto-creates shopping lists
- Prioritizes high-protein options

### 📈 Progress Tracking
- Before/after photo grid
- Weight progression over time
- AI body transformation prediction (coming soon)

## Tech Stack
- **Backend:** Flask (Python)
- **AI:** OpenAI GPT-4o + Whisper
- **Frontend:** Vanilla JS + Chart.js
- **Storage:** JSON files (ready for DB migration)

## Running Locally
```bash
cd fitness-tracker
python3 app_pro.py
# Open http://localhost:3000
```

## Deployment Ready
- Docker support
- Railway/Heroku compatible
- Environment variables for API keys
- Production WSGI server configs

## Product Philosophy
**Speed = dopamine. Friction = failure.**

Lean isn't about gamification or XP systems. It's about making calorie tracking so fast and effortless that you actually do it every day. When tracking is instant, accountability becomes automatic.

## Built With
- OpenAI GPT-4o (vision + text)
- OpenAI Whisper (speech-to-text)
- Chart.js (visualizations)
- Flask (backend)
- Pure CSS (no frameworks)

---

**Status:** Production-ready MVP  
**Live Demo:** http://10.0.0.18:3000  
**Created:** February 2026
