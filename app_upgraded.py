from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import math
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# File upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

DATA_FILE = 'fitness_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'workouts': [],
        'food_logs': [],
        'weight_logs': [],
        'meal_templates': [],  # NEW: Saved meal templates
        'settings': {
            'target_weight': 210,
            'current_weight': 225,
            'daily_calories': 2150,
            'daily_protein': 225,
            'daily_carbs': 200,
            'daily_fat': 75,
            'birthday': '2026-05-24'
        }
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_1rm(weight, reps):
    """Epley formula for 1RM estimation"""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)

@app.route('/')
def index():
    # Provide dummy user for template (standalone mode)
    user = {'email': 'ross@local', 'name': 'Ross'}
    return render_template('dashboard_upgraded.html', user=user)

@app.route('/simple')
def simple():
    return render_template('index.html')

# NEW: Daily summary endpoint
@app.route('/api/daily-summary')
def daily_summary():
    """Get today's complete summary"""
    data = load_data()
    settings = data['settings']
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_logs = [f for f in data['food_logs'] if f['date'] == today]
    
    total_calories = sum(f.get('calories', 0) for f in today_logs)
    total_protein = sum(f.get('protein', 0) for f in today_logs)
    total_carbs = sum(f.get('carbs', 0) for f in today_logs)
    total_fat = sum(f.get('fat', 0) for f in today_logs)
    
    return jsonify({
        'date': today,
        'totals': {
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        },
        'goals': {
            'calories': settings['daily_calories'],
            'protein': settings['daily_protein'],
            'carbs': settings['daily_carbs'],
            'fat': settings['daily_fat']
        },
        'progress': {
            'calories': min(100, round((total_calories / settings['daily_calories']) * 100)),
            'protein': min(100, round((total_protein / settings['daily_protein']) * 100)),
            'carbs': min(100, round((total_carbs / settings['daily_carbs']) * 100)),
            'fat': min(100, round((total_fat / settings['daily_fat']) * 100))
        },
        'recent_meals': sorted(today_logs, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
    })

# NEW: Meal templates endpoints
@app.route('/api/meal-templates', methods=['GET'])
def get_meal_templates():
    """Get all saved meal templates"""
    data = load_data()
    return jsonify({'templates': data.get('meal_templates', [])})

@app.route('/api/meal-templates', methods=['POST'])
def save_meal_template():
    """Save a new meal template"""
    data = load_data()
    payload = request.json
    
    template = {
        'id': len(data.get('meal_templates', [])) + 1,
        'name': payload.get('name'),
        'description': payload.get('description'),
        'calories': payload.get('calories', 0),
        'protein': payload.get('protein', 0),
        'carbs': payload.get('carbs', 0),
        'fat': payload.get('fat', 0),
        'created_at': datetime.now().timestamp()
    }
    
    if 'meal_templates' not in data:
        data['meal_templates'] = []
    
    data['meal_templates'].append(template)
    save_data(data)
    
    return jsonify({'status': 'saved', 'template': template})

@app.route('/api/meal-templates/<int:template_id>', methods=['DELETE'])
def delete_meal_template(template_id):
    """Delete a meal template"""
    data = load_data()
    templates = data.get('meal_templates', [])
    data['meal_templates'] = [t for t in templates if t['id'] != template_id]
    save_data(data)
    return jsonify({'status': 'deleted'})

@app.route('/api/log-from-template/<int:template_id>', methods=['POST'])
def log_from_template(template_id):
    """Log a meal from a saved template"""
    data = load_data()
    template = next((t for t in data.get('meal_templates', []) if t['id'] == template_id), None)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    food = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'description': template['description'],
        'calories': template['calories'],
        'protein': template['protein'],
        'carbs': template['carbs'],
        'fat': template['fat'],
        'from_template': True,
        'template_name': template['name']
    }
    
    data['food_logs'].append(food)
    save_data(data)
    
    return jsonify({'status': 'logged', 'food': food})

