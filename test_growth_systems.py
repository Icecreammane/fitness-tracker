#!/usr/bin/env python3
"""
Quick test script for Growth Engine systems
Run this to verify all systems are working
"""

import sys
import os

def test_referral_system():
    """Test referral system"""
    print("\n=== Testing Referral System ===")
    try:
        from referral_system import generate_referral_code, track_referral, get_user_referral_stats
        
        # Generate code
        code = generate_referral_code('test_user_1')
        print(f"✅ Generated referral code: {code}")
        
        # Track referral
        result = track_referral(code, 'test_user_2')
        print(f"✅ Tracked referral: {result}")
        
        # Get stats
        stats = get_user_referral_stats('test_user_1')
        print(f"✅ Referral stats: {stats['total_referrals']} referrals")
        
        return True
    except Exception as e:
        print(f"❌ Referral system error: {e}")
        return False

def test_share_cards():
    """Test share card generation"""
    print("\n=== Testing Share Card Generation ===")
    try:
        from share_card_generator import generate_progress_card
        
        result = generate_progress_card(
            weight_lost=10,
            weeks=8,
            current_weight=180,
            goal_weight=165,
            user_id='test_user'
        )
        
        if result['success']:
            print(f"✅ Generated share card: {result['filename']}")
            print(f"   Saved to: {result['path']}")
            return True
        else:
            print(f"❌ Share card generation failed")
            return False
    except Exception as e:
        print(f"❌ Share card error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics():
    """Test analytics system"""
    print("\n=== Testing Analytics ===")
    try:
        from analytics import Analytics
        
        # Track test events
        Analytics.track_signup('test_user', source='test')
        print("✅ Tracked signup event")
        
        Analytics.track_meal_logged('test_user', 'voice', 450, 35)
        print("✅ Tracked meal_logged event")
        
        Analytics.track_goal_set('test_user', 200, 180, 12)
        print("✅ Tracked goal_set event")
        
        print("📊 Check PostHog dashboard for events (if configured)")
        return True
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_payment_system():
    """Test payment system"""
    print("\n=== Testing Payment System ===")
    try:
        from payment_system import get_user_tier, check_usage_limit, get_pricing
        
        # Check tier
        tier = get_user_tier('test_user')
        print(f"✅ User tier: {tier}")
        
        # Check usage
        can_log, remaining = check_usage_limit('test_user')
        print(f"✅ Usage limit: {remaining} meals remaining" if remaining > 0 else "✅ Unlimited meals")
        
        # Get pricing
        pricing = get_pricing()
        print(f"✅ Pricing loaded: {len(pricing)} plans")
        
        print("💳 Stripe integration ready (add API keys to .env)")
        return True
    except Exception as e:
        print(f"❌ Payment system error: {e}")
        return False

def test_email_system():
    """Test email capture system"""
    print("\n=== Testing Email System ===")
    try:
        from email_system import capture_email, get_subscriber_stats
        
        # Capture test email
        result = capture_email('test@example.com', source='test', name='Test User')
        print(f"✅ Email captured: {result['email']}")
        
        # Get stats
        stats = get_subscriber_stats()
        print(f"✅ Total subscribers: {stats['total_subscribers']}")
        
        print("📧 Email automation ready (configure Loops.so/Airtable in .env)")
        return True
    except Exception as e:
        print(f"❌ Email system error: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n=== Environment Check ===")
    
    required_vars = {
        'OPENAI_API_KEY': 'Required for voice/photo logging',
    }
    
    optional_vars = {
        'POSTHOG_API_KEY': 'Analytics',
        'STRIPE_SECRET_KEY': 'Payments',
        'AIRTABLE_API_KEY': 'Email sync',
        'LOOPS_API_KEY': 'Email automation'
    }
    
    print("\nRequired:")
    for var, desc in required_vars.items():
        status = "✅" if os.getenv(var) else "⚠️"
        print(f"{status} {var} - {desc}")
    
    print("\nOptional:")
    for var, desc in optional_vars.items():
        status = "✅" if os.getenv(var) else "  "
        print(f"{status} {var} - {desc}")

def main():
    print("=" * 60)
    print("Lean Growth Engine - System Test")
    print("=" * 60)
    
    # Check environment
    check_environment()
    
    # Run tests
    results = {
        'Referral System': test_referral_system(),
        'Share Cards': test_share_cards(),
        'Analytics': test_analytics(),
        'Payment System': test_payment_system(),
        'Email System': test_email_system()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for system, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {system}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All systems operational!")
        print("\nNext steps:")
        print("1. Add API keys to .env (see GROWTH.md)")
        print("2. Run: python app_pro.py")
        print("3. Visit: http://localhost:3000/settings")
        print("4. Test referral and share features")
    else:
        print("\n⚠️  Some systems need attention")
        print("Check errors above and refer to GROWTH.md")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
