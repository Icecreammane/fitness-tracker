#!/usr/bin/env python3
"""
Referral System for Lean
"Give 1 month Pro, get 1 month Pro" mechanic
"""

import json
import os
import secrets
from datetime import datetime, timedelta

REFERRAL_FILE = 'referral_data.json'

def load_referrals():
    """Load referral data"""
    if not os.path.exists(REFERRAL_FILE):
        return {'users': {}, 'referrals': []}
    with open(REFERRAL_FILE) as f:
        return json.load(f)

def save_referrals(data):
    """Save referral data"""
    with open(REFERRAL_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_referral_code(user_id):
    """Generate unique referral code for user"""
    data = load_referrals()
    
    # Check if user already has code
    if user_id in data['users']:
        return data['users'][user_id]['code']
    
    # Generate new code
    code = secrets.token_urlsafe(8).upper().replace('_', 'X').replace('-', 'Y')[:8]
    
    # Ensure uniqueness
    while code in [u['code'] for u in data['users'].values()]:
        code = secrets.token_urlsafe(8).upper().replace('_', 'X').replace('-', 'Y')[:8]
    
    # Store
    data['users'][user_id] = {
        'code': code,
        'created_at': datetime.now().isoformat(),
        'referrals': [],
        'pro_days_earned': 0
    }
    
    save_referrals(data)
    return code

def track_referral(referrer_code, new_user_id):
    """Track when someone uses a referral code"""
    data = load_referrals()
    
    # Find referrer
    referrer_id = None
    for uid, user_data in data['users'].items():
        if user_data['code'] == referrer_code:
            referrer_id = uid
            break
    
    if not referrer_id:
        return {'success': False, 'error': 'Invalid referral code'}
    
    # Check if user already used a code
    for ref in data['referrals']:
        if ref['new_user_id'] == new_user_id:
            return {'success': False, 'error': 'User already used a referral code'}
    
    # Record referral
    referral = {
        'referrer_id': referrer_id,
        'new_user_id': new_user_id,
        'referrer_code': referrer_code,
        'created_at': datetime.now().isoformat(),
        'referrer_reward_granted': False,
        'new_user_reward_granted': False
    }
    
    data['referrals'].append(referral)
    data['users'][referrer_id]['referrals'].append({
        'user_id': new_user_id,
        'date': datetime.now().isoformat(),
        'status': 'pending'
    })
    
    save_referrals(data)
    
    return {
        'success': True,
        'referrer_id': referrer_id,
        'new_user_id': new_user_id
    }

def grant_referral_rewards(referral_id):
    """Grant Pro time to both users (called after new user logs first meal)"""
    data = load_referrals()
    
    if referral_id >= len(data['referrals']):
        return {'success': False, 'error': 'Invalid referral'}
    
    referral = data['referrals'][referral_id]
    
    # Grant 30 days Pro to both
    referrer_id = referral['referrer_id']
    new_user_id = referral['new_user_id']
    
    # Update referral status
    data['referrals'][referral_id]['referrer_reward_granted'] = True
    data['referrals'][referral_id]['new_user_reward_granted'] = True
    data['referrals'][referral_id]['reward_granted_at'] = datetime.now().isoformat()
    
    # Update referrer's earned days
    data['users'][referrer_id]['pro_days_earned'] += 30
    
    # Update referral status in referrer's list
    for ref in data['users'][referrer_id]['referrals']:
        if ref['user_id'] == new_user_id:
            ref['status'] = 'completed'
            ref['completed_at'] = datetime.now().isoformat()
    
    save_referrals(data)
    
    return {
        'success': True,
        'referrer_id': referrer_id,
        'new_user_id': new_user_id,
        'pro_days_granted': 30
    }

def get_user_referral_stats(user_id):
    """Get referral stats for a user"""
    data = load_referrals()
    
    if user_id not in data['users']:
        return None
    
    user_data = data['users'][user_id]
    
    completed = len([r for r in user_data['referrals'] if r['status'] == 'completed'])
    pending = len([r for r in user_data['referrals'] if r['status'] == 'pending'])
    
    return {
        'code': user_data['code'],
        'total_referrals': len(user_data['referrals']),
        'completed': completed,
        'pending': pending,
        'pro_days_earned': user_data['pro_days_earned'],
        'referrals': user_data['referrals']
    }

def get_referral_link(code, base_url="https://lean.app"):
    """Generate shareable referral link"""
    return f"{base_url}?ref={code}"
