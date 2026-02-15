# 📸 Photo Macro Logger - Quick Start

## 30-Second Setup

```bash
# 1. Install vision model (one-time, ~4GB download)
ollama pull llava:latest

# 2. Start the tracker
cd ~/clawd/fitness-tracker
python3 app.py

# 3. Open browser
open http://localhost:3000
```

## How to Use

1. **Click**: "📸 Snap Food Photo" button in Quick Log widget
2. **Select**: A photo of your meal
3. **Wait**: 30-60 seconds for AI analysis
4. **Review**: Auto-populated macro fields
5. **Adjust**: Change values if needed
6. **Log**: Click "Log It! 🚀"

## Example Results

### Grilled Chicken Breast
- **Detected**: Grilled chicken breast (8oz)
- **Macros**: 250 cal, 45g protein, 0g carbs, 7g fat
- **Confidence**: High
- **Time**: ~35 seconds

### Salad Bowl
- **Detected**: Mixed green salad with chicken
- **Macros**: 320 cal, 30g protein, 15g carbs, 18g fat
- **Confidence**: Medium
- **Time**: ~40 seconds

## Tips for Best Results

✅ **DO:**
- Take photos in good lighting
- Show the full meal clearly
- Get close enough to see details
- Use common foods (chicken, rice, salads, etc.)

❌ **DON'T:**
- Take photos in very dim lighting
- Blur the image or shoot from far away
- Expect perfect accuracy on complex mixed dishes
- Forget to review and adjust the estimates!

## Troubleshooting

### "Could not connect to Ollama"
```bash
# Check if ollama is running
ollama list

# If not, start it
ollama serve
```

### "Request timed out"
- First request after model download takes longer (60-90s)
- Model is loading into memory
- Subsequent requests will be faster (20-30s)

### "Analysis failed"
- Try a different photo with better lighting
- Make sure the food is clearly visible
- Fall back to manual entry if needed

## What Gets Analyzed

The AI looks at:
- **Food type** (chicken, rice, vegetables, etc.)
- **Portion size** (small, medium, large, or specific measurements)
- **Preparation method** (grilled, fried, boiled)
- **Visible ingredients** (sauce, toppings, sides)

Then estimates:
- Calories
- Protein (grams)
- Carbs (grams)
- Fat (grams)
- Confidence level (high/medium/low)
- Notes (any relevant observations)

## Privacy & Performance

- **100% Local**: All analysis happens on your Mac
- **No Cloud**: Images never leave your computer
- **No Storage**: Photos deleted after analysis
- **Memory**: Uses ~4-5GB RAM while model is loaded
- **Speed**: 20-60 seconds per photo

## Need Help?

See `PHOTO_MACRO_FEATURE.md` for detailed documentation.

---

**Status**: ✅ Production Ready  
**Built**: February 8, 2026
