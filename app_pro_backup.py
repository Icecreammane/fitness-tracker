#!/usr/bin/env python3
"""
Professional Fitness Dashboard - Frictionless meal tracking
Built for speed, simplicity, and visual clarity
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from gamification_system import GamificationEngine

app = Flask(__name__)

DATA_FILE = 'fitness_data.json'
gamification = GamificationEngine()

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def dashboard():
    return render_template('dashboard_v3.html')

@app.route('/api/today')
def get_today():
    """Get today's complete data"""
    data = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's meals
    today_meals = [m for m in data['meals'] if m['date'] == today]
    
    # Calculate totals
    total_cal = sum(m['calories'] for m in today_meals)
    total_protein = sum(m['protein'] for m in today_meals)
    total_carbs = sum(m.get('carbs', 0) for m in today_meals)
    total_fat = sum(m.get('fat', 0) for m in today_meals)
    
    # Goals
    settings = data.get('settings', {})
    cal_goal = settings.get('daily_calorie_goal', 2200)
    protein_goal = settings.get('daily_protein_goal', 200)
    
    return jsonify({
        'date': today,
        'meals': today_meals,
        'totals': {
            'calories': total_cal,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        },
        'goals': {
            'calories': cal_goal,
            'protein': protein_goal
        },
        'progress': {
            'calories_pct': round((total_cal / cal_goal) * 100),
            'protein_pct': round((total_protein / protein_goal) * 100)
        }
    })

@app.route('/api/goal_projection')
def get_goal_projection():
    """Calculate goal projection based on actual progress"""
    data = load_data()
    
    # Load user goals (would come from database in production)
    try:
        with open('user_goals.json') as f:
            goals = json.load(f)
    except:
        return jsonify({'error': 'Goals not set'})
    
    # Calculate actual deficit over time
    meals_by_date = defaultdict(list)
    for meal in data['meals']:
        meals_by_date[meal['date']].append(meal)
    
    start_date = datetime.strptime(goals['started_date'], '%Y-%m-%d')
    today = datetime.now()
    days_tracked = (today - start_date).days
    
    # Calculate cumulative deficit
    total_deficit = 0
    days_under_target = 0
    logging_streak = 0
    current_streak = 0
    last_logged_date = None
    
    for i in range(days_tracked + 1):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        meals = meals_by_date[date]
        
        if meals:
            day_cal = sum(m['calories'] for m in meals)
            day_deficit = goals['daily_calorie_goal'] - day_cal
            total_deficit += day_deficit
            
            if day_deficit > 0:
                days_under_target += 1
            
            # Calculate logging streak
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if last_logged_date:
                gap = (date_obj - last_logged_date).days
                if gap == 1:
                    current_streak += 1
                else:
                    current_streak = 1
            else:
                current_streak = 1
            
            logging_streak = max(logging_streak, current_streak)
            last_logged_date = date_obj
    
    # Calculate lbs lost (3500 cal = 1 lb)
    lbs_lost = total_deficit / 3500
    current_weight = goals['current_weight'] - lbs_lost
    
    # Calculate required vs actual rate
    target_date = datetime.strptime(goals['target_date'], '%Y-%m-%d')
    days_to_goal = (target_date - today).days
    lbs_to_goal = current_weight - goals['goal_weight']
    
    required_weekly_loss = (lbs_to_goal / days_to_goal) * 7 if days_to_goal > 0 else 0
    actual_weekly_loss = (lbs_lost / days_tracked) * 7 if days_tracked > 0 else 0
    
    # Determine status
    if actual_weekly_loss >= required_weekly_loss * 0.9:
        status = 'on_pace'
        status_text = '✅ On Pace'
    elif actual_weekly_loss >= required_weekly_loss * 0.7:
        status = 'slipping'
        needed = int((required_weekly_loss - actual_weekly_loss) * 500)  # cal per day
        status_text = f'⚠️ Slipping (need {needed} more cal deficit/day)'
    else:
        status = 'off_track'
        new_weeks = int(lbs_to_goal / actual_weekly_loss) if actual_weekly_loss > 0 else 52
        status_text = f'❌ Off Track (reset to {new_weeks} weeks)'
    
    return jsonify({
        'current_weight': round(current_weight, 1),
        'goal_weight': goals['goal_weight'],
        'lbs_to_goal': round(lbs_to_goal, 1),
        'lbs_lost': round(lbs_lost, 1),
        'target_date': goals['target_date'],
        'days_to_goal': days_to_goal,
        'status': status,
        'status_text': status_text,
        'required_weekly_loss': round(required_weekly_loss, 2),
        'actual_weekly_loss': round(actual_weekly_loss, 2),
        'total_deficit': int(total_deficit),
        'days_tracked': days_tracked,
        'days_under_target': days_under_target,
        'logging_streak': logging_streak,
        'current_streak': current_streak
    })

