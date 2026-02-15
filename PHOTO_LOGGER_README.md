# 📸 Photo Food Logger

**Status:** ✅ COMPLETE  
**Built:** 2026-02-02 08:04 CST

## What It Does

Send a food photo to Jarvis → Get automatic macro tracking

**Flow:**
1. Ross sends food photo via Telegram
2. GPT-4o Vision analyzes the image
3. Extracts nutritional data (calories, protein, carbs, fat)
4. Auto-logs to fitness tracker
5. Confirms back with macro breakdown

## Usage

**For Ross:**
Just send food photos to Jarvis on Telegram. That's it.

**Manual Testing:**
```bash
cd /Users/clawdbot/clawd/fitness-tracker
python3 food_photo_handler.py <image_path>
```

## Components

### 1. `photo_analyzer.py`
- Uses OpenAI GPT-4o Vision API
- Analyzes food images
- Extracts macro estimates
- Returns JSON with nutritional data

### 2. `food_photo_handler.py`
- Integrates analyzer with fitness tracker
- Logs macros via API
- Formats user-friendly confirmations

### 3. Telegram Integration (Jarvis)
- Detects incoming food photos
- Calls food_photo_handler.py
- Sends formatted confirmation back

## Example Output

```
✅ Logged: Banana

📊 Macros:
• 105 calories
• 1g protein
• 27g carbs
• 0g fat

📏 Portion: medium banana ~120g
🎯 Confidence: high

💡 The banana looks ripe and is of a typical medium size.
```

## API Requirements

- OpenAI API key (set as `OPENAI_API_KEY` env var)
- Fitness tracker running on `localhost:3000`

## Dependencies

```bash
pip3 install openai requests pillow
```

## Accuracy Notes

- **High confidence:** Single, clear food items (fruits, single proteins)
- **Medium confidence:** Plated meals, multiple items
- **Low confidence:** Mixed dishes, unclear portions

Ross can always override estimates manually if needed.

## Future Enhancements

- Multi-item meal recognition
- Meal type auto-detection (breakfast/lunch/dinner)
- Historical accuracy tracking
- Custom portion calibration per user

---

**Built autonomously by Jarvis while Ross was at work** 🤖
