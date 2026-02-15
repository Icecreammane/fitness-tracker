#!/usr/bin/env python3
"""
Test script to verify Lean is deployment-ready
Validates configuration, dependencies, and critical endpoints
"""

import os
import json
import sys
from pathlib import Path

def test_files_exist():
    """Verify all required files exist"""
    required_files = [
        'app_pro.py',
        'requirements.txt',
        'Dockerfile',
        'Procfile',
        'railway.json',
        'fitness_data.json',
        'gamification_system.py'
    ]
    
    print("📁 Checking required files...")
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ❌ {file} - MISSING")
        else:
            print(f"  ✅ {file}")
    
    return len(missing) == 0

def test_requirements():
    """Check if requirements.txt has all dependencies"""
    print("\n📦 Checking dependencies...")
    
    with open('requirements.txt') as f:
        reqs = f.read().lower()
    
    required_deps = ['flask', 'gunicorn']
    missing = []
    
    for dep in required_deps:
        if dep in reqs:
            print(f"  ✅ {dep}")
        else:
            missing.append(dep)
            print(f"  ❌ {dep} - MISSING")
    
    # Check if openai is in requirements or Dockerfile
    with open('Dockerfile') as f:
        dockerfile = f.read()
    
    if 'openai' in reqs or 'openai' in dockerfile:
        print(f"  ✅ openai")
    else:
        print(f"  ⚠️  openai - Only in Dockerfile")
    
    return len(missing) == 0

def test_configuration():
    """Validate configuration files"""
    print("\n⚙️  Checking configuration...")
    
    # Check Dockerfile
    with open('Dockerfile') as f:
        dockerfile = f.read()
    
    if 'app_pro:app' in dockerfile:
        print("  ✅ Dockerfile uses app_pro:app")
    else:
        print("  ❌ Dockerfile incorrect")
        return False
    
    # Check Procfile
    with open('Procfile') as f:
        procfile = f.read()
    
    if 'app_pro:app' in procfile:
        print("  ✅ Procfile uses app_pro:app")
    else:
        print("  ❌ Procfile incorrect")
        return False
    
    # Check railway.json
    with open('railway.json') as f:
        railway_config = json.load(f)
    
    if 'app_pro:app' in railway_config.get('deploy', {}).get('startCommand', ''):
        print("  ✅ railway.json uses app_pro:app")
    else:
        print("  ❌ railway.json incorrect")
        return False
    
    return True

def test_app_imports():
    """Test if app can be imported"""
    print("\n🐍 Testing app imports...")
    
    try:
        import app_pro
        print("  ✅ app_pro imports successfully")
        
        # Check if Flask app exists
        if hasattr(app_pro, 'app'):
            print("  ✅ Flask app instance exists")
        else:
            print("  ❌ No Flask app instance found")
            return False
            
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_environment():
    """Check environment variables"""
    print("\n🔐 Checking environment...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        print(f"  ✅ OPENAI_API_KEY set (length: {len(openai_key)})")
    else:
        print("  ⚠️  OPENAI_API_KEY not set (will need to set in Railway)")
    
    return True

def test_data_structure():
    """Validate fitness_data.json structure"""
    print("\n📊 Checking data structure...")
    
    try:
        with open('fitness_data.json') as f:
            data = json.load(f)
        
        required_keys = ['meals', 'settings']
        for key in required_keys:
            if key in data:
                print(f"  ✅ {key} exists")
            else:
                print(f"  ❌ {key} missing")
                return False
        
        print(f"  ℹ️  {len(data['meals'])} meals logged")
        return True
    except Exception as e:
        print(f"  ❌ Data validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Lean Deployment Readiness\n")
    print("=" * 50)
    
    tests = [
        ("Files", test_files_exist),
        ("Requirements", test_requirements),
        ("Configuration", test_configuration),
        ("Environment", test_environment),
        ("Data Structure", test_data_structure),
        ("App Imports", test_app_imports)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("\n📋 TEST SUMMARY\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready to deploy!")
        return 0
    else:
        print("\n⚠️  Some tests failed - fix issues before deploying")
        return 1

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    sys.exit(main())
