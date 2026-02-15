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
    return render_template('dashboard_enhanced.html', user=user)

@app.route('/simple')
def simple():
    return render_template('index.html')

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

@app.route('/progress')
def progress_page():
    """Render weekly progress page"""
    return render_template('weekly_progress.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
