#!/usr/bin/env python3
"""
Telegram food photo handler - integrates with photo_analyzer and fitness tracker
"""

import sys
import json
import requests
from photo_analyzer import analyze_food_image

FITNESS_TRACKER_URL = "http://localhost:3000"

def log_to_tracker(analysis_data):
    """Log analyzed food to fitness tracker"""
    food_data = {
        "description": f"{analysis_data['food']} ({analysis_data['portion_size']})",
        "calories": analysis_data['calories'],
        "protein": analysis_data['protein'],
        "carbs": analysis_data['carbs'],
        "fat": analysis_data['fat']
    }
    
    response = requests.post(
        f"{FITNESS_TRACKER_URL}/api/log-food",
        json=food_data
    )
    
    return response.json()

def format_confirmation(analysis_data):
    """Format a user-friendly confirmation message"""
    food = analysis_data['food']
    portion = analysis_data['portion_size']
    cal = analysis_data['calories']
    protein = analysis_data['protein']
    carbs = analysis_data['carbs']
    fat = analysis_data['fat']
    confidence = analysis_data['confidence']
    
    message = f"""✅ **Logged: {food.title()}**

📊 **Macros:**
• {cal} calories
• {protein}g protein
• {carbs}g carbs
• {fat}g fat

📏 **Portion:** {portion}
🎯 **Confidence:** {confidence}"""
    
    if 'notes' in analysis_data and analysis_data['notes']:
        message += f"\n\n💡 {analysis_data['notes']}"
    
    return message

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: food_photo_handler.py <image_path>'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Step 1: Analyze photo
    result = analyze_food_image(image_path)
    
    if not result['success']:
        print(json.dumps({
            'success': False,
            'error': f"Analysis failed: {result.get('error')}",
            'message': "❌ Sorry, I couldn't analyze that food photo. Please try again or log manually."
        }))
        sys.exit(1)
    
    analysis_data = result['data']
    
    # Step 2: Log to tracker
    try:
        log_result = log_to_tracker(analysis_data)
        
        # Step 3: Format confirmation
        confirmation = format_confirmation(analysis_data)
        
        print(json.dumps({
            'success': True,
            'analysis': analysis_data,
            'logged': log_result,
            'message': confirmation
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
            'analysis': analysis_data,
            'message': f"⚠️ Analyzed but failed to log: {str(e)}"
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
