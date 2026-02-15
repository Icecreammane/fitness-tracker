#!/usr/bin/env python3
"""
Photo-based macro analyzer using OpenAI GPT-4o Vision
Processes food images and extracts nutritional information
"""

import sys
import json
import os
import base64
from openai import OpenAI

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_food_image(image_path):
    """
    Analyze a food image and return macro estimates
    
    Args:
        image_path: Path to the food image
        
    Returns:
        dict: Nutritional information
    """
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Detailed analysis prompt
        prompt = """Analyze this food image and provide detailed macro estimates.

You are a nutrition expert. Based on the visual appearance, estimate:
1. What food item(s) are shown
2. Approximate portion size (use common measurements)
3. Nutritional breakdown

Format your response as valid JSON only (no markdown, no code blocks, no explanation):
{
  "food": "name of food item",
  "portion_size": "estimate with units (e.g., 'medium banana ~120g', '8 oz grilled chicken breast', '2 cups cooked rice')",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fat": number,
  "confidence": "high/medium/low",
  "notes": "any relevant observations about preparation, ripeness, or portion accuracy"
}

Be conservative with portions if uncertain. Provide your best estimate based on standard serving sizes.
Return ONLY the JSON object, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # Parse response
        text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join([l for l in lines if not l.startswith('```')])
            text = text.strip()
            if text.startswith('json'):
                text = text[4:].strip()
        
        data = json.loads(text)
        
        return {
            'success': True,
            'data': data
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': 'Failed to parse response as JSON',
            'raw_response': text if 'text' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: photo_analyzer.py <image_path>'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(json.dumps({
            'success': False,
            'error': f'Image not found: {image_path}'
        }))
        sys.exit(1)
    
    result = analyze_food_image(image_path)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
