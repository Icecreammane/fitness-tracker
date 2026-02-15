from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', 'price_1234')  # Set this after creating product in Stripe

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data directory
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# User Model
class User(UserMixin):
    def __init__(self, id, email, password_hash, created_at, subscription_status='trial', subscription_id=None, trial_end=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.subscription_status = subscription_status  # trial, active, canceled, expired
        self.subscription_id = subscription_id
        self.trial_end = trial_end or (datetime.now() + timedelta(days=7)).isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'subscription_status': self.subscription_status,
            'subscription_id': self.subscription_id,
            'trial_end': self.trial_end
        }
    
    def is_subscription_active(self):
        if self.subscription_status == 'active':
            return True
        if self.subscription_status == 'trial':
            trial_end = datetime.fromisoformat(self.trial_end)
            return datetime.now() < trial_end
        return False

# Database functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user_by_email(email):
    users = load_users()
    for user_id, user_data in users.items():
        if user_data['email'] == email:
            return User(**user_data)
    return None

def get_user_by_id(user_id):
    users = load_users()
    if user_id in users:
        return User(**users[user_id])
    return None

def create_user(email, password):
    users = load_users()
    user_id = secrets.token_hex(16)
    
    user = User(
        id=user_id,
        email=email,
        password_hash=generate_password_hash(password),
        created_at=datetime.now().isoformat()
    )
    
    users[user_id] = user.to_dict()
    save_users(users)
    
    # Create user's fitness data file
    user_data_file = os.path.join(DATA_DIR, f'{user_id}_fitness.json')
    initial_data = {
        'workouts': [],
        'food_logs': [],
        'weight_logs': [],
        'settings': {
            'target_weight': 180,
            'current_weight': 200,
            'daily_calories': 2000,
            'daily_protein': 150,
            'daily_carbs': 200,
            'daily_fat': 70
        }
    }
    with open(user_data_file, 'w') as f:
        json.dump(initial_data, f, indent=2)
    
    return user

def update_user_subscription(user_id, subscription_status, subscription_id=None):
    users = load_users()
    if user_id in users:
        users[user_id]['subscription_status'] = subscription_status
        if subscription_id:
            users[user_id]['subscription_id'] = subscription_id
        save_users(users)

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# User data functions
def get_user_data_file(user_id):
    return os.path.join(DATA_DIR, f'{user_id}_fitness.json')

def load_user_data(user_id):
    data_file = get_user_data_file(user_id)
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return {
        'workouts': [],
        'food_logs': [],
        'weight_logs': [],
        'settings': {
            'target_weight': 180,
            'current_weight': 200,
            'daily_calories': 2000,
            'daily_protein': 150,
            'daily_carbs': 200,
            'daily_fat': 70
        }
    }

def save_user_data(user_id, data):
    data_file = get_user_data_file(user_id)
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_1rm(weight, reps):
    """Epley formula for 1RM estimation"""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)

# Routes - Public
@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

# Routes - Auth
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            if request.is_json:
                return jsonify({'error': 'Email and password required'}), 400
            flash('Email and password required', 'error')
            return redirect(url_for('signup'))
        
        if get_user_by_email(email):
            if request.is_json:
                return jsonify({'error': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        user = create_user(email, password)
        login_user(user)
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        user = get_user_by_email(email)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid email or password'}), 401
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

# Routes - Protected
@app.route('/dashboard')
@login_required
def dashboard():
    # Check subscription status
    if not current_user.is_subscription_active():
        return redirect(url_for('subscription_expired'))
    
    return render_template('dashboard_saas.html', user=current_user)

@app.route('/subscription-expired')
@login_required
def subscription_expired():
    return render_template('subscription_expired.html', user=current_user)

@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

# Routes - API
@app.route('/api/stats')
@login_required
def api_stats():
    if not current_user.is_subscription_active():
        return jsonify({'error': 'Subscription required'}), 403
    
    data = load_user_data(current_user.id)
    settings = data['settings']
    workouts = data['workouts']
    food_logs = data['food_logs']
    weight_logs = data['weight_logs']
    
    # Current weight
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
    
    # Prepare history
    history = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
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
@login_required
def log_workout():
    if not current_user.is_subscription_active():
        return jsonify({'error': 'Subscription required'}), 403
    
    data = load_user_data(current_user.id)
    payload = request.json
    
    workout = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'lifts': payload.get('lifts', [])
    }
    
    data['workouts'].append(workout)
    save_user_data(current_user.id, data)
    
    return jsonify({'status': 'logged', 'workout': workout})

@app.route('/api/log-food', methods=['POST'])
@login_required
def log_food():
    if not current_user.is_subscription_active():
        return jsonify({'error': 'Subscription required'}), 403
    
    data = load_user_data(current_user.id)
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
    save_user_data(current_user.id, data)
    
    return jsonify({'status': 'logged', 'food': food})

@app.route('/api/log-weight', methods=['POST'])
@login_required
def log_weight():
    if not current_user.is_subscription_active():
        return jsonify({'error': 'Subscription required'}), 403
    
    data = load_user_data(current_user.id)
    payload = request.json
    
    weight_log = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().timestamp(),
        'weight': payload.get('weight')
    }
    
    data['weight_logs'].append(weight_log)
    save_user_data(current_user.id, data)
    
    return jsonify({'status': 'logged', 'weight': weight_log})

# Stripe Routes
@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'FitTrack Pro - Monthly Subscription',
                        'description': 'Track macros, workouts, and weight with AI-powered insights',
                    },
                    'unit_amount': 1000,  # $10.00
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'pricing',
            metadata={
                'user_id': current_user.id
            }
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/payment-success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    return render_template('payment_success.html', session_id=session_id)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Handle subscription events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        subscription_id = session['subscription']
        update_user_subscription(user_id, 'active', subscription_id)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Find user by subscription ID
        users = load_users()
        for user_id, user_data in users.items():
            if user_data.get('subscription_id') == subscription['id']:
                update_user_subscription(user_id, 'canceled')
                break
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
