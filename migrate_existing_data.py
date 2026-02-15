#!/usr/bin/env python3
"""
Migration script to import Ross's existing fitness data into the SaaS version.

Usage:
    python migrate_existing_data.py <your_email> <password>

Example:
    python migrate_existing_data.py ross@example.com mypassword123
"""

import sys
import json
import os
from app_saas import create_user, save_user_data

def migrate_data(email, password):
    """Migrate existing fitness_data.json to new user account."""
    
    # Check if old data file exists
    old_data_file = 'fitness_data.json'
    if not os.path.exists(old_data_file):
        print(f"❌ Error: {old_data_file} not found")
        print("Make sure you're in the fitness-tracker directory")
        return False
    
    # Load old data
    print(f"📂 Loading data from {old_data_file}...")
    with open(old_data_file, 'r') as f:
        old_data = json.load(f)
    
    print(f"✓ Found {len(old_data.get('workouts', []))} workouts")
    print(f"✓ Found {len(old_data.get('food_logs', []))} food logs")
    print(f"✓ Found {len(old_data.get('weight_logs', []))} weight logs")
    
    # Create new user
    print(f"\n👤 Creating user account: {email}")
    try:
        user = create_user(email, password)
        print(f"✓ User created with ID: {user.id}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        print("User might already exist. Try logging in instead.")
        return False
    
    # Save old data to new user's file
    print(f"\n💾 Migrating data to user {user.id}...")
    save_user_data(user.id, old_data)
    
    print(f"✓ Data migrated successfully!")
    print(f"\n🎉 Migration complete!")
    print(f"\nYou can now:")
    print(f"1. Start the app: ./start.sh")
    print(f"2. Login with: {email}")
    print(f"3. Your existing data will be there!")
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python migrate_existing_data.py <email> <password>")
        print("\nExample:")
        print("  python migrate_existing_data.py ross@example.com mypassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    print("🚀 FitTrack Pro - Data Migration")
    print("=" * 50)
    
    if migrate_data(email, password):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
