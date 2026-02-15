#!/usr/bin/env python3
"""
FitTrack Pro - Production Readiness Verification Script

Run this before deploying to production to ensure everything is set up correctly.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_env_example():
    """Check if .env.example has all required variables."""
    required_vars = [
        'SECRET_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_PRICE_ID',
        'STRIPE_WEBHOOK_SECRET',
        'GA_MEASUREMENT_ID',
        'FLASK_ENV'
    ]
    
    if not Path('.env.example').exists():
        print("❌ .env.example missing")
        return False
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    all_present = True
    for var in required_vars:
        if var in content:
            print(f"✅ .env.example contains {var}")
        else:
            print(f"❌ .env.example missing {var}")
            all_present = False
    
    return all_present

def check_syntax(filepath):
    """Check Python file syntax."""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        print(f"✅ Syntax valid: {filepath}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return False

def main():
    print("🔍 FitTrack Pro - Production Readiness Check\n")
    print("=" * 60)
    
    all_checks = []
    
    # Check critical files
    print("\n📂 Critical Files:")
    all_checks.append(check_file_exists('app_production.py', 'Production app'))
    all_checks.append(check_file_exists('requirements_production.txt', 'Production requirements'))
    all_checks.append(check_file_exists('.env.example', 'Environment template'))
    all_checks.append(check_file_exists('Procfile', 'Heroku config'))
    all_checks.append(check_file_exists('railway.json', 'Railway config'))
    all_checks.append(check_file_exists('Dockerfile', 'Docker config'))
    
    # Check templates
    print("\n📄 Templates:")
    all_checks.append(check_file_exists('templates/landing_optimized.html', 'Optimized landing'))
    all_checks.append(check_file_exists('templates/404.html', 'Custom 404'))
    all_checks.append(check_file_exists('templates/500.html', 'Custom 500'))
    all_checks.append(check_file_exists('templates/dashboard_saas.html', 'Dashboard'))
    all_checks.append(check_file_exists('templates/login.html', 'Login page'))
    all_checks.append(check_file_exists('templates/signup.html', 'Signup page'))
    
    # Check documentation
    print("\n📚 Documentation:")
    all_checks.append(check_file_exists('START_HERE.md', 'Start guide'))
    all_checks.append(check_file_exists('PRODUCTION_LAUNCH_CHECKLIST.md', 'Launch checklist'))
    all_checks.append(check_file_exists('PRODUCTION_OPTIMIZATION_SUMMARY.md', 'Optimization summary'))
    all_checks.append(check_file_exists('SECURITY_AUDIT_REPORT.md', 'Security audit'))
    all_checks.append(check_file_exists('ADMIN_GUIDE.md', 'Admin guide'))
    all_checks.append(check_file_exists('MARKETING_GUIDE.md', 'Marketing guide'))
    all_checks.append(check_file_exists('EMAIL_TEMPLATES.md', 'Email templates'))
    all_checks.append(check_file_exists('SUPPORT_FAQ.md', 'Support FAQ'))
    all_checks.append(check_file_exists('PERFORMANCE_BENCHMARKS.md', 'Performance benchmarks'))
    
    # Check environment setup
    print("\n🔐 Environment Configuration:")
    all_checks.append(check_env_example())
    
    # Check Python syntax
    print("\n🐍 Python Syntax:")
    if Path('app_production.py').exists():
        all_checks.append(check_syntax('app_production.py'))
    
    # Check data directory
    print("\n📁 Data Directory:")
    if Path('data').exists():
        print("✅ data/ directory exists")
        all_checks.append(True)
    else:
        print("⚠️  data/ directory will be created on first run")
        all_checks.append(True)  # Not critical, created automatically
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total:
        print(f"\n✅ All checks passed! ({passed}/{total})")
        print("\n🚀 Ready to deploy!")
        print("\nNext steps:")
        print("1. Read START_HERE.md")
        print("2. Follow PRODUCTION_LAUNCH_CHECKLIST.md")
        print("3. Deploy and launch!")
        return 0
    else:
        print(f"\n⚠️  Some checks failed ({passed}/{total} passed)")
        print("\nFix the issues above before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
