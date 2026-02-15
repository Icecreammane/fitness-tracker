#!/usr/bin/env python3
import json
from datetime import datetime

# Load existing data
with open('fitness_data.json', 'r') as f:
    data = json.load(f)

# Feb 9 meals - dinner around 6:40 PM, late night at 11:44 PM
feb9_dinner_time = datetime(2026, 2, 9, 18, 40).timestamp()
feb9_latenight_time = datetime(2026, 2, 9, 23, 44).timestamp()

feb9_meals = [
    {
        "date": "2026-02-09",
        "timestamp": feb9_dinner_time,
        "description": "10 slices Black Label bacon + crispy chicken sandwich + fried onions + Santitas chips",
        "calories": 950,
        "protein": 48,
        "carbs": 65,
        "fat": 52
    },
    {
        "date": "2026-02-09",
        "timestamp": feb9_latenight_time,
        "description": "4 hamburger sliders + glass of white wine",
        "calories": 620,
        "protein": 32,
        "carbs": 48,
        "fat": 26
    }
]

# Add to food_logs
data['food_logs'].extend(feb9_meals)

# Remove the accidentally logged Feb 12 entry (last one)
if data['food_logs'][-1]['description'] == "10 slices Black Label bacon + crispy chicken sandwich + fried onions + Santitas chips":
    data['food_logs'].pop()

# Sort by timestamp
data['food_logs'].sort(key=lambda x: x['timestamp'])

# Save
with open('fitness_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Added Feb 9 meals")
print(f"Total food logs: {len(data['food_logs'])}")
