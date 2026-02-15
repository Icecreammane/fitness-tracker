#!/usr/bin/env python3
"""
Test script for the meal photo macro estimation feature
Downloads sample food images and tests the complete flow
"""

import requests
import json
import time
import os
import sys

# Test configuration
TRACKER_URL = "http://localhost:3000"
TEST_IMAGES = [
    {
        "url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
        "name": "salad_bowl.jpg",
        "description": "Fresh salad bowl"
    },
    {
        "url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800", 
        "name": "burger.jpg",
        "description": "Burger with fries"
    },
    {
        "url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "name": "pasta.jpg",
        "description": "Pasta dish"
    }
]

def download_test_image(image_info):
    """Download a test food image"""
    print(f"📥 Downloading {image_info['description']}...")
    
    response = requests.get(image_info['url'], timeout=30)
    if response.status_code == 200:
        filepath = f"/tmp/{image_info['name']}"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ Saved to {filepath}")
        return filepath
    else:
        print(f"   ❌ Failed to download: {response.status_code}")
        return None

def test_direct_analyzer(image_path):
    """Test the vision analyzer directly"""
    print(f"\n🧪 Testing direct analyzer on {os.path.basename(image_path)}...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['python3', 'local_vision_analyzer.py', image_path],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('success'):
                print("   ✅ Direct analyzer SUCCESS")
                print(f"   🍽️  Food: {data['data']['food']}")
                print(f"   📊 Macros: {data['data']['calories']}cal, {data['data']['protein']}p, {data['data']['carbs']}c, {data['data']['fat']}f")
                return True
            else:
                print(f"   ❌ Analysis failed: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Script error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏱️  Timeout (model may still be loading)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_api_endpoint(image_path, image_description):
    """Test the Flask API endpoint"""
    print(f"\n🧪 Testing API endpoint with {image_description}...")
    
    try:
        # Check if server is running
        response = requests.get(f"{TRACKER_URL}/api/stats", timeout=5)
        if response.status_code != 200:
            print("   ⚠️  Tracker server not responding. Start with: python3 app.py")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Tracker server not running. Start with: python3 app.py")
        return False
    
    # Test photo analysis endpoint
    with open(image_path, 'rb') as f:
        files = {'photo': (os.path.basename(image_path), f, 'image/jpeg')}
        
        print("   📤 Uploading photo...")
        start_time = time.time()
        
        response = requests.post(
            f"{TRACKER_URL}/api/analyze-food-photo",
            files=files,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        print(f"   ⏱️  Analysis took {elapsed:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API endpoint SUCCESS")
                print(f"   🍽️  Food: {data['data']['food']}")
                print(f"   📏 Portion: {data['data'].get('portion_size', 'N/A')}")
                print(f"   📊 Macros: {data['data']['calories']}cal, {data['data']['protein']}p, {data['data']['carbs']}c, {data['data']['fat']}f")
                print(f"   🎯 Confidence: {data['data'].get('confidence', 'N/A')}")
                if data['data'].get('notes'):
                    print(f"   💡 Notes: {data['data']['notes']}")
                return True
            else:
                print(f"   ❌ Analysis failed: {data.get('error')}")
                if data.get('raw_response'):
                    print(f"   📝 Raw: {data['raw_response'][:200]}")
                return False
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏱️  Request timed out (model may be slow to load)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...\n")
    
    issues = []
    
    # Check Ollama
    try:
        result = os.popen('ollama list 2>/dev/null').read()
        if 'llava' in result.lower():
            print("   ✅ Ollama LLaVA model installed")
        else:
            print("   ⚠️  LLaVA model not found")
            issues.append("Run: ollama pull llava:latest")
    except:
        print("   ❌ Ollama not found")
        issues.append("Install Ollama from https://ollama.ai")
    
    # Check if tracker files exist
    if os.path.exists('local_vision_analyzer.py'):
        print("   ✅ Vision analyzer script exists")
    else:
        print("   ❌ local_vision_analyzer.py not found")
        issues.append("Make sure you're in the fitness-tracker directory")
    
    if os.path.exists('app.py'):
        print("   ✅ Flask app exists")
    else:
        print("   ❌ app.py not found")
        issues.append("Make sure you're in the fitness-tracker directory")
    
    return len(issues) == 0, issues

def main():
    print("=" * 60)
    print("🧪 MEAL PHOTO MACRO ESTIMATION - TEST SUITE")
    print("=" * 60)
    
    # Check prerequisites
    prereqs_ok, issues = check_prerequisites()
    if not prereqs_ok:
        print("\n⚠️  Prerequisites not met:")
        for issue in issues:
            print(f"   • {issue}")
        print("\nPlease fix these issues and try again.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("PHASE 1: Download Test Images")
    print("=" * 60)
    
    # Download test images
    test_files = []
    for img in TEST_IMAGES[:2]:  # Just test 2 images to save time
        filepath = download_test_image(img)
        if filepath:
            test_files.append((filepath, img['description']))
    
    if not test_files:
        print("\n❌ Could not download any test images")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("PHASE 2: Test Direct Vision Analyzer")
    print("=" * 60)
    
    # Test direct analyzer
    direct_success = False
    for filepath, desc in test_files:
        if test_direct_analyzer(filepath):
            direct_success = True
            break  # One success is enough
    
    print("\n" + "=" * 60)
    print("PHASE 3: Test API Endpoint")
    print("=" * 60)
    
    # Test API endpoint
    api_success = False
    for filepath, desc in test_files:
        if test_api_endpoint(filepath, desc):
            api_success = True
            break  # One success is enough
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Prerequisites: {'PASS' if prereqs_ok else 'FAIL'}")
    print(f"✅ Direct Analyzer: {'PASS' if direct_success else 'FAIL'}")
    print(f"✅ API Endpoint: {'PASS' if api_success else 'FAIL'}")
    
    if prereqs_ok and direct_success and api_success:
        print("\n🎉 ALL TESTS PASSED! Feature is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Start tracker: python3 app.py")
        print("   2. Open browser: http://localhost:3000")
        print("   3. Click '📸 Snap Food Photo' button")
        print("   4. Upload a meal photo and watch the magic! ✨")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
