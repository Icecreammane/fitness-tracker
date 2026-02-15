#!/usr/bin/env python3
"""
Test production setup before Railway deployment
Run this to verify everything is configured correctly
"""

import os
import sys
import json
from datetime import datetime

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_pass(msg):
    print(f"✅ {msg}")
    return True

def check_fail(msg):
    print(f"❌ {msg}")
    return False

def check_warn(msg):
    print(f"⚠️  {msg}")
    return True

def test_imports():
    """Test all required imports"""
    print_header("Testing Imports")
    
    required_modules = [
        'flask',
        'json',
        'os',
        'datetime',
        'collections',
        'zoneinfo'
    ]
    
    optional_modules = [
        ('openai', 'Voice logging will not work'),
        ('stripe', 'Payment features will not work')
    ]
    
    all_pass = True
    
    # Test required
    for module in required_modules:
        try:
            __import__(module)
            check_pass(f"Required module '{module}' installed")
        except ImportError:
            check_fail(f"Required module '{module}' MISSING")
            all_pass = False
    
    # Test optional
    for module, warning in optional_modules:
        try:
            __import__(module)
            check_pass(f"Optional module '{module}' installed")
        except ImportError:
            check_warn(f"Optional module '{module}' missing - {warning}")
    
    return all_pass

def test_files():
    """Test required files exist"""
    print_header("Testing Files")
    
    required_files = [
        ('requirements.txt', 'Dependencies list'),
        ('Procfile', 'Railway process config'),
        ('railway.json', 'Railway deployment config'),
        ('Dockerfile', 'Container configuration'),
        ('app_pro.py', 'Main application'),
        ('.gitignore', 'Git ignore rules'),
        ('.env.example', 'Environment variables template')
    ]
    
    optional_files = [
        ('fitness_data.json', 'Data file (will be created)'),
        ('.env', 'Environment variables (for local dev)')
    ]
    
    all_pass = True
    
    for filename, description in required_files:
        if os.path.exists(filename):
            check_pass(f"{filename} exists ({description})")
        else:
            check_fail(f"{filename} MISSING ({description})")
            all_pass = False
    
    for filename, description in optional_files:
        if os.path.exists(filename):
            check_pass(f"{filename} exists ({description})")
        else:
            check_warn(f"{filename} missing ({description})")
    
    return all_pass

def test_app_syntax():
    """Test if app_pro.py has valid syntax"""
    print_header("Testing App Syntax")
    
    try:
        import app_pro
        check_pass("app_pro.py imports successfully")
        
        # Check Flask app exists
        if hasattr(app_pro, 'app'):
            check_pass("Flask app object exists")
        else:
            check_fail("Flask app object not found")
            return False
        
        # Check critical routes exist
        routes = [r.rule for r in app_pro.app.url_map.iter_rules()]
        
        critical_routes = ['/health', '/', '/api/today', '/api/add_meal']
        for route in critical_routes:
            if route in routes:
                check_pass(f"Route {route} registered")
            else:
                check_fail(f"Route {route} NOT registered")
                return False
        
        return True
        
    except Exception as e:
        check_fail(f"Failed to import app_pro.py: {e}")
        return False

def test_requirements():
    """Test requirements.txt has all needed packages"""
    print_header("Testing Requirements")
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().lower()
    
    required_packages = [
        'flask',
        'gunicorn',
        'werkzeug'
    ]
    
    recommended_packages = [
        ('openai', 'Voice logging'),
        ('stripe', 'Payments'),
        ('flask-cors', 'CORS support')
    ]
    
    all_pass = True
    
    for package in required_packages:
        if package in requirements:
            check_pass(f"Package '{package}' in requirements.txt")
        else:
            check_fail(f"Package '{package}' MISSING from requirements.txt")
            all_pass = False
    
    for package, feature in recommended_packages:
        if package in requirements:
            check_pass(f"Package '{package}' in requirements.txt ({feature})")
        else:
            check_warn(f"Package '{package}' missing - {feature} won't work")
    
    return all_pass