@app.route('/api/week')
def get_week():
    """Get last 7 days summary"""
    data = load_data()
    
    # Calculate last 7 days
    meals_by_date = defaultdict(list)
    for meal in data['meals']:
        meals_by_date[meal['date']].append(meal)
    
    today = datetime.now()
    week_data = []
    
    for i in range(6, -1, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        meals = meals_by_date[date]
        
        day_cal = sum(m['calories'] for m in meals)
        day_protein = sum(m['protein'] for m in meals)
        
        week_data.append({
            'date': date,
            'day': (today - timedelta(days=i)).strftime('%a'),
            'calories': day_cal,
            'protein': day_protein,
            'meal_count': len(meals)
        })
    
    return jsonify(week_data)

@app.route('/api/last_14_days')
def get_last_14_days():
    """Get last 14 days for trend chart"""
    data = load_data()
    
    # Calculate last 14 days
    meals_by_date = defaultdict(list)
    for meal in data['meals']:
        meals_by_date[meal['date']].append(meal)
    
    today = datetime.now()
    trend_data = []
    
    for i in range(13, -1, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        meals = meals_by_date[date]
        
        day_cal = sum(m['calories'] for m in meals)
        day_protein = sum(m['protein'] for m in meals)
        
        trend_data.append({
            'date': date,
            'day': (today - timedelta(days=i)).strftime('%a'),
            'calories': day_cal,
            'protein': day_protein
        })
    
    return jsonify(trend_data)

@app.route('/api/meal_history')
def get_meal_history():
    """Get all meals with dates for history view"""
    data = load_data()
    
    # Group meals by date
    meals_by_date = defaultdict(list)
    for meal in data['meals']:
        meals_by_date[meal['date']].append(meal)
    
    # Sort dates descending (newest first)
    sorted_dates = sorted(meals_by_date.keys(), reverse=True)
    
    history = []
    for date in sorted_dates:
        meals = meals_by_date[date]
        day_cal = sum(m['calories'] for m in meals)
        day_protein = sum(m['protein'] for m in meals)
        
        # Format date
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %B %d')
        
        history.append({
            'date': date,
            'formatted_date': formatted_date,
            'meals': meals,
            'totals': {
                'calories': day_cal,
                'protein': day_protein
            }
        })
    
    return jsonify(history)

@app.route('/api/generate_meal_plan')
def generate_meal_plan():
    """Generate a 7-day meal plan from meal history"""
    data = load_data()
    settings = data.get('settings', {})
    cal_target = settings.get('daily_calorie_goal', 2200)
    protein_target = settings.get('daily_protein_goal', 200)
    
    # Analyze meal library - filter out meals without descriptions
    meals = [m for m in data['meals'] if m.get('description')]
    
    if len(meals) < 5:
        return jsonify({'error': 'Not enough meals logged to generate a plan. Log at least 5 meals first.'})
    
    # Categorize meals by type and quality
    breakfast_meals = []
    lunch_meals = []
    dinner_meals = []
    snacks = []
    
    for meal in meals:
        cal = meal['calories']
        protein = meal['protein']
        time = int(meal['time'].split(':')[0])
        
        # Categorize by time and nutritional value
        if time < 11:  # Breakfast
            breakfast_meals.append(meal)
        elif time < 16:  # Lunch
            lunch_meals.append(meal)
        elif time < 21:  # Dinner
            dinner_meals.append(meal)
        else:  # Snacks
            snacks.append(meal)
    
    # Score meals by protein density and calorie efficiency
    def score_meal(meal):
        protein_ratio = meal['protein'] / max(meal['calories'], 1) * 100
        return protein_ratio
    
    # Sort by quality
    breakfast_meals.sort(key=score_meal, reverse=True)
    lunch_meals.sort(key=score_meal, reverse=True)
    dinner_meals.sort(key=score_meal, reverse=True)
    snacks.sort(key=score_meal, reverse=True)
    
    # Generate 7-day plan
    plan = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for i, day in enumerate(days):
        day_meals = []
        day_cal = 0
        day_protein = 0
        
        # Pick breakfast (rotate through top options)
        if breakfast_meals:
            breakfast = breakfast_meals[i % len(breakfast_meals)]
            day_meals.append({**breakfast, 'meal_type': 'Breakfast'})
            day_cal += breakfast['calories']
            day_protein += breakfast['protein']
        
        # Pick lunch (high protein priority)
        if lunch_meals:
            lunch = lunch_meals[i % len(lunch_meals)]
            day_meals.append({**lunch, 'meal_type': 'Lunch'})
            day_cal += lunch['calories']
            day_protein += lunch['protein']
        
        # Pick dinner (largest meal, high protein)
        if dinner_meals:
            dinner = dinner_meals[i % len(dinner_meals)]
            day_meals.append({**dinner, 'meal_type': 'Dinner'})
            day_cal += dinner['calories']
            day_protein += dinner['protein']
        
        # Add snack if needed to hit targets
        remaining_cal = cal_target - day_cal
        if remaining_cal > 100 and snacks:
            snack = snacks[i % len(snacks)]
            if snack['calories'] <= remaining_cal + 200:  # Allow 200 cal buffer
                day_meals.append({**snack, 'meal_type': 'Snack'})
                day_cal += snack['calories']
                day_protein += snack['protein']
        
        plan.append({
            'day': day,
            'meals': day_meals,
            'totals': {
                'calories': day_cal,
                'protein': day_protein,
                'deficit': cal_target - day_cal
            }
        })
    
    # Generate shopping list
    shopping_list = defaultdict(int)
    ingredients_map = {
        'banana': ['banana', 1],
        'chicken': ['chicken breast', 'lb'],
        'beef': ['ground beef', 'lb'],
        'cottage cheese': ['cottage cheese', 'oz'],
        'hash browns': ['hash browns', 'cups'],
        'carrots': ['baby carrots', 'bag'],
        'wraps': ['flour tortillas', 'count'],
        'chips': ['tortilla chips', 'bag']
    }
    
    for day in plan:
        for meal in day['meals']:
            desc = meal.get('description', '').lower()
            if desc:  # Only process if description exists
                for key, item in ingredients_map.items():
                    if key in desc:
                        shopping_list[item[0]] += 1
    
    return jsonify({
        'plan': plan,
        'shopping_list': dict(shopping_list),
        'weekly_totals': {
            'avg_calories': sum(d['totals']['calories'] for d in plan) / 7,
            'avg_protein': sum(d['totals']['protein'] for d in plan) / 7,
            'total_deficit': sum(d['totals']['deficit'] for d in plan)
        }
    })

@app.route('/api/progress_photos')
def get_progress_photos():
    """Get all progress photos"""
    data = load_data()
    photos = data.get('progress_photos', [])
    
    # Sort by date
    photos = sorted(photos, key=lambda x: x['date'])
    
    return jsonify(photos)

@app.route('/api/upload_progress_photo', methods=['POST'])
def upload_progress_photo():
    """Upload a progress photo"""
    photo_data = request.json
    data = load_data()
    
    if 'progress_photos' not in data:
        data['progress_photos'] = []
    
    # Add photo entry
    photo_entry = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'weight': photo_data.get('weight'),
        'waist': photo_data.get('waist'),
        'photo_url': photo_data.get('photo_url'),  # Base64 or file path
        'notes': photo_data.get('notes', '')
    }
    
    data['progress_photos'].append(photo_entry)
    save_data(data)
    
    return jsonify({'status': 'success', 'photo': photo_entry})

@app.route('/api/generate_future_body', methods=['POST'])
def generate_future_body():
    """Generate AI prediction of future body based on trajectory"""
    request_data = request.json
    current_photo = request_data.get('current_photo')
    weeks_ahead = request_data.get('weeks_ahead', 12)
    
    # In production, this would call an image generation API
    # For now, return projection data
    
    data = load_data()
    
    # Calculate projected weight loss
    try:
        with open('user_goals.json') as f:
            goals = json.load(f)
    except:
        return jsonify({'error': 'Goals not set'})
    
    # Get current stats
    projection = get_goal_projection().json
    weekly_loss = projection['actual_weekly_loss']
    projected_weight_loss = weekly_loss * weeks_ahead
    projected_weight = projection['current_weight'] - projected_weight_loss
    
    return jsonify({
        'weeks_ahead': weeks_ahead,
        'projected_weight_loss': round(projected_weight_loss, 1),
        'projected_weight': round(projected_weight, 1),
        'current_weight': projection['current_weight'],
        'note': 'AI body generation would happen here in production',
        'confidence': 'High' if projection['status'] == 'on_pace' else 'Medium'
    })

@app.route('/api/gamification')
def get_gamification():
    """Get gamification dashboard data"""
    return jsonify(gamification.get_dashboard_data())

@app.route('/api/log_meal_with_gamification', methods=['POST'])
def log_meal_with_gamification():
    """Log meal and award XP"""
    meal_data = request.json
    data = load_data()
    
    # Add timestamp
    meal_data['date'] = datetime.now().strftime('%Y-%m-%d')
    meal_data['time'] = datetime.now().strftime('%H:%M')
    
    data['meals'].append(meal_data)
    data['meals'] = sorted(data['meals'], key=lambda x: (x['date'], x['time']))
    
    # Calculate day totals
    today = meal_data['date']
    today_meals = [m for m in data['meals'] if m['date'] == today]
    total_cal = sum(m['calories'] for m in today_meals)
    total_protein = sum(m['protein'] for m in today_meals)
    
    settings = data.get('settings', {})
    cal_goal = settings.get('daily_calorie_goal', 2200)
    protein_goal = settings.get('daily_protein_goal', 200)
    
    under_target = total_cal <= cal_goal
    protein_hit = total_protein >= protein_goal
    
    # Award XP
    xp_result = gamification.log_meal_xp(under_target=under_target, protein_hit=protein_hit)
    
    save_data(data)
    
    return jsonify({
        'status': 'success',
        'meal': meal_data,
        'gamification': xp_result
    })

@app.route('/api/add_meal', methods=['POST'])
def add_meal():
    """Quick add a meal"""
    meal_data = request.json
    data = load_data()
    
    # Add timestamp
    meal_data['date'] = datetime.now().strftime('%Y-%m-%d')
    meal_data['time'] = datetime.now().strftime('%H:%M')
    
    data['meals'].append(meal_data)
    data['meals'] = sorted(data['meals'], key=lambda x: (x['date'], x['time']))
    
    save_data(data)
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

@app.route('/api/voice_log', methods=['POST'])
def voice_log():
    """Process voice recording and log meal"""
    try:
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save temporarily
        temp_path = f'/tmp/voice_{datetime.now().timestamp()}.webm'
        audio_file.save(temp_path)
        
        # Transcribe with Whisper
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        with open(temp_path, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        
        text = transcript.text
        
        # Parse food from text using GPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Parse this meal description and provide macro estimates.

User said: "{text}"

Return ONLY valid JSON (no markdown, no explanation):
{{
  "food": "parsed food name",
  "portion_size": "estimated portion",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fat": number,
  "confidence": "high/medium/low"
}}"""
            }]
        )
        
        # Parse response
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            result_text = '\n'.join([l for l in lines if not l.startswith('```')])
            result_text = result_text.strip()
            if result_text.startswith('json'):
                result_text = result_text[4:].strip()
        
        meal_data = json.loads(result_text)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'transcript': text,
            'meal': meal_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calculate_goals', methods=['POST'])
def calculate_goals():
    """
    Calculate recommended calories based on goals
    Uses Mifflin-St Jeor equation for BMR + activity multiplier
    """
    try:
        params = request.json
        
        # Extract parameters
        age = params.get('age', 30)
        gender = params.get('gender', 'male')  # male/female
        height_inches = params.get('height_inches', 73)  # 6'1" = 73"
        current_weight = params['current_weight']
        goal_weight = params['goal_weight']
        timeline_weeks = params['timeline_weeks']
        activity_level = params.get('activity_level', 'moderate')  # sedentary/light/moderate/active/very_active
        
        # Calculate BMR (Mifflin-St Jeor)
        height_cm = height_inches * 2.54
        weight_kg = current_weight * 0.453592
        
        if gender == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,      # Little/no exercise
            'light': 1.375,        # 1-3 days/week
            'moderate': 1.55,      # 3-5 days/week
            'active': 1.725,       # 6-7 days/week
            'very_active': 1.9     # Athlete/physical job
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        tdee = bmr * multiplier  # Total Daily Energy Expenditure
        
        # Calculate required deficit/surplus
        weight_change = goal_weight - current_weight
        total_deficit_needed = weight_change * 3500  # 3500 cal/lb
        daily_deficit = total_deficit_needed / (timeline_weeks * 7)
        
        # Recommended daily calories
        recommended_calories = round(tdee + daily_deficit)
        
        # Weekly weight change rate
        weekly_rate = weight_change / timeline_weeks
        
        # Safety checks
        warnings = []
        if abs(weekly_rate) > 2:
            warnings.append("⚠️ Rate >2 lbs/week - may be aggressive")
        if recommended_calories < 1500:
            warnings.append("⚠️ Calories below 1500 - not recommended")
            recommended_calories = 1500
        
        # Protein recommendation (1g per lb bodyweight for cutting, 0.8g for maintenance)
        if weight_change < 0:
            recommended_protein = round(current_weight * 1.0)
        else:
            recommended_protein = round(current_weight * 0.8)
        
        return jsonify({
            'success': True,
            'bmr': round(bmr),
            'tdee': round(tdee),
            'recommended_calories': recommended_calories,
            'recommended_protein': recommended_protein,
            'daily_deficit': round(daily_deficit),
            'weekly_rate': round(weekly_rate, 2),
            'timeline_days': timeline_weeks * 7,
            'total_weight_change': round(weight_change, 1),
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/save_goals', methods=['POST'])
def save_goals():
    """Save user goals and apply recommended calories"""
    try:
        goals = request.json
        
        # Save to user_goals.json
        with open('user_goals.json', 'w') as f:
            json.dump(goals, f, indent=2)
        
        # Update settings in fitness_data.json
        data = load_data()
        if 'settings' not in data:
            data['settings'] = {}
        
        data['settings']['daily_calorie_goal'] = goals.get('daily_calorie_goal', 2200)
        data['settings']['daily_protein_goal'] = goals.get('daily_protein_goal', 200)
        
        save_data(data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
