import os
import requests

def transcribe_audio_direct(audio_path, api_key):
    """Call Whisper API directly without SDK"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Ensure file has correct extension for Whisper
    with open(audio_path, 'rb') as f:
        files = {'file': ('audio.webm', f, 'audio/webm')}
        data = {'model': 'whisper-1'}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()['text']
    else:
        raise Exception(f"Whisper API error: {response.text}")

def parse_meal_direct(text, api_key):
    """Call GPT API directly without SDK"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user",
            "content": f"""Parse this meal description and provide macro estimates.

User said: "{text}"

Return ONLY valid JSON (no markdown, no explanation):
{{
  "food": "parsed food name",
  "portion_size": "estimated portion",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fat": number,
  "confidence": "high/medium/low"
}}"""
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content'].strip()
        # Clean markdown if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join([l for l in lines if not l.startswith('```')])
            content = content.strip()
            if content.startswith('json'):
                content = content[4:].strip()
        return content
    else:
        raise Exception(f"GPT API error: {response.text}")
