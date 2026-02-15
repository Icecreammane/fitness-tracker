#!/usr/bin/env python3
import json
from datetime import datetime

# Load existing data
with open('fitness_data.json', 'r') as f:
    data = json.load(f)

# Feb 11 meals - lunch at 12:08 PM, dinner at 6:12 PM
feb11_lunch_time = datetime(2026, 2, 11, 12, 8).timestamp()
feb11_dinner_time = datetime(2026, 2, 11, 18, 12).timestamp()

feb11_meals = [
    {
        "date": "2026-02-11",
        "timestamp": feb11_lunch_time,
        "description": "2 chicken wraps (tortilla) + baby carrots + hummus",
        "calories": 480,
        "protein": 23,
        "carbs": 43,
        "fat": 21
    },
    {
        "date": "2026-02-11",
        "timestamp": feb11_dinner_time,
        "description": "Beef Hash Brown Cottage Cheese Bowl (6 oz ground beef, 1 cup hash browns, 3/4 cup cottage cheese)",
        "calories": 730,
        "protein": 60,
        "carbs": 31,
        "fat": 41
    }
]

# Add to food_logs
data['food_logs'].extend(feb11_meals)

# Sort by timestamp
data['food_logs'].sort(key=lambda x: x['timestamp'])

# Save
with open('fitness_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Added Feb 11 meals")
print(f"  12:08 PM - Chicken wraps + carrots (480 cal, 23g P)")
print(f"  06:12 PM - Beef bowl (730 cal, 60g P)")
print(f"Total food logs: {len(data['food_logs'])}")
