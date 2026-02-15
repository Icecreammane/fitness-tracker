# Lean - Quick Start Guide

## Running the App

```bash
cd ~/clawd/fitness-tracker
python3 app_pro.py
```

Open: `http://localhost:3000`

---

## New Features Quick Reference

### 1️⃣ **Onboarding**
- Shows automatically on first visit
- 3 screens: Welcome → Demo → Goal Setting
- To reset: `localStorage.clear()` in browser console

### 2️⃣ **Share Progress**
- Click 📊 icon in header
- Generates beautiful card: "Lost X lbs in Y days"
- Mobile: Opens native share sheet
- Desktop: Downloads PNG
- Saved to: `static/shares/`

### 3️⃣ **Settings**
- Click ⚙️ icon in header
- Export data (JSON download)
- Privacy policy (placeholder)
- Delete account (double confirmation)

### 4️⃣ **Mobile Optimization**
- All touch targets ≥44px
- Responsive design (breakpoint: 600px)
- Horizontal scrolling tabs
- Native share API support

### 5️⃣ **Error Handling**
- Red banner on API failures
- Retry button to re-fetch
- Loading spinners
- Toast notifications for actions

---

## File Structure

```
fitness-tracker/
├── app_pro.py                 # Main Flask app
├── templates/
│   └── dashboard_v3.html      # Dashboard (UPDATED)
├── static/
│   └── shares/                # Share images (NEW)
├── fitness_data.json          # User data
└── user_goals.json            # Goals
```

---

## API Endpoints

### Existing
- `GET /api/today` - Today's stats
- `GET /api/goal_projection` - Progress
- `GET /api/last_14_days` - Trend data

### New
- `POST /api/save_share_image` - Save share card
- `GET /api/export_data` - Export user data

---

## Testing Checklist

**First Time User Flow:**
1. Visit app → Onboarding shows
2. Click through 3 screens
3. Dashboard loads

**Share Feature:**
1. Click 📊 in header
2. Card generates
3. Share/download works

**Settings:**
1. Click ⚙️ in header
2. Try "Export Data"
3. Try "Delete Account" (test confirmation)

**Mobile:**
1. Open DevTools → Mobile view
2. Check touch targets
3. Test horizontal tab scroll
4. Test share feature

**Error Handling:**
1. Disconnect internet
2. Try to refresh
3. Error banner shows
4. Click "Retry"

---

## Deployment Notes

### Before Launch:
1. Replace `demo@lean.app` with real user data
2. Implement actual authentication
3. Replace JSON storage with database
4. Add real privacy policy
5. Set up analytics
6. Test voice recording on HTTPS

### Environment Variables:
```bash
export OPENAI_API_KEY="your-key"  # For voice transcription
export FLASK_ENV="production"
```

### Production Command:
```bash
gunicorn -w 4 -b 0.0.0.0:3000 app_pro:app
```

---

## Browser Support

✅ Chrome (desktop + mobile)  
✅ Safari (desktop + mobile)  
✅ Firefox (desktop + mobile)  
✅ Edge  

**Note:** Voice recording requires HTTPS in production

---

## Known Limitations

1. **Onboarding** - Stored in localStorage (clears if user clears data)
2. **Share Feature** - Desktop doesn't have native share (downloads instead)
3. **Data Storage** - JSON files (not scalable, replace with DB)
4. **Authentication** - Not implemented (add before multi-user)

---

## Future Enhancements

- [ ] History tab with filtering
- [ ] Progress photos upload & comparison
- [ ] Meal prep generator (already in code, needs UI)
- [ ] AI body prediction with actual image generation
- [ ] Social features (follow friends, compare progress)
- [ ] Streak rewards & gamification
- [ ] Apple Health / Google Fit integration

---

## Support

Questions? Check:
- `LAUNCH_FEATURES.md` - Full feature documentation
- `app_pro.py` - Backend implementation
- `templates/dashboard_v3.html` - Frontend code

---

**Status:** ✅ Ready for Launch  
**Version:** 2.0  
**Last Updated:** 2025-02-13
