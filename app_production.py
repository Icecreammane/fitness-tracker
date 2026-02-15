"""
FitTrack Pro - Production-Ready Flask Application
Includes: Security hardening, rate limiting, error handling, analytics, and optimization
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import stripe
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import secrets
import logging
from logging.handlers import RotatingFileHandler
import traceback

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files

# Trust proxy headers (for Railway/Heroku)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Security headers with Talisman (only in production)
if os.getenv('FLASK_ENV') == 'production':
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "https://js.stripe.com", "https://www.googletagmanager.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "data:"],
        'connect-src': ["'self'", "https://api.stripe.com", "https://www.google-analytics.com"],
        'frame-src': ["https://js.stripe.com"]
    }
    Talisman(app, 
             force_https=True,
             strict_transport_security=True,
             content_security_policy=csp,
             content_security_policy_nonce_in=['script-src'])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', 'price_1234')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Google Analytics
GA_MEASUREMENT_ID = os.getenv('GA_MEASUREMENT_ID', 'G-XXXXXXXXXX')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data directory
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
FITNESS_DATA_FILE = 'fitness_data_{user_id}.json'

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Logging configuration
if not app.debug:
    file_handler = RotatingFileHandler('logs/fittrack.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('FitTrack Pro startup')

# User Model
class User(UserMixin):
    def __init__(self, id, email, password_hash, created_at, subscription_status='trial', 
                 subscription_id=None, trial_end=None, stripe_customer_id=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.subscription_status = subscription_status
        self.subscription_id = subscription_id
        self.trial_end = trial_end or (datetime.now() + timedelta(days=7)).isoformat()
        self.stripe_customer_id = stripe_customer_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'subscription_status': self.subscription_status,
            'subscription_id': self.subscription_id,
            'trial_end': self.trial_end,
            'stripe_customer_id': self.stripe_customer_id
        }
    
    def is_subscription_active(self):
        if self.subscription_status == 'active':
            return True
        if self.subscription_status == 'trial':
            trial_end = datetime.fromisoformat(self.trial_end)
            return datetime.now() < trial_end
        return False

# Database functions with error handling
def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        app.logger.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving users: {e}")
        raise

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

def get_user_by_stripe_customer(customer_id):
    users = load_users()
    for user_id, user_data in users.items():
        if user_data.get('stripe_customer_id') == customer_id:
            return User(**user_data)
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
    
    return user

def update_user(user):
    users = load_users()
    users[user.id] = user.to_dict()
    save_users(users)

# Fitness data functions
def get_user_data_file(user_id):
    return os.path.join(DATA_DIR, FITNESS_DATA_FILE.format(user_id=user_id))

def load_fitness_data(user_id):
    file_path = get_user_data_file(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading fitness data for {user_id}: {e}")
            return init_fitness_data()
    return init_fitness_data()

def init_fitness_data():
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

def save_fitness_data(user_id, data):
    file_path = get_user_data_file(user_id)
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving fitness data for {user_id}: {e}")
        raise

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}, route: {request.url}')
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error. Please try again later.'}), 500
    return render_template('500.html'), 500

@app.errorhandler(429)
def ratelimit_error(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# Landing page
@app.route('/')
def landing():
    return render_template('landing.html', 
                         ga_id=GA_MEASUREMENT_ID,
                         stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html', ga_id=GA_MEASUREMENT_ID)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', 
                         ga_id=GA_MEASUREMENT_ID,
                         stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

# Auth routes with rate limiting
@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def signup():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validation
            if not email or not password:
                flash('Email and password are required', 'error')
                return redirect(url_for('signup'))
            
            if len(password) < 8:
                flash('Password must be at least 8 characters', 'error')
                return redirect(url_for('signup'))
            
            if get_user_by_email(email):
                flash('Email already registered', 'error')
                return redirect(url_for('login'))
            
            # Create user
            user = create_user(email, password)
            login_user(user)
            
            app.logger.info(f'New user signup: {email}')
            
            # Track signup event (GA4 will pick this up)
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            app.logger.error(f'Signup error: {e}')
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html', ga_id=GA_MEASUREMENT_ID)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            user = get_user_by_email(email)
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                app.logger.info(f'User login: {email}')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            app.logger.error(f'Login error: {e}')
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html', ga_id=GA_MEASUREMENT_ID)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

# Dashboard (main app)
@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_subscription_active():
        return redirect(url_for('subscription_expired'))
    
    return render_template('dashboard_enhanced.html', 
                         user=current_user,
                         ga_id=GA_MEASUREMENT_ID)

@app.route('/subscription-expired')
@login_required
def subscription_expired():
    return render_template('subscription_expired.html',
                         user=current_user,
                         ga_id=GA_MEASUREMENT_ID,
                         stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

# API endpoints with rate limiting
@app.route('/api/stats')
@login_required
@limiter.limit("60 per minute")
def api_stats():
    try:
        data = load_fitness_data(current_user.id)
        settings = data['settings']
        workouts = data['workouts']
        food_logs = data['food_logs']
        weight_logs = data['weight_logs']
        
        # Current weight
        current_weight = weight_logs[-1]['weight'] if weight_logs else settings.get('current_weight', 0)
        
        # Weekly change
        one_week_ago = (datetime.now() - timedelta(days=7)).timestamp()
        week_logs = [w for w in weight_logs if w.get('timestamp', 0) > one_week_ago]
        weekly_change = 0
        if len(week_logs) > 1:
            weekly_change = week_logs[-1]['weight'] - week_logs[0]['weight']
        
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
        
        return jsonify({
            'current_weight': current_weight,
            'target_weight': settings.get('target_weight', 0),
            'weekly_change': round(weekly_change, 1),
            'today': {
                'calories': today_calories,
                'protein': today_protein,
                'carbs': today_carbs,
                'fat': today_fat
            },
            'goals': {
                'calories': settings.get('daily_calories', 2000),
                'protein': settings.get('daily_protein', 150),
                'carbs': settings.get('daily_carbs', 200),
                'fat': settings.get('daily_fat', 70)
            },
            'history': history,
            'workouts_this_week': len([w for w in workouts if 
                (datetime.now() - datetime.fromisoformat(w.get('date', datetime.now().isoformat()))).days < 7])
        })
        
    except Exception as e:
        app.logger.error(f'Stats API error: {e}\n{traceback.format_exc()}')
        return jsonify({'error': 'Failed to load stats'}), 500

@app.route('/api/log-food', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def log_food():
    try:
        data = load_fitness_data(current_user.id)
        payload = request.json
        
        # Sanitize input
        food = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'description': str(payload.get('description', ''))[:200],
            'calories': min(max(int(payload.get('calories', 0)), 0), 10000),
            'protein': min(max(int(payload.get('protein', 0)), 0), 1000),
            'carbs': min(max(int(payload.get('carbs', 0)), 0), 1000),
            'fat': min(max(int(payload.get('fat', 0)), 0), 1000)
        }
        
        data['food_logs'].append(food)
        save_fitness_data(current_user.id, data)
        
        return jsonify({'status': 'success', 'food': food})
        
    except Exception as e:
        app.logger.error(f'Log food error: {e}')
        return jsonify({'error': 'Failed to log food'}), 500

@app.route('/api/log-workout', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def log_workout():
    try:
        data = load_fitness_data(current_user.id)
        payload = request.json
        
        workout = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'lifts': payload.get('lifts', [])[:20]  # Max 20 lifts per workout
        }
        
        data['workouts'].append(workout)
        save_fitness_data(current_user.id, data)
        
        return jsonify({'status': 'success', 'workout': workout})
        
    except Exception as e:
        app.logger.error(f'Log workout error: {e}')
        return jsonify({'error': 'Failed to log workout'}), 500

@app.route('/api/log-weight', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def log_weight():
    try:
        data = load_fitness_data(current_user.id)
        payload = request.json
        
        weight_log = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().timestamp(),
            'weight': min(max(float(payload.get('weight', 0)), 50), 1000)
        }
        
        data['weight_logs'].append(weight_log)
        save_fitness_data(current_user.id, data)
        
        return jsonify({'status': 'success', 'weight': weight_log})
        
    except Exception as e:
        app.logger.error(f'Log weight error: {e}')
        return jsonify({'error': 'Failed to log weight'}), 500

# Stripe integration
@app.route('/create-checkout-session', methods=['POST'])
@limiter.limit("5 per hour")
def create_checkout_session():
    try:
        if current_user.is_authenticated:
            email = current_user.email
            customer_id = current_user.stripe_customer_id
        else:
            email = request.json.get('email')
            customer_id = None
        
        # Create or retrieve customer
        if not customer_id and email:
            customers = stripe.Customer.list(email=email, limit=1)
            if customers.data:
                customer_id = customers.data[0].id
            else:
                customer = stripe.Customer.create(email=email)
                customer_id = customer.id
                
                if current_user.is_authenticated:
                    current_user.stripe_customer_id = customer_id
                    update_user(current_user)
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('pricing', _external=True),
        )
        
        return jsonify({'sessionId': checkout_session.id})
        
    except Exception as e:
        app.logger.error(f'Checkout error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/payment-success')
def payment_success():
    session_id = request.args.get('session_id')
    return render_template('payment_success.html', 
                         session_id=session_id,
                         ga_id=GA_MEASUREMENT_ID)

@app.route('/stripe-webhook', methods=['POST'])
@limiter.exempt
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_update(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_canceled(subscription)
    
    return jsonify({'status': 'success'})

def handle_checkout_session(session):
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    user = get_user_by_stripe_customer(customer_id)
    if user:
        user.subscription_status = 'active'
        user.subscription_id = subscription_id
        user.stripe_customer_id = customer_id
        update_user(user)
        app.logger.info(f'Subscription activated for user: {user.email}')

def handle_subscription_update(subscription):
    customer_id = subscription.get('customer')
    status = subscription.get('status')
    
    user = get_user_by_stripe_customer(customer_id)
    if user:
        if status == 'active':
            user.subscription_status = 'active'
        elif status in ['canceled', 'incomplete_expired']:
            user.subscription_status = 'canceled'
        update_user(user)
        app.logger.info(f'Subscription updated for user: {user.email} - Status: {status}')

def handle_subscription_canceled(subscription):
    customer_id = subscription.get('customer')
    
    user = get_user_by_stripe_customer(customer_id)
    if user:
        user.subscription_status = 'canceled'
        update_user(user)
        app.logger.info(f'Subscription canceled for user: {user.email}')

# Sitemap
@app.route('/sitemap.xml')
def sitemap():
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    
    # Static pages
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            if rule.rule not in ['/health', '/stripe-webhook', '/api/stats', '/dashboard', 
                                '/logout', '/subscription-expired']:
                pages.append({
                    'loc': url_for(rule.endpoint, _external=True),
                    'lastmod': ten_days_ago,
                    'changefreq': 'weekly',
                    'priority': '0.8' if rule.rule == '/' else '0.6'
                })
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    '''
    for page in pages:
        sitemap_xml += f'''
        <url>
            <loc>{page['loc']}</loc>
            <lastmod>{page['lastmod']}</lastmod>
            <changefreq>{page['changefreq']}</changefreq>
            <priority>{page['priority']}</priority>
        </url>
        '''
    sitemap_xml += '\n    </urlset>'
    
    response = app.make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

# Robots.txt
@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /api/
Disallow: /admin/

Sitemap: {}/sitemap.xml
'''.format(request.url_root.rstrip('/'))

if __name__ == '__main__':
    # Validate required environment variables
    required_vars = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'SECRET_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing)}")
        print("App will run but some features may not work.")
    
    # Run app
    port = int(os.getenv('PORT', 3000))
    app.run(
        debug=os.getenv('FLASK_ENV') != 'production',
        host='0.0.0.0',
        port=port
    )
