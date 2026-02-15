#!/usr/bin/env python3
"""
Test script for the 3 new features:
1. Streak Counter API + UI
2. Weight Tracking + Chart
3. Progress Cards Generator
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:3000"

def test_streak_api():
    """Test the streak counter API"""
    print("\n🔥 Testing Streak Counter API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/streak")
        data = response.json()
        
        assert 'current' in data, "Missing 'current' field"
        assert 'longest' in data, "Missing 'longest' field"
        assert 'logged_today' in data, "Missing 'logged_today' field"
        
        print(f"  ✅ Current streak: {data['current']} days")
        print(f"  ✅ Longest streak: {data['longest']} days")
        print(f"  ✅ Logged today: {data['logged_today']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_weight_tracking():
    """Test weight tracking APIs"""
    print("\n⚖️ Testing Weight Tracking APIs...")
    
    try:
        # Test POST /api/weight
        print("  Testing POST /api/weight...")
        weight_data = {
            "weight": 180.5,
            "notes": "Test weigh-in"
        }
        response = requests.post(f"{BASE_URL}/api/weight", json=weight_data)
        data = response.json()
        
        assert data['success'] == True, "POST failed"
        assert 'entry' in data, "Missing entry in response"
        print(f"  ✅ Weight logged: {data['entry']['weight']} lbs")
        
        # Test GET /api/weight/history
        print("  Testing GET /api/weight/history...")
        response = requests.get(f"{BASE_URL}/api/weight/history?days=7")
        data = response.json()
        
        assert data['success'] == True, "GET failed"
        assert 'history' in data, "Missing history"
        assert 'stats' in data, "Missing stats"
        
        print(f"  ✅ Found {len(data['history'])} weight entries")
        if data['stats']['current']:
            print(f"  ✅ Current weight: {data['stats']['current']} lbs")
            print(f"  ✅ Change: {data['stats']['change']} lbs")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_progress_card():
    """Test progress card generator API"""
    print("\n📊 Testing Progress Card Generator...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/progress_card")
        data = response.json()
        
        assert data['success'] == True, "API call failed"
        assert 'card_data' in data, "Missing card_data"
        
        card = data['card_data']
        assert 'weight_lost' in card, "Missing weight_lost"
        assert 'streak' in card, "Missing streak"
        assert 'meals_logged' in card, "Missing meals_logged"
        assert 'avg_deficit' in card, "Missing avg_deficit"
        
        print(f"  ✅ Weight lost: {card['weight_lost']} lbs")
        print(f"  ✅ Streak: {card['streak']} days")
        print(f"  ✅ Meals logged: {card['meals_logged']}")
        print(f"  ✅ Avg deficit: {card['avg_deficit']} cal")
        print(f"  ✅ Period: {card['period']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_dashboard_loads():
    """Test that the dashboard loads with new components"""
    print("\n🏠 Testing Dashboard UI...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        html = response.text
        
        # Check for key components
        assert 'weight_modal.html' in html or 'weight-modal' in html, "Weight modal not included"
        assert 'progress_card_modal.html' in html or 'progress-card-modal' in html, "Progress card modal not included"
        assert 'streak' in html.lower(), "Streak not in dashboard"
        
        print("  ✅ Dashboard loads successfully")
        print("  ✅ Weight modal included")
        print("  ✅ Progress card modal included")
        print("  ✅ Streak counter present")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Lean Fitness Tracker - New Features")
    print("=" * 60)
    
    results = []
    
    # Test 1: Streak Counter
    results.append(("Streak Counter API", test_streak_api()))
    
    # Test 2: Weight Tracking
    results.append(("Weight Tracking", test_weight_tracking()))
    
    # Test 3: Progress Card
    results.append(("Progress Card Generator", test_progress_card()))
    
    # Test 4: Dashboard UI
    results.append(("Dashboard UI", test_dashboard_loads()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All features working!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