# NEW: Weekly trends endpoint
@app.route('/api/weekly-trends')
def weekly_trends():
    """Get trend data for specified period"""
    data = load_data()
    settings = data['settings']
    days = int(request.args.get('days', 7))  # Default 7 days, support 7/14/30
    
    trends = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
        day_logs = [f for f in data['food_logs'] if f['date'] == date]
        
        trends.append({
            'date': date,
            'date_label': datetime.strptime(date, '%Y-%m-%d').strftime('%a %m/%d'),
            'calories': sum(f.get('calories', 0) for f in day_logs),
            'protein': sum(f.get('protein', 0) for f in day_logs),
            'carbs': sum(f.get('carbs', 0) for f in day_logs),
            'fat': sum(f.get('fat', 0) for f in day_logs),
            'meal_count': len(day_logs)
        })
    
    # Calculate averages
    avg_calories = sum(t['calories'] for t in trends) / len(trends) if trends else 0
    avg_protein = sum(t['protein'] for t in trends) / len(trends) if trends else 0
    
    # Calculate consistency (days hitting protein goal)
    days_hit_protein = sum(1 for t in trends if t['protein'] >= settings['daily_protein'])
    consistency = round((days_hit_protein / len(trends)) * 100) if trends else 0
    
    return jsonify({
        'period': f'{days} days',
        'trends': trends,
        'averages': {
            'calories': round(avg_calories),
            'protein': round(avg_protein)
        },
        'goals': {
            'calories': settings['daily_calories'],
            'protein': settings['daily_protein']
        },
        'consistency': consistency,
        'days_hit_goal': days_hit_protein,
        'total_days': len(trends)
    })

@app.route('/api/dashboard')
@app.route('/api/stats')
def dashboard():
    data = load_data()
    settings = data['settings']
    
    # Calculate stats
    workouts = data['workouts']
    food_logs = data['food_logs']
    weight_logs = data['weight_logs']
    
    # Current weight (latest)
    current_weight = weight_logs[-1]['weight'] if weight_logs else settings['current_weight']
    
    # Weekly weight change
    one_week_ago = (datetime.now() - timedelta(days=7)).timestamp()
    week_logs = [w for w in weight_logs if w['timestamp'] > one_week_ago]
    weekly_change = 0
    if len(week_logs) > 1:
        weekly_change = week_logs[-1]['weight'] - week_logs[0]['weight']
    
    # Today's macros
    today = datetime.now().strftime('%Y-%m-%d')
    today_logs = [f for f in food_logs if f['date'] == today]
    today_calories = sum(f.get('calories', 0) for f in today_logs)
    today_protein = sum(f.get('protein', 0) for f in today_logs)
    today_carbs = sum(f.get('carbs', 0) for f in today_logs)
    today_fat = sum(f.get('fat', 0) for f in today_logs)
    
    # Latest lifts
    latest_lifts = {}
    for workout in reversed(workouts):
        for lift in workout.get('lifts', []):
            lift_name = lift['name']
            if lift_name not in latest_lifts:
                one_rm = calculate_1rm(lift['weight'], lift['reps'])
                latest_lifts[lift_name] = {
                    'weight': lift['weight'],
                    'reps': lift['reps'],
                    'estimated_1rm': round(one_rm, 1),
                    'date': workout['date']
                }
    
    # Days until goal
    goal_date = datetime.strptime(settings['birthday'], '%Y-%m-%d')
    days_left = (goal_date - datetime.now()).days
    
    # Prepare history for charts (last 30 days)
    history = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
        day_logs = [f for f in food_logs if f['date'] == date]
        day_weight = next((w['weight'] for w in weight_logs if w['date'] == date), None)
        
        history.append({
            'date': date,
            'calories': sum(f.get('calories', 0) for f in day_logs),
            'protein': sum(f.get('protein', 0) for f in day_logs),
            'carbs': sum(f.get('carbs', 0) for f in day_logs),
            'fat': sum(f.get('fat', 0) for f in day_logs),
            'weight': day_weight
        })
    
    return jsonify({
        'current_weight': current_weight,
        'target_weight': settings['target_weight'],
        'weekly_change': round(weekly_change, 1),
        'days_until_goal': days_left,
        'today': {
            'calories': today_calories,
            'protein': today_protein,
            'carbs': today_carbs,
            'fat': today_fat
        },
        'goals': {
            'calories': settings['daily_calories'],
            'protein': settings['daily_protein'],
            'carbs': settings['daily_carbs'],
            'fat': settings['daily_fat']
        },
        'history': history,
        'latest_lifts': latest_lifts,
        'workouts_this_week': len([w for w in workouts if (datetime.now() - datetime.strptime(w['date'], '%Y-%m-%d')).days < 7])
    })

