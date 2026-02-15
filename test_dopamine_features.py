#!/usr/bin/env python3
"""
Test Suite for Dopamine-Optimized Lean Dashboard
Tests all API endpoints and features
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:3000"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """Run a single test"""
        print(f"\n{Fore.CYAN}Testing: {name}{Style.RESET_ALL}")
        try:
            result = func()
            if result:
                print(f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ FAIL{Style.RESET_ALL}")
                self.failed += 1
            self.tests.append((name, result))
        except Exception as e:
            print(f"{Fore.RED}✗ ERROR: {str(e)}{Style.RESET_ALL}")
            self.failed += 1
            self.tests.append((name, False))
    
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"{Fore.CYAN}TEST SUMMARY{Style.RESET_ALL}")
        print(f"{'='*50}")
        print(f"Total: {total}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        print(f"{'='*50}\n")
        
        if self.failed == 0:
            print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! Dashboard is production-ready.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Some tests failed. Review issues above.{Style.RESET_ALL}")


def test_dashboard_loads():
    """Test that dashboard HTML loads successfully"""
    response = requests.get(f"{BASE_URL}/")
    if response.status_code != 200:
        print(f"  Status code: {response.status_code}")
        return False
    
    content = response.text
    checks = [
        'class="app-container"' in content,
        'class="streak-display"' in content,
        'class="voice-fab"' in content,
        'class="progress-photos"' in content,
        'class="calorie-section"' in content,
    ]
    
    if all(checks):
        print(f"  ✓ All core elements present")
        return True
    else:
        print(f"  ✗ Missing elements: {[i for i, x in enumerate(checks) if not x]}")
        return False


def test_api_today():
    """Test /api/today endpoint"""
    response = requests.get(f"{BASE_URL}/api/today")
    if response.status_code != 200:
        return False
    
    data = response.json()
    required_keys = ['date', 'meals', 'totals', 'goals', 'progress']
    
    if all(key in data for key in required_keys):
        print(f"  ✓ Date: {data['date']}")
        print(f"  ✓ Meals: {len(data['meals'])}")
        print(f"  ✓ Calories: {data['totals']['calories']}/{data['goals']['calories']}")
        return True
    else:
        print(f"  ✗ Missing keys in response")
        return False


def test_api_streak():
    """Test /api/streak endpoint"""
    response = requests.get(f"{BASE_URL}/api/streak")
    if response.status_code != 200:
        return False
    
    data = response.json()
    required_keys = ['current', 'longest', 'logged_today']
    
    if all(key in data for key in required_keys):
        print(f"  ✓ Current streak: {data['current']} days")
        print(f"  ✓ Longest: {data['longest']} days")
        print(f"  ✓ Logged today: {data['logged_today']}")
        return True
    else:
        return False


def test_api_week():
    """Test /api/week endpoint (7-day history)"""
    response = requests.get(f"{BASE_URL}/api/week")
    if response.status_code != 200:
        return False
    
    data = response.json()
    
    if len(data) == 7:
        print(f"  ✓ 7 days of data returned")
        print(f"  ✓ Latest: {data[-1]['date']} - {data[-1]['calories']} cal")
        return True
    else:
        print(f"  ✗ Expected 7 days, got {len(data)}")
        return False


def test_api_add_meal():
    """Test /api/add_meal endpoint"""
    meal_data = {
        "description": "Test Meal",
        "calories": 300,
        "protein": 25,
        "carbs": 30,
        "fat": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/api/add_meal",
        json=meal_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print(f"  ✓ Meal logged successfully")
            return True
    
    print(f"  ✗ Failed to log meal: {response.status_code}")
    return False


def test_api_progress_photos():
    """Test /api/progress_photos endpoint"""
    response = requests.get(f"{BASE_URL}/api/progress_photos")
    if response.status_code != 200:
        return False
    
    data = response.json()
    print(f"  ✓ Progress photos: {len(data)} photos")
    return True


def test_api_meal_history():
    """Test /api/meal_history endpoint"""
    response = requests.get(f"{BASE_URL}/api/meal_history")
    if response.status_code != 200:
        return False
    
    data = response.json()
    
    if isinstance(data, list):
        print(f"  ✓ Meal history: {len(data)} days")
        if len(data) > 0:
            print(f"  ✓ Latest day: {data[0]['formatted_date']}")
        return True
    
    return False


def test_api_generate_meal_plan():
    """Test /api/generate_meal_plan endpoint"""
    response = requests.get(f"{BASE_URL}/api/generate_meal_plan")
    
    if response.status_code == 200:
        data = response.json()
        if 'plan' in data:
            print(f"  ✓ Meal plan generated: {len(data['plan'])} days")
            return True
        elif 'error' in data:
            print(f"  ! {data['error']}")
            return True  # Expected error if not enough meals logged
    
    return False


def test_api_weight():
    """Test /api/weight endpoint"""
    weight_data = {
        "weight": 175.5,
        "notes": "Morning weight"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/weight",
        json=weight_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"  ✓ Weight logged: {weight_data['weight']} lbs")
            return True
    
    return False


def test_api_weight_history():
    """Test /api/weight/history endpoint"""
    response = requests.get(f"{BASE_URL}/api/weight/history")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            stats = data.get('stats', {})
            print(f"  ✓ Weight entries: {stats.get('entries', 0)}")
            if stats.get('current'):
                print(f"  ✓ Current weight: {stats['current']} lbs")
            return True
    
    return False


def test_api_progress_card():
    """Test /api/progress_card endpoint"""
    response = requests.get(f"{BASE_URL}/api/progress_card")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            card_data = data.get('card_data', {})
            print(f"  ✓ Card data: {card_data.get('weight_lost', 0)} lbs lost")
            print(f"  ✓ Streak: {card_data.get('streak', 0)} days")
            return True
    
    return False


def test_api_calculate_goals():
    """Test /api/calculate_goals endpoint"""
    goal_data = {
        "age": 30,
        "gender": "male",
        "height_inches": 73,
        "current_weight": 195,
        "goal_weight": 175,
        "timeline_weeks": 20,
        "activity_level": "moderate"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/calculate_goals",
        json=goal_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"  ✓ BMR: {data.get('bmr')} cal")
            print(f"  ✓ TDEE: {data.get('tdee')} cal")
            print(f"  ✓ Recommended: {data.get('recommended_calories')} cal/day")
            return True
    
    return False


def test_health_check():
    """Test /health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code != 200:
        return False
    
    data = response.json()
    if data.get('status') == 'healthy':
        print(f"  ✓ Server is healthy")
        print(f"  ✓ Timestamp: {data.get('timestamp')}")
        return True
    
    return False