def test_dockerfile():
    """Test Dockerfile configuration"""
    print_header("Testing Dockerfile")
    
    with open('Dockerfile', 'r') as f:
        dockerfile = f.read()
    
    checks = [
        ('FROM python:', 'Base image specified'),
        ('COPY requirements.txt', 'Requirements copied'),
        ('RUN pip install', 'Dependencies installed'),
        ('COPY . .', 'Application copied'),
        ('CMD', 'Start command specified'),
        ('gunicorn', 'Gunicorn configured'),
        ('app_pro:app', 'Correct app module'),
        ('$PORT', 'Uses Railway PORT variable')
    ]
    
    all_pass = True
    
    for pattern, description in checks:
        if pattern in dockerfile:
            check_pass(f"{description}")
        else:
            check_fail(f"Missing: {description}")
            all_pass = False
    
    return all_pass

def test_railway_json():
    """Test railway.json configuration"""
    print_header("Testing Railway Config")
    
    try:
        with open('railway.json', 'r') as f:
            config = json.load(f)
        
        # Check structure
        if 'build' not in config:
            check_fail("Missing 'build' section")
            return False
        
        if 'deploy' not in config:
            check_fail("Missing 'deploy' section")
            return False
        
        check_pass("railway.json has valid structure")
        
        # Check deploy config
        deploy = config.get('deploy', {})
        
        if 'healthcheckPath' in deploy:
            if deploy['healthcheckPath'] == '/health':
                check_pass("Health check configured correctly")
            else:
                check_warn(f"Health check path is {deploy['healthcheckPath']}")
        else:
            check_warn("No health check configured")
        
        if 'startCommand' in deploy:
            cmd = deploy['startCommand']
            if 'gunicorn' in cmd and '$PORT' in cmd:
                check_pass("Start command looks good")
            else:
                check_warn(f"Start command may need review: {cmd}")
        
        return True
        
    except Exception as e:
        check_fail(f"Failed to parse railway.json: {e}")
        return False

def test_env_example():
    """Test .env.example has all needed variables"""
    print_header("Testing Environment Variables Template")
    
    with open('.env.example', 'r') as f:
        env_example = f.read()
    
    required_vars = [
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    optional_vars = [
        'OPENAI_API_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY'
    ]
    
    all_pass = True
    
    for var in required_vars:
        if var in env_example:
            check_pass(f"Variable {var} documented")
        else:
            check_fail(f"Variable {var} NOT documented")
            all_pass = False
    
    for var in optional_vars:
        if var in env_example:
            check_pass(f"Optional variable {var} documented")
        else:
            check_warn(f"Variable {var} not documented")
    
    return all_pass

def test_gitignore():
    """Test .gitignore protects secrets"""
    print_header("Testing Git Ignore")
    
    with open('.gitignore', 'r') as f:
        gitignore = f.read()
    
    required_patterns = [
        '.env',
        '__pycache__',
        '*.pyc',
        'venv'
    ]
    
    all_pass = True
    
    for pattern in required_patterns:
        if pattern in gitignore:
            check_pass(f"Ignoring {pattern}")
        else:
            check_fail(f"NOT ignoring {pattern} - SECURITY RISK")
            all_pass = False
    
    return all_pass

def generate_report(results):
    """Generate final report"""
    print_header("Production Readiness Report")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print()
    
    if failed_tests == 0:
        print("✅ ALL TESTS PASSED - Ready for Railway deployment!")
        print()
        print("Next steps:")
        print("1. railway login")
        print("2. ./deploy_to_railway.sh")
        print("3. Test live deployment")
        return True
    else:
        print("❌ SOME TESTS FAILED - Fix issues before deploying")
        print()
        print("Failed tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name}")
        print()
        print("Fix these issues, then run this test again.")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Lean Fitness Tracker - Production Setup Test")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    results = {
        "Imports": test_imports(),
        "Files": test_files(),
        "App Syntax": test_app_syntax(),
        "Requirements": test_requirements(),
        "Dockerfile": test_dockerfile(),
        "Railway Config": test_railway_json(),
        "Environment Template": test_env_example(),
        "Git Ignore": test_gitignore()
    }
    
    success = generate_report(results)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
