# 📸 Photo Macro Logger - README

## TL;DR
Snap a meal photo → AI estimates macros → review → log. **100% local. No cloud.**

## Quick Start (30 seconds)
```bash
cd ~/clawd/fitness-tracker
./venv/bin/python3 app.py
open http://localhost:3000
# Click "📸 Snap Food Photo" button!
```

## What You Get
- **AI-powered macro estimation** from meal photos
- **Local processing** (Ollama + LLaVA vision model)
- **Instant results** (8-60 seconds)
- **User control** (review and adjust before logging)
- **Privacy-first** (images never leave your Mac)

## How It Works
1. Take/upload photo of your meal
2. Local AI analyzes it (LLaVA vision model)
3. Estimates: calories, protein, carbs, fat
4. Auto-fills the form fields
5. You review/adjust if needed
6. Log it!

## Performance
- **First use**: 60-90 seconds (model loading)
- **After that**: 8-10 seconds per photo
- **Accuracy**: Good for simple foods, reasonable for complex dishes
- **Memory**: Uses ~4-5GB RAM while active

## Files
- `local_vision_analyzer.py` - Vision model interface
- `app.py` - API endpoint: POST `/api/analyze-food-photo`
- `dashboard_enhanced.html` - UI integration
- `test_photo_feature.py` - Test suite

## Documentation
- **Quick Start**: `PHOTO_FEATURE_QUICKSTART.md`
- **Full Docs**: `PHOTO_MACRO_FEATURE.md`
- **Build Summary**: `BUILD_PHOTO_MACRO_INTEGRATION.md`
- **Test Results**: `TEST_RESULTS.md`
- **Completion Report**: `SUBAGENT_COMPLETION_REPORT.md`

## Status
✅ **Production Ready**  
✅ **Tested with real photos**  
✅ **Privacy-preserving (100% local)**  
✅ **Documentation complete**  
🚀 **Ready to use NOW**

## Need Help?
See the docs above or just try it - it's intuitive!

---
**Built**: Feb 8, 2026 | **Status**: Shipped ✅
