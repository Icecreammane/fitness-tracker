#!/usr/bin/env python3
"""
Local vision-based macro analyzer using Ollama + LLaVA
Processes food images locally and extracts nutritional information
"""

import sys
import json
import os
import base64
import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "llava:latest"

def encode_image_to_base64(image_path):
    """Encode image to base64 for ollama"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_food_image_local(image_path):
    """
    Analyze a food image using local ollama vision model
    
    Args:
        image_path: Path to the food image
        
    Returns:
        dict: Nutritional information
    """
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Prompt for macro estimation
        prompt = """Analyze this food image and estimate the macros. You are a nutrition expert.

Based on the visual appearance, estimate:
1. What food items are shown
2. Approximate portion size
3. Nutritional breakdown

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{
  "food": "name of food item",
  "portion_size": "estimate with units like '8oz chicken breast' or '1 medium banana'",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fat": number,
  "confidence": "high/medium/low",
  "notes": "any relevant observations"
}

Be conservative with portions if uncertain. Provide your best estimate."""

        # Call ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Ollama API error: {response.status_code}'
            }
        
        # Parse response
        result = response.json()
        text = result.get('response', '').strip()
        
        # Clean up markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        # Try to extract JSON from text
        # Sometimes the model adds extra text, so we look for the JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_text = text[start_idx:end_idx]
            
            # Fix common JSON issues from vision models
            # Replace values like "35g" with just "35" in numeric fields
            import re
            # Fix: "calories": 500, "protein": 35g, → "calories": 500, "protein": 35,
            json_text = re.sub(r'("(?:calories|protein|carbs|fat)":\s*)(\d+(?:\.\d+)?)g\b', r'\1\2', json_text)
            # Fix: "calories": 500cal → "calories": 500
            json_text = re.sub(r'("calories":\s*)(\d+(?:\.\d+)?)(?:cal|kcal)\b', r'\1\2', json_text)
            
            data = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['food', 'calories', 'protein', 'carbs', 'fat']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}',
                        'raw_response': text
                    }
            
            # Ensure numeric fields are numbers (strip units if present)
            for field in ['calories', 'protein', 'carbs', 'fat']:
                value = data[field]
                # If it's a string, try to extract the number
                if isinstance(value, str):
                    # Remove common units (g, mg, cal, kcal, etc.)
                    value = value.lower().replace('g', '').replace('mg', '').replace('cal', '').replace('kcal', '').strip()
                    
                    # Handle ranges like "600 - 700" or "45-50"
                    if '-' in value:
                        parts = value.split('-')
                        try:
                            # Take the average of the range
                            low = float(parts[0].strip())
                            high = float(parts[1].strip())
                            value = (low + high) / 2
                        except:
                            # If parsing fails, try to extract first number
                            import re
                            numbers = re.findall(r'\d+\.?\d*', value)
                            value = numbers[0] if numbers else value
                    
                data[field] = float(value)
            
            return {
                'success': True,
                'data': data
            }
        else:
            return {
                'success': False,
                'error': 'Could not find valid JSON in response',
                'raw_response': text
            }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': 'Failed to parse response as JSON',
            'raw_response': text if 'text' in locals() else None,
            'parse_error': str(e)
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timed out. The model might still be loading.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Could not connect to Ollama. Is it running? (ollama serve)'
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
            'error': 'Usage: local_vision_analyzer.py <image_path>'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(json.dumps({
            'success': False,
            'error': f'Image not found: {image_path}'
        }))
        sys.exit(1)
    
    result = analyze_food_image_local(image_path)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
