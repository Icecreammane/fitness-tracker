#!/usr/bin/env python3
"""
Email Capture & Automation for Lean
Integrates with Airtable/Google Sheets for capture
Email drip sequences via Loops.so or manual
"""

import os
import json
from datetime import datetime

EMAIL_FILE = 'email_subscribers.json'

def load_subscribers():
    """Load subscriber data"""
    if not os.path.exists(EMAIL_FILE):
        return {'subscribers': []}
    with open(EMAIL_FILE) as f:
        return json.load(f)

def save_subscribers(data):
    """Save subscriber data"""
    with open(EMAIL_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def capture_email(email, source='landing', name=None, metadata=None):
    """
    Capture email signup
    source: 'landing', 'app', 'referral'
    """
    data = load_subscribers()
    
    # Check if already subscribed
    existing = [s for s in data['subscribers'] if s['email'].lower() == email.lower()]
    if existing:
        return {
            'success': True,
            'already_subscribed': True,
            'email': email
        }
    
    # Add subscriber
    subscriber = {
        'email': email,
        'name': name,
        'source': source,
        'subscribed_at': datetime.now().isoformat(),
        'metadata': metadata or {},
        'drip_sequence_sent': []
    }
    
    data['subscribers'].append(subscriber)
    save_subscribers(data)
    
    # Send to external services
    _send_to_airtable(subscriber)
    _send_to_loops(subscriber)
    
    # Track in analytics
    from analytics import Analytics
    Analytics.track_signup(email, source=source)
    
    return {
        'success': True,
        'email': email,
        'subscriber': subscriber
    }

def _send_to_airtable(subscriber):
    """Send subscriber to Airtable"""
    airtable_api_key = os.getenv('AIRTABLE_API_KEY')
    airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
    airtable_table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Subscribers')
    
    if not airtable_api_key or not airtable_base_id:
        return
    
    try:
        import requests
        
        url = f'https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_name}'
        headers = {
            'Authorization': f'Bearer {airtable_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'fields': {
                'Email': subscriber['email'],
                'Name': subscriber.get('name', ''),
                'Source': subscriber['source'],
                'Subscribed At': subscriber['subscribed_at'],
                'Metadata': json.dumps(subscriber.get('metadata', {}))
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    except Exception as e:
        print(f"Airtable sync error: {e}")
        return None

def _send_to_loops(subscriber):
    """Send subscriber to Loops.so for email automation"""
    loops_api_key = os.getenv('LOOPS_API_KEY')
    
    if not loops_api_key:
        return
    
    try:
        import requests
        
        url = 'https://app.loops.so/api/v1/contacts/create'
        headers = {
            'Authorization': f'Bearer {loops_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'email': subscriber['email'],
            'firstName': subscriber.get('name', '').split()[0] if subscriber.get('name') else '',
            'source': subscriber['source'],
            'userGroup': 'lean_subscribers'
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    except Exception as e:
        print(f"Loops.so sync error: {e}")
        return None

def get_drip_sequence():
    """
    Get email drip sequence outline
    Day 0, 3, 7 cadence
    """
    return [
        {
            'day': 0,
            'subject': 'Welcome to Lean! 🎉',
            'content': '''
Hey {name},

Welcome to Lean! You're about to experience the easiest way to track your nutrition and hit your goals.

Here's what to do first:

1. **Log your first meal** - Use voice, photo, or text. We make it stupid simple.
2. **Set your goal** - Tell us where you want to be, we'll help you get there.
3. **Track daily** - Just 30 seconds per meal. That's it.

Over 1,000 people have already lost weight with Lean. You're next.

Ready to start? [Log your first meal →]

Ross
Founder, Lean
            ''',
            'cta_url': '/dashboard',
            'cta_text': 'Log First Meal'
        },
        {
            'day': 3,
            'subject': 'Your first wins on Lean 💪',
            'content': '''
{name},

You've logged {meals_logged} meals this week - nice work!

Here's what successful Lean users do:

✅ **Log consistently** - Even if it's not perfect
✅ **Hit your protein** - This is the game changer
✅ **Track progress** - Small wins add up

People who log 4+ days in their first week are 3x more likely to hit their goal.

Keep going. You've got this.

[View Your Progress →]

Ross
            ''',
            'cta_url': '/dashboard',
            'cta_text': 'See My Progress'
        },
        {
            'day': 7,
            'subject': 'One week down. Here\'s what\'s next.',
            'content': '''
{name},

You've been using Lean for a week. Here's what the data shows:

📊 **Your Stats:**
- Meals logged: {meals_logged}
- Avg calories: {avg_calories}
- Streak: {streak} days

🎯 **What's Working:**
{whats_working}

🚀 **Upgrade to Pro:**
You're crushing it on the free plan. Ready to unlock unlimited tracking, advanced analytics, and share cards?

[Upgrade to Pro - $4.99/mo →]

or

[Invite a friend, both get 1 month free →]

Keep pushing,
Ross

P.S. - Have questions? Just reply to this email.
            ''',
            'cta_url': '/pricing',
            'cta_text': 'Upgrade to Pro'
        }
    ]

def send_welcome_email(email, name=None):
    """Send immediate welcome email"""
    sequence = get_drip_sequence()
    day_0 = sequence[0]
    
    # In production, this would send via SendGrid/Mailgun
    # For now, just log it
    
    data = load_subscribers()
    
    for sub in data['subscribers']:
        if sub['email'].lower() == email.lower():
            sub['drip_sequence_sent'].append({
                'day': 0,
                'sent_at': datetime.now().isoformat()
            })
            break
    
    save_subscribers(data)
    
    return {
        'success': True,
        'email': email,
        'subject': day_0['subject']
    }

def get_subscriber_stats():
    """Get subscriber statistics"""
    data = load_subscribers()
    
    total = len(data['subscribers'])
    by_source = {}
    
    for sub in data['subscribers']:
        source = sub['source']
        by_source[source] = by_source.get(source, 0) + 1
    
    # Recent signups (last 7 days)
    from datetime import timedelta
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent = [s for s in data['subscribers'] if s['subscribed_at'] > week_ago]
    
    return {
        'total_subscribers': total,
        'by_source': by_source,
        'last_7_days': len(recent),
        'latest': data['subscribers'][-10:] if data['subscribers'] else []
    }