@app.route('/api/log-workout', methods=['POST'])
def log_workout():
    data = load_data()
    payload = request.json
    
    workout = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'lifts': payload.get('lifts', [])
    }
    
    data['workouts'].append(workout)
    save_data(data)
    
    return jsonify({'status': 'logged', 'workout': workout})

@app.route('/api/log-food', methods=['POST'])
def log_food():
    data = load_data()
    payload = request.json
    
    food = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'description': payload.get('description'),
        'calories': payload.get('calories', 0),
        'protein': payload.get('protein', 0),
        'carbs': payload.get('carbs', 0),
        'fat': payload.get('fat', 0)
    }
    
    data['food_logs'].append(food)
    save_data(data)
    
    return jsonify({'status': 'logged', 'food': food})

@app.route('/api/log-weight', methods=['POST'])
def log_weight():
    data = load_data()
    payload = request.json
    
    weight_log = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'weight': payload.get('weight')
    }
    
    data['weight_logs'].append(weight_log)
    save_data(data)
    
    return jsonify({'status': 'logged', 'weight': weight_log})

@app.route('/api/analyze-food-photo', methods=['POST'])
def analyze_food_photo():
    """Analyze uploaded food photo using local vision model"""
    
    # Check if file was uploaded
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No photo uploaded'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Use PNG, JPG, or GIF'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'food_{datetime.now().timestamp()}_{filename}')
        file.save(filepath)
        
        # Run local vision analyzer (use venv python if available)
        script_path = os.path.join(os.path.dirname(__file__), 'local_vision_analyzer.py')
        venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python3')
        python_cmd = venv_python if os.path.exists(venv_python) else 'python3'
        
        result = subprocess.run(
            [python_cmd, script_path, filepath],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        # Clean up temp file
        try:
            os.remove(filepath)
        except:
            pass
        
        # Parse result
        if result.returncode == 0:
            analysis = json.loads(result.stdout)
            return jsonify(analysis)
        else:
            return jsonify({
                'success': False,
                'error': 'Vision model analysis failed',
                'details': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Analysis timed out. The model may still be loading.'
        }), 504
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'Could not parse analysis result',
            'raw': result.stdout if 'result' in locals() else None
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/progress')
def get_progress():
    """Get weekly progress report with meal logs"""
    data = load_data()
    
    # Get settings
    settings = data.get('settings', {})
    meals = data.get('meals', [])
    food_logs = data.get('food_logs', [])
    
    # Combine food_logs and meals into unified structure
    all_foods = []
    for log in food_logs:
        all_foods.append({
            'date': log.get('date'),
            'time': datetime.fromtimestamp(log.get('timestamp', 0)).strftime('%H:%M') if log.get('timestamp') else '?:??',
            'food': log.get('description'),
            'calories': log.get('calories', 0),
            'protein': log.get('protein', 0),
            'carbs': log.get('carbs', 0),
            'fat': log.get('fat', 0)
        })
    
    for meal in meals:
        all_foods.append({
            'date': meal.get('date'),
            'time': meal.get('time', '?:??'),
            'food': meal.get('food'),
            'calories': meal.get('calories', 0),
            'protein': meal.get('protein', 0),
            'carbs': meal.get('carbs', 0),
            'fat': meal.get('fat', 0)
        })
    
    # Sort by date and time
    all_foods.sort(key=lambda x: (x['date'], x['time']))
    
    # Calculate week totals (last 7 days)
    today = datetime.now()
    week_start = today - timedelta(days=6)
    
    week_totals = {
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fat': 0,
        'daily_calories': settings.get('daily_calories', 2200),
        'daily_protein': settings.get('daily_protein', 200),
        'daily_carbs': settings.get('daily_carbs', 250),
        'daily_fat': settings.get('daily_fat', 70)
    }
    
    # Group meals by date
    meal_log = {}
    daily_breakdown = []
    
    for i in range(7):
        date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
        date_meals = [f for f in all_foods if f['date'] == date]
        
        if date_meals:
            meal_log[date] = date_meals
            
            day_total = {
                'day': (datetime.strptime(date, '%Y-%m-%d')).strftime('%a'),
                'date': date,
                'calories': sum(f['calories'] for f in date_meals),
                'protein': sum(f['protein'] for f in date_meals),
                'carbs': sum(f['carbs'] for f in date_meals),
                'fat': sum(f['fat'] for f in date_meals)
            }
            
            daily_breakdown.append(day_total)
            
            week_totals['total_calories'] += day_total['calories']
            week_totals['total_protein'] += day_total['protein']
            week_totals['total_carbs'] += day_total['carbs']
            week_totals['total_fat'] += day_total['fat']
    
    # Macro totals for pie chart
    macro_totals = {
        'protein': week_totals['total_protein'],
        'carbs': week_totals['total_carbs'],
        'fat': week_totals['total_fat']
    }
    
    return jsonify({
        'success': True,
        'stats': week_totals,
        'daily_breakdown': daily_breakdown,
        'macro_totals': macro_totals,
        'meal_log': meal_log
    })

@app.route('/api/meal-history')
def meal_history():
    """Get all logged meals and food logs"""
    data = load_data()
    
    # Combine food_logs and meals
    all_entries = []
    
    for log in data.get('food_logs', []):
        all_entries.append({
            'date': log.get('date'),
            'time': datetime.fromtimestamp(log.get('timestamp', 0)).strftime('%I:%M %p'),
            'timestamp': log.get('timestamp', 0),
            'description': log.get('description', 'Unknown food'),
            'calories': log.get('calories', 0),
            'protein': log.get('protein', 0),
            'carbs': log.get('carbs', 0),
            'fat': log.get('fat', 0),
            'notes': log.get('notes', ''),
            'from_template': log.get('from_template', False),
            'template_name': log.get('template_name', '')
        })
    
    for meal in data.get('meals', []):
        # Parse time string to timestamp for sorting
        try:
            date_time = datetime.strptime(f"{meal.get('date')} {meal.get('time')}", '%Y-%m-%d %H:%M')
            timestamp = date_time.timestamp()
        except:
            timestamp = 0
            
        all_entries.append({
            'date': meal.get('date'),
            'time': meal.get('time', '?:??'),
            'timestamp': timestamp,
            'description': meal.get('food', 'Unknown food'),
            'calories': meal.get('calories', 0),
            'protein': meal.get('protein', 0),
            'carbs': meal.get('carbs', 0),
            'fat': meal.get('fat', 0),
            'notes': meal.get('notes', ''),
            'from_template': False,
            'template_name': ''
        })
    
    # Sort by date and timestamp (most recent first)
    all_entries.sort(key=lambda x: (x['date'], x['timestamp']), reverse=True)
    
    # Group by date
    grouped = {}
    for entry in all_entries:
        date = entry['date']
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(entry)
    
    return jsonify({
        'entries': all_entries,
        'grouped': grouped,
        'total_entries': len(all_entries)
    })

@app.route('/progress')
def progress_page():
    """Render weekly progress page"""
    return render_template('weekly_progress.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
