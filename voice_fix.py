import os
import requests

def transcribe_audio_direct(audio_path, api_key):
    """Call Whisper API directly without SDK"""
    import os
    
    # Check file size
    file_size = os.path.getsize(audio_path)
    print(f"Audio file size: {file_size} bytes")
    
    if file_size == 0:
        raise Exception("Audio file is empty")
    
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Try multiple formats - webm might not work, try as mp3
    with open(audio_path, 'rb') as f:
        files = {'file': ('audio.mp3', f, 'audio/mpeg')}
        data = {'model': 'whisper-1'}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()['text']
    else:
        raise Exception(f"Whisper API error: {response.text}")

def _clean_jsonish(content: str) -> str:
    content = content.strip()
    if content.startswith('```'):
        lines = content.split('\n')
        content = '\n'.join([l for l in lines if not l.startswith('```')])
        content = content.strip()
        if content.startswith('json'):
            content = content[4:].strip()
    return content


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
        content = response.json()['choices'][0]['message']['content']
        return _clean_jsonish(content)
    else:
        raise Exception(f"GPT API error: {response.text}")


def analyze_meal_photo_direct(image_bytes: bytes, api_key: str) -> str:
    """Call GPT-4o Vision directly without SDK. Returns JSON string."""
    import base64

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{b64}"

    prompt = (
        "Analyze this meal photo and estimate macros. "
        "If unsure, make a reasonable conservative estimate. "
        "Return ONLY valid JSON (no markdown, no explanation):\n"
        "{\n"
        "  \"food\": \"short description\",\n"
        "  \"portion_size\": \"estimate\",\n"
        "  \"calories\": number,\n"
        "  \"protein\": number,\n"
        "  \"carbs\": number,\n"
        "  \"fat\": number,\n"
        "  \"confidence\": \"high/medium/low\"\n"
        "}"
    )

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        return _clean_jsonish(content)
    else:
        raise Exception(f"Vision API error: {response.text}")
