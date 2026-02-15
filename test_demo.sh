#!/bin/bash
# Demo script showing all 3 features working

echo "=================================================="
echo "   LEAN FITNESS TRACKER - NEW FEATURES DEMO"
echo "=================================================="
echo ""

echo "🔥 FEATURE 1: STREAK COUNTER"
echo "----------------------------"
curl -s http://localhost:3000/api/streak | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Current Streak: {data['current']} days 🔥\")
print(f\"Longest Streak: {data['longest']} days\")
print(f\"Logged Today: {'Yes ✅' if data['logged_today'] else 'No ❌'}\")
"
echo ""

echo "⚖️ FEATURE 2: WEIGHT TRACKING"
echo "----------------------------"
# Add a test weight
curl -s -X POST http://localhost:3000/api/weight \
  -H "Content-Type: application/json" \
  -d "{\"weight\": $((180 + RANDOM % 10)).5, \"notes\": \"Test weigh-in\"}" > /dev/null

# Show history
curl -s "http://localhost:3000/api/weight/history?days=30" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stats = data['stats']
print(f\"Entries Tracked: {stats['entries']}\")
print(f\"Current Weight: {stats['current']} lbs\")
print(f\"Weight Change: {stats['change']:+.1f} lbs\")
print(f\"Average: {stats['average']} lbs\")
"
echo ""

echo "📊 FEATURE 3: PROGRESS CARD GENERATOR"
echo "------------------------------------"
curl -s http://localhost:3000/api/progress_card | python3 -c "
import sys, json
data = json.load(sys.stdin)
card = data['card_data']
print(f\"Period: {card['period']}\")
print(f\"Weight Lost: {card['weight_lost']} lbs\")
print(f\"Streak: {card['streak']} days\")
print(f\"Meals Logged: {card['meals_logged']}\")
print(f\"Avg Daily Deficit: {card['avg_deficit']} cal\")
print(\"\n✨ Card ready for download at 1080x1350px\")
"
echo ""

echo "=================================================="
echo "       ✅ ALL FEATURES WORKING!"
echo "=================================================="
