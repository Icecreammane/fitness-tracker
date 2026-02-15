#!/usr/bin/env python3
"""
Test script for Lean launch features
Verifies all new endpoints and functionality
"""

import requests
import json
import os
from datetime import datetime

BASE_URL = 'http://localhost:3000'

def test_api_today():
    """Test /api/today endpoint"""
    print("Testing /api/today...")
    try:
        response = requests.get(f'{BASE_URL}/api/today')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Today: {data['totals']['calories']} cal")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_goal_projection():
    """Test /api/goal_projection endpoint"""
    print("\nTesting /api/goal_projection...")
    try:
        response = requests.get(f'{BASE_URL}/api/goal_projection')
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"⚠️  No goals set (expected): {data['error']}")
            else:
                print(f"✅ Progress: {data['lbs_lost']} lbs lost, {data['status_text']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_last_14_days():
    """Test /api/last_14_days endpoint"""
    print("\nTesting /api/last_14_days...")
    try:
        response = requests.get(f'{BASE_URL}/api/last_14_days')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trend data: {len(data)} days")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_export_data():
    """Test /api/export_data endpoint (NEW)"""
    print("\nTesting /api/export_data...")
    try:
        response = requests.get(f'{BASE_URL}/api/export_data')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Export successful")
            print(f"   - Exported at: {data['exported_at']}")
            print(f"   - Version: {data['version']}")
            print(f"   - Meals: {len(data['data']['meals'])}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_shares_directory():
    """Test that shares directory exists"""
    print("\nTesting shares directory...")
    shares_dir = os.path.join(os.path.dirname(__file__), 'static', 'shares')
    if os.path.exists(shares_dir):
        print(f"✅ Shares directory exists: {shares_dir}")
        files = os.listdir(shares_dir)
        print(f"   - Files: {len(files)}")
        return True
    else:
        print(f"❌ Shares directory missing: {shares_dir}")
        return False

def test_dashboard_loads():
    """Test that dashboard HTML loads"""
    print("\nTesting dashboard page...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html = response.text
            
            # Check for key features
            checks = {
                'Onboarding': 'onboarding-overlay' in html,
                'Share button': 'shareProgress()' in html,
                'Settings button': 'openSettings()' in html,
                'Error handling': 'error-message' in html,
                'Loading state': 'loading-spinner' in html,
                'Toast notifications': 'toast' in html,
            }
            
            all_passed = True
            for feature, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {feature}")
                if not passed:
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("LEAN LAUNCH FEATURES TEST SUITE")
    print("=" * 60)
    print("\nMake sure app is running: python3 app_pro.py")
    print("Press Enter to start tests...")
    input()
    
    results = []
    
    # Test all endpoints
    results.append(("API: /api/today", test_api_today()))
    results.append(("API: /api/goal_projection", test_api_goal_projection()))
    results.append(("API: /api/last_14_days", test_api_last_14_days()))
    results.append(("API: /api/export_data (NEW)", test_api_export_data()))
    results.append(("Directory: static/shares", test_shares_directory()))
    results.append(("Dashboard: HTML features", test_dashboard_loads()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for launch!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review issues above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
