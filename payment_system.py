#!/usr/bin/env python3
"""
Stripe Payment Integration for Lean
Test mode integration for Pro subscriptions
"""

import os
import json
from datetime import datetime, timedelta

# Stripe client - lazy load
_stripe = None

def get_stripe_client():
    """Get or initialize Stripe client"""
    global _stripe
    
    if _stripe is None:
        try:
            import stripe as stripe_module
            api_key = os.getenv('STRIPE_SECRET_KEY')
            
            if api_key:
                stripe_module.api_key = api_key
                _stripe = stripe_module
            else:
                print("Warning: STRIPE_SECRET_KEY not set")
                _stripe = None
        except ImportError:
            print("Warning: stripe not installed")
            _stripe = None
    
    return _stripe

SUBSCRIPTION_FILE = 'subscriptions.json'

def load_subscriptions():
    """Load subscription data"""
    if not os.path.exists(SUBSCRIPTION_FILE):
        return {'users': {}}
    with open(SUBSCRIPTION_FILE) as f:
        return json.load(f)

def save_subscriptions(data):
    """Save subscription data"""
    with open(SUBSCRIPTION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_tier(user_id):
    """
    Get user's subscription tier
    Returns: 'free', 'pro', 'lifetime'
    """
    data = load_subscriptions()
    
    if user_id not in data['users']:
        return 'free'
    
    user = data['users'][user_id]
    tier = user.get('tier', 'free')
    
    # Check if subscription expired
    if tier == 'pro' and 'expires_at' in user:
        expires_at = datetime.fromisoformat(user['expires_at'])
        if datetime.now() > expires_at:
            # Expired
            user['tier'] = 'free'
            save_subscriptions(data)
            return 'free'
    
    return tier

def check_usage_limit(user_id):
    """
    Check if user can log meals based on their tier
    Free: 50 meals/month
    Pro/Lifetime: unlimited
    Returns: (can_log: bool, meals_remaining: int)
    """
    tier = get_user_tier(user_id)
    
    if tier in ['pro', 'lifetime']:
        return True, -1  # Unlimited
    
    # Count this month's meals
    from datetime import datetime
    import json
    
    with open('fitness_data.json') as f:
        data = json.load(f)
    
    current_month = datetime.now().strftime('%Y-%m')
    user_meals = [
        m for m in data['meals']
        if m.get('user_id') == user_id and m['date'].startswith(current_month)
    ]
    
    meals_logged = len(user_meals)
    meals_remaining = 50 - meals_logged
    
    return meals_remaining > 0, meals_remaining

def create_checkout_session(user_id, plan, success_url, cancel_url):
    """
    Create Stripe Checkout session
    plan: 'pro_monthly', 'lifetime'
    """
    stripe = get_stripe_client()
    
    if not stripe:
        return {'error': 'Stripe not configured'}
    
    # Pricing
    prices = {
        'pro_monthly': {
            'amount': 499,  # $4.99
            'currency': 'usd',
            'interval': 'month',
            'name': 'Lean Pro - Monthly'
        },
        'lifetime': {
            'amount': 4900,  # $49
            'currency': 'usd',
            'interval': 'one_time',
            'name': 'Lean Pro - Lifetime'
        }
    }
    
    if plan not in prices:
        return {'error': 'Invalid plan'}
    
    price_info = prices[plan]
    
    try:
        # Create Checkout Session
        if price_info['interval'] == 'one_time':
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'product_data': {
                            'name': price_info['name'],
                        },
                        'unit_amount': price_info['amount'],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={
                    'user_id': user_id,
                    'plan': plan
                }
            )
        else:
            # Recurring subscription
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'product_data': {
                            'name': price_info['name'],
                        },
                        'unit_amount': price_info['amount'],
                        'recurring': {
                            'interval': price_info['interval']
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={
                    'user_id': user_id,
                    'plan': plan
                }
            )
        
        return {
            'success': True,
            'session_id': session.id,
            'checkout_url': session.url
        }
    
    except Exception as e:
        return {'error': str(e)}

def handle_successful_payment(session_id):
    """Handle successful Stripe payment"""
    stripe = get_stripe_client()
    
    if not stripe:
        return {'error': 'Stripe not configured'}
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        user_id = session.metadata.get('user_id') or session.client_reference_id
        plan = session.metadata.get('plan')
        
        data = load_subscriptions()
        
        if user_id not in data['users']:
            data['users'][user_id] = {}
        
        # Update user's subscription
        if plan == 'lifetime':
            data['users'][user_id] = {
                'tier': 'lifetime',
                'purchased_at': datetime.now().isoformat(),
                'stripe_session_id': session_id
            }
        elif plan == 'pro_monthly':
            # Set expiration to 30 days from now
            expires_at = datetime.now() + timedelta(days=30)
            data['users'][user_id] = {
                'tier': 'pro',
                'purchased_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'stripe_session_id': session_id,
                'stripe_subscription_id': session.subscription if hasattr(session, 'subscription') else None
            }
        
        save_subscriptions(data)
        
        # Track in analytics
        from analytics import Analytics
        Analytics.track_subscription_started(
            user_id,
            plan,
            session.amount_total / 100 if hasattr(session, 'amount_total') else 0
        )
        
        return {
            'success': True,
            'user_id': user_id,
            'plan': plan
        }
    
    except Exception as e:
        return {'error': str(e)}

def grant_pro_time(user_id, days):
    """Grant Pro time to user (for referrals)"""
    data = load_subscriptions()
    
    if user_id not in data['users']:
        data['users'][user_id] = {}
    
    user = data['users'][user_id]
    
    # If already has Pro, extend it
    if user.get('tier') == 'pro' and 'expires_at' in user:
        expires_at = datetime.fromisoformat(user['expires_at'])
        # Extend from current expiration
        new_expiration = expires_at + timedelta(days=days)
    else:
        # Grant new Pro time
        new_expiration = datetime.now() + timedelta(days=days)
        user['tier'] = 'pro'
    
    user['expires_at'] = new_expiration.isoformat()
    
    # Track how it was granted
    if 'granted_days' not in user:
        user['granted_days'] = []
    
    user['granted_days'].append({
        'days': days,
        'granted_at': datetime.now().isoformat(),
        'source': 'referral'
    })
    
    save_subscriptions(data)
    
    return {
        'success': True,
        'tier': 'pro',
        'expires_at': new_expiration.isoformat()
    }

def get_pricing():
    """Get pricing information"""
    return {
        'free': {
            'name': 'Free',
            'price': 0,
            'features': [
                '50 meals per month',
                'Voice & photo logging',
                'Basic analytics',
                'Progress tracking'
            ]
        },
        'pro_monthly': {
            'name': 'Pro',
            'price': 4.99,
            'interval': 'month',
            'features': [
                'Unlimited meals',
                'All Free features',
                'Advanced analytics',
                'Share cards',
                'Meal planning',
                'Priority support'
            ]
        },
        'lifetime': {
            'name': 'Pro Lifetime',
            'price': 49.00,
            'interval': 'one-time',
            'features': [
                'All Pro features',
                'Lifetime access',
                'One-time payment',
                'Best value'
            ]
        }
    }