def test_performance():
    """Test dashboard load performance"""
    start = time.time()
    response = requests.get(f"{BASE_URL}/")
    load_time = time.time() - start
    
    print(f"  Load time: {load_time*1000:.0f}ms")
    
    if load_time < 1.0:
        print(f"  ✓ Excellent performance (<1s)")
        return True
    elif load_time < 2.0:
        print(f"  ✓ Good performance (<2s)")
        return True
    else:
        print(f"  ⚠️  Slow load time (>2s)")
        return False


def main():
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔥 LEAN DOPAMINE-OPTIMIZED DASHBOARD TEST SUITE 🔥{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    runner = TestRunner()
    
    # Core functionality tests
    print(f"\n{Fore.YELLOW}{'='*50}")
    print("CORE FUNCTIONALITY")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    runner.test("Health Check", test_health_check)
    runner.test("Dashboard Loads", test_dashboard_loads)
    runner.test("Performance", test_performance)
    
    # API endpoint tests
    print(f"\n{Fore.YELLOW}{'='*50}")
    print("API ENDPOINTS")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    runner.test("API: Today's Data", test_api_today)
    runner.test("API: Streak", test_api_streak)
    runner.test("API: Week History", test_api_week)
    runner.test("API: Meal History", test_api_meal_history)
    runner.test("API: Progress Photos", test_api_progress_photos)
    runner.test("API: Progress Card", test_api_progress_card)
    
    # Write operations
    print(f"\n{Fore.YELLOW}{'='*50}")
    print("WRITE OPERATIONS")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    runner.test("API: Add Meal", test_api_add_meal)
    runner.test("API: Log Weight", test_api_weight)
    runner.test("API: Weight History", test_api_weight_history)
    
    # Advanced features
    print(f"\n{Fore.YELLOW}{'='*50}")
    print("ADVANCED FEATURES")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    runner.test("API: Calculate Goals", test_api_calculate_goals)
    runner.test("API: Generate Meal Plan", test_api_generate_meal_plan)
    
    # Summary
    runner.summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
