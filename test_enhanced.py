#!/usr/bin/env python3
"""
Test Enhanced Dashboard
Runs on port 8080
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATA_FILE = 'fitness_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'workouts': [],
        'food_logs': [],
        'weight_logs': [],
        'settings': {
            'target_weight': 210,
            'current_weight': 225,
            'daily_calories': 2150,
            'daily_protein': 225,
            'daily_carbs': 200,
            'daily_fat': 75
        }
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    # For testing without auth
    class MockUser:
        email = "test@fittrack.com"
    return render_template('dashboard_enhanced.html', user=MockUser(), ga_id='G-TEST')

@app.route('/api/stats')
def stats():
    data = load_data()
    settings = data['settings']
    food_logs = data['food_logs']
    weight_logs = data['weight_logs']
    workouts = data['workouts']
    
    current_weight = weight_logs[-1]['weight'] if weight_logs else settings.get('current_weight', 225)
    
    # Today's macros
    today = datetime.now().strftime('%Y-%m-%d')
    today_logs = [f for f in food_logs if f.get('date') == today]
    today_calories = sum(f.get('calories', 0) for f in today_logs)
    today_protein = sum(f.get('protein', 0) for f in today_logs)
    today_carbs = sum(f.get('carbs', 0) for f in today_logs)
    today_fat = sum(f.get('fat', 0) for f in today_logs)
    
    # History (last 30 days)
    history = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
        day_logs = [f for f in food_logs if f.get('date') == date]
        day_weight = next((w['weight'] for w in weight_logs if w.get('date') == date), None)
        
        history.append({
            'date': date,
            'calories': sum(f.get('calories', 0) for f in day_logs),
            'protein': sum(f.get('protein', 0) for f in day_logs),
            'carbs': sum(f.get('carbs', 0) for f in day_logs),
            'fat': sum(f.get('fat', 0) for f in day_logs),
            'weight': day_weight
        })
    
    # Weekly change
    one_week_ago = (datetime.now() - timedelta(days=7)).timestamp()
    week_logs = [w for w in weight_logs if w.get('timestamp', 0) > one_week_ago]
    weekly_change = 0
    if len(week_logs) > 1:
        weekly_change = week_logs[-1]['weight'] - week_logs[0]['weight']
    
    return jsonify({
        'current_weight': current_weight,
        'target_weight': settings.get('target_weight', 210),
        'weekly_change': round(weekly_change, 1),
        'today': {
            'calories': today_calories,
            'protein': today_protein,
            'carbs': today_carbs,
            'fat': today_fat
        },
        'goals': {
            'calories': settings.get('daily_calories', 2150),
            'protein': settings.get('daily_protein', 225),
            'carbs': settings.get('daily_carbs', 200),
            'fat': settings.get('daily_fat', 75)
        },
        'history': history,
        'workouts_this_week': len([w for w in workouts if 
            (datetime.now() - datetime.fromisoformat(w.get('date', datetime.now().isoformat()))).days < 7])
    })

@app.route('/api/log-food', methods=['POST'])
def log_food():
    try:
        data = load_data()
        payload = request.json
        
        food = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'description': payload.get('description', ''),
            'calories': int(payload.get('calories', 0)),
            'protein': int(payload.get('protein', 0)),
            'carbs': int(payload.get('carbs', 0)),
            'fat': int(payload.get('fat', 0))
        }
        
        data['food_logs'].append(food)
        save_data(data)
        
        return jsonify({'status': 'success', 'food': food})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-weight', methods=['POST'])
def log_weight():
    try:
        data = load_data()
        payload = request.json
        
        weight_log = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'weight': float(payload.get('weight', 0))
        }
        
        data['weight_logs'].append(weight_log)
        save_data(data)
        
        return jsonify({'status': 'success', 'weight': weight_log})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-workout', methods=['POST'])
def log_workout():
    try:
        data = load_data()
        payload = request.json
        
        workout = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'lifts': payload.get('lifts', [])
        }
        
        data['workouts'].append(workout)
        save_data(data)
        
        return jsonify({'status': 'success', 'workout': workout})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 FitTrack Enhanced Dashboard')
    print('='*60)
    print('✨ Features:')
    print('  • Quick-log widget (< 5 taps)')
    print('  • Weekly progress cards with comparisons')
    print('  • 30-day trend charts for calories & protein')
    print('\n📍 Dashboard: http://localhost:8080')
    print('='*60 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=8080)
