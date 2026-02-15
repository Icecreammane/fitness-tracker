# 🚀 Quick Start - New Features

## Start the Server
```bash
cd ~/clawd/fitness-tracker
python3 app_pro.py
```

Open: **http://localhost:3000**

---

## 🔥 Feature 1: Streak Counter

**Where:** Dashboard stats card (automatic)

**What it shows:**
- Current streak (flame icon + number)
- Updates on page load
- Counts consecutive days with logged meals

**Test:**
```bash
curl http://localhost:3000/api/streak | python3 -m json.tool
```

---

## ⚖️ Feature 2: Weight Tracking

**Where:** Click the ⚖️ button in dashboard header

**How to use:**
1. Click ⚖️ icon
2. Enter weight (e.g., 185.5)
3. Add optional notes
4. Click "Save Weight"
5. View chart with 7d/30d/90d tabs

**Test:**
```bash
# Log weight
curl -X POST http://localhost:3000/api/weight \
  -H "Content-Type: application/json" \
  -d '{"weight": 180.5, "notes": "Morning weigh-in"}'

# View history
curl "http://localhost:3000/api/weight/history?days=30"
```

---

## 📊 Feature 3: Progress Card

**Where:** Click the 📊 button in dashboard header

**What it does:**
1. Shows weekly stats (weight lost, streak, meals, deficit)
2. Generates Instagram-ready card (1080x1350px)
3. Click "Download Card" to save PNG
4. Click "Share to Instagram" on mobile

**Test:**
```bash
curl http://localhost:3000/api/progress_card | python3 -m json.tool
```

---

## 🧪 Run All Tests
```bash
cd ~/clawd/fitness-tracker
python3 test_new_features.py
```

Expected: 4/4 tests passing

---

## 📊 Run Visual Demo
```bash
cd ~/clawd/fitness-tracker
./test_demo.sh
```

Shows all 3 features with live data

---

## 📱 UI Buttons Reference

| Button | Feature | Location |
|--------|---------|----------|
| 🔥 | Streak (auto) | Stats card |
| ⚖️ | Weight tracking | Header |
| 📊 | Progress cards | Header |

---

## 🐛 Troubleshooting

**Port 3000 in use:**
```bash
pkill -f "python3 app_pro.py"
python3 app_pro.py
```

**Tests fail:**
- Ensure server is running on port 3000
- Check `fitness_data.json` exists
- Run from `fitness-tracker` directory

**Modal doesn't open:**
- Check browser console for errors
- Verify templates are included in dashboard_v3.html
- Refresh page (Cmd+R)

---

## 📖 Full Documentation

- **Technical Specs:** `BUILD_FEATURES_COMPLETE.md`
- **Executive Summary:** `SUBAGENT_COMPLETION_SUMMARY.md`
- **Test Suite:** `test_new_features.py`
- **Demo Script:** `test_demo.sh`

---

**All features tested and working!** ✅
