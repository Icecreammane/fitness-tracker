#!/usr/bin/env python3
"""
Analytics Integration for Lean
PostHog for event tracking and user analytics
"""

import os
from datetime import datetime

# PostHog client - lazy load
_posthog_client = None

def get_posthog_client():
    """Get or initialize PostHog client"""
    global _posthog_client
    
    if _posthog_client is None:
        try:
            import posthog
            
            api_key = os.getenv('POSTHOG_API_KEY')
            host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
            
            if api_key:
                posthog.api_key = api_key
                posthog.host = host
                _posthog_client = posthog
            else:
                print("Warning: POSTHOG_API_KEY not set, analytics disabled")
                _posthog_client = MockPostHog()
        except ImportError:
            print("Warning: posthog not installed, analytics disabled")
            _posthog_client = MockPostHog()
    
    return _posthog_client

class MockPostHog:
    """Mock PostHog client for when it's not available"""
    def capture(self, *args, **kwargs):
        pass
    
    def identify(self, *args, **kwargs):
        pass

class Analytics:
    """Analytics event tracker"""
    
    @staticmethod
    def track_signup(user_id, source='direct', referral_code=None):
        """Track new user signup"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'signup',
            properties={
                'source': source,
                'referral_code': referral_code,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_meal_logged(user_id, method, calories, protein):
        """
        Track meal logging
        method: 'voice', 'photo', 'text'
        """
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'meal_logged',
            properties={
                'method': method,
                'calories': calories,
                'protein': protein,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_goal_set(user_id, current_weight, goal_weight, timeline_weeks):
        """Track when user sets their goal"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'goal_set',
            properties={
                'current_weight': current_weight,
                'goal_weight': goal_weight,
                'weight_to_lose': current_weight - goal_weight,
                'timeline_weeks': timeline_weeks,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_share_generated(user_id, share_type, weight_lost=None):
        """
        Track share card generation
        share_type: 'progress', 'milestone'
        """
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'share_generated',
            properties={
                'share_type': share_type,
                'weight_lost': weight_lost,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_referral_used(referrer_id, new_user_id, referral_code):
        """Track when a referral code is used"""
        posthog = get_posthog_client()
        
        # Track for referrer
        posthog.capture(
            referrer_id,
            'referral_used',
            properties={
                'new_user_id': new_user_id,
                'referral_code': referral_code,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Track for new user
        posthog.capture(
            new_user_id,
            'referred_signup',
            properties={
                'referrer_id': referrer_id,
                'referral_code': referral_code,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_subscription_started(user_id, plan, amount):
        """Track subscription purchase"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'subscription_started',
            properties={
                'plan': plan,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_page_view(user_id, page, referrer=None):
        """Track page views"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'page_view',
            properties={
                'page': page,
                'referrer': referrer,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def identify_user(user_id, email=None, name=None, created_at=None):
        """Identify user with properties"""
        posthog = get_posthog_client()
        
        properties = {}
        if email:
            properties['email'] = email
        if name:
            properties['name'] = name
        if created_at:
            properties['created_at'] = created_at
        
        posthog.identify(user_id, properties)
    
    @staticmethod
    def track_milestone(user_id, milestone_type, value):
        """Track milestone achievements"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'milestone_achieved',
            properties={
                'milestone_type': milestone_type,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def track_streak(user_id, days):
        """Track logging streaks"""
        posthog = get_posthog_client()
        posthog.capture(
            user_id,
            'streak_updated',
            properties={
                'days': days,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def get_dashboard_url():
        """Get PostHog dashboard URL"""
        return os.getenv('POSTHOG_DASHBOARD_URL', 'https://app.posthog.com')
