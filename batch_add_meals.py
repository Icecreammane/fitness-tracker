#!/usr/bin/env python3
import json
from datetime import datetime

with open('fitness_data.json', 'r') as f:
    data = json.load(f)

# Feb 8 Super Bowl meals
feb8_meals = [
    {
        "date": "2026-02-08",
        "timestamp": datetime(2026, 2, 8, 14, 17).timestamp(),
        "description": "2 Italian subs from deli (Super Bowl party)",
        "calories": 1400,
        "protein": 65,
        "carbs": 110,
        "fat": 70
    },
    {
        "date": "2026-02-08",
        "timestamp": datetime(2026, 2, 8, 20, 14).timestamp(),
        "description": "Super Bowl party snacks: M&M cookie, jalapeño poppers, chips+dip, pretzels",
        "calories": 940,
        "protein": 22,
        "carbs": 97,
        "fat": 50
    }
]

# Remove test entries from Feb 8
data['food_logs'] = [f for f in data['food_logs'] if not (f['date'] == '2026-02-08' and (f.get('description') is None or 'Test' in str(f.get('description', ''))))]

# Add new meals
data['food_logs'].extend(feb8_meals)

# Sort
data['food_logs'].sort(key=lambda x: x['timestamp'])

with open('fitness_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Added Feb 8 Super Bowl meals")
print(f"  2:17 PM - 2 Italian subs (1,400 cal, 65g P)")
print(f"  8:14 PM - Party snacks (940 cal, 22g P)")
print(f"Total food logs: {len(data['food_logs'])}")
