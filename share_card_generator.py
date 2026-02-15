#!/usr/bin/env python3
"""
Viral Share Card Generator for Lean
Creates Instagram-story-ready progress images
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def generate_progress_card(
    weight_lost,
    weeks,
    current_weight,
    goal_weight,
    output_dir='static/shares',
    user_id='user'
):
    """
    Generate viral progress share card
    Template: "Lost X lbs in Y weeks with @LeanApp"
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Instagram Story dimensions (1080x1920)
    width = 1080
    height = 1920
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (light to dark green)
    for y in range(height):
        progress = y / height
        r = int(240 - progress * 70)  # 240 -> 170
        g = int(255 - progress * 20)  # 255 -> 235
        b = int(240 - progress * 70)  # 240 -> 170
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to load fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 120)
        stat_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 200)
        label_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 50)
        app_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 60)
    except:
        # Fallback to default
        title_font = ImageFont.load_default()
        stat_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        app_font = ImageFont.load_default()
    
    # Main headline
    headline = f"Lost {weight_lost} lbs"
    bbox = draw.textbbox((0, 0), headline, font=stat_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 300),
        headline,
        fill='#1a1a1a',
        font=stat_font
    )
    
    # Timeline
    timeline = f"in {weeks} weeks"
    bbox = draw.textbbox((0, 0), timeline, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 550),
        timeline,
        fill='#333333',
        font=title_font
    )
    
    # Progress bar
    bar_width = 800
    bar_height = 40
    bar_x = (width - bar_width) // 2
    bar_y = 750
    
    total_loss_needed = current_weight - goal_weight + weight_lost
    progress_pct = weight_lost / total_loss_needed if total_loss_needed > 0 else 1.0
    progress_pct = min(progress_pct, 1.0)
    
    # Background bar
    draw.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
        radius=20,
        fill='#e0e0e0'
    )
    
    # Progress fill
    if progress_pct > 0:
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + int(bar_width * progress_pct), bar_y + bar_height],
            radius=20,
            fill='#4CAF50'
        )
    
    # Progress percentage
    progress_text = f"{int(progress_pct * 100)}% to goal"
    bbox = draw.textbbox((0, 0), progress_text, font=label_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 820),
        progress_text,
        fill='#666666',
        font=label_font
    )
    
    # Stats box
    box_y = 950
    box_padding = 40
    
    stats = [
        ('Current', f"{current_weight} lbs"),
        ('Goal', f"{goal_weight} lbs"),
        ('To Go', f"{current_weight - goal_weight:.1f} lbs")
    ]
    
    stat_box_width = 280
    spacing = (width - (stat_box_width * 3)) // 4
    
    for i, (label, value) in enumerate(stats):
        x = spacing + i * (stat_box_width + spacing)
        
        # Box background
        draw.rounded_rectangle(
            [x, box_y, x + stat_box_width, box_y + 160],
            radius=20,
            fill=(255, 255, 255)
        )
        
        # Value (larger)
        bbox = draw.textbbox((0, 0), value, font=title_font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (x + (stat_box_width - text_width) // 2, box_y + 30),
            value,
            fill='#1a1a1a',
            font=title_font
        )
        
        # Label (smaller)
        bbox = draw.textbbox((0, 0), label, font=label_font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (x + (stat_box_width - text_width) // 2, box_y + 110),
            label,
            fill='#666666',
            font=label_font
        )
    
    # App branding
    branding = "Track with Lean"
    bbox = draw.textbbox((0, 0), branding, font=app_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 1600),
        branding,
        fill='#1a1a1a',
        font=app_font
    )
    
    # URL
    url = "lean.app"
    bbox = draw.textbbox((0, 0), url, font=label_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 1700),
        url,
        fill='#4CAF50',
        font=label_font
    )
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"lean_progress_{user_id}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    img.save(filepath, quality=95)
    
    return {
        'success': True,
        'filename': filename,
        'path': filepath,
        'url': f'/static/shares/{filename}'
    }

def generate_milestone_card(milestone_type, value, output_dir='static/shares', user_id='user'):
    """
    Generate milestone celebration cards
    Types: first_meal, 7_day_streak, 10_lbs_lost, goal_reached
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    width = 1080
    height = 1920
    
    # Create image
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # Colorful gradient based on milestone
    colors = {
        'first_meal': ('#FFE5B4', '#FFD700'),  # Golden
        '7_day_streak': ('#E8F5E9', '#4CAF50'),  # Green
        '10_lbs_lost': ('#E3F2FD', '#2196F3'),  # Blue
        'goal_reached': ('#F3E5F5', '#9C27B0')   # Purple
    }
    
    color_start, color_end = colors.get(milestone_type, ('#F5F5F5', '#E0E0E0'))
    
    # Gradient
    for y in range(height):
        progress = y / height
        # Simple linear interpolation between colors
        draw.line([(0, y), (width, y)], fill=color_end)
    
    # Emoji/Icon
    emojis = {
        'first_meal': '🎉',
        '7_day_streak': '🔥',
        '10_lbs_lost': '💪',
        'goal_reached': '🏆'
    }
    
    emoji = emojis.get(milestone_type, '⭐')
    
    try:
        emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 300)
        title_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 90)
        desc_font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 60)
    except:
        emoji_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
    
    # Emoji
    bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 400),
        emoji,
        font=emoji_font,
        embedded_color=True
    )
    
    # Milestone text
    titles = {
        'first_meal': 'First Meal Logged!',
        '7_day_streak': '7 Day Streak!',
        '10_lbs_lost': '10 Pounds Down!',
        'goal_reached': 'Goal Reached!'
    }
    
    title = titles.get(milestone_type, 'Milestone!')
    bbox = draw.textbbox((0, 0), title, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 800),
        title,
        fill='#1a1a1a',
        font=title_font
    )
    
    # Value/description
    if value:
        bbox = draw.textbbox((0, 0), value, font=desc_font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            ((width - text_width) // 2, 950),
            value,
            fill='#555555',
            font=desc_font
        )
    
    # Branding
    branding = "Keep crushing it with Lean"
    bbox = draw.textbbox((0, 0), branding, font=desc_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 1500),
        branding,
        fill='#1a1a1a',
        font=desc_font
    )
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"lean_milestone_{milestone_type}_{user_id}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    img.save(filepath, quality=95)
    
    return {
        'success': True,
        'filename': filename,
        'path': filepath,
        'url': f'/static/shares/{filename}'
    }
