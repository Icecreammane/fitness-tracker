#!/usr/bin/env python3
"""
Gamification System for Fitness Tracker
Handles XP, levels, quests, achievements, combos
"""

import json
from datetime import datetime, timedelta
import random

class GamificationEngine:
    
    # XP Values
    XP_MEAL_LOGGED = 10
    XP_UNDER_TARGET = 20
    XP_PROTEIN_HIT = 15
    XP_PERFECT_DAY = 50
    XP_QUEST_COMPLETE = 30
    
    # Level thresholds
    XP_PER_LEVEL = 500
    
    # Combo multipliers
    COMBO_2_MEALS = 1.5
    COMBO_3_MEALS = 2.0
    COMBO_4_MEALS = 3.0
    
    def __init__(self, user_data_file='user_gamification.json'):
        self.data_file = user_data_file
        self.data = self.load_data()
    
    def load_data(self):
        """Load user gamification data"""
        try:
            with open(self.data_file) as f:
                return json.load(f)
        except:
            return {
                'total_xp': 0,
                'level': 1,
                'achievements': [],
                'daily_quests': [],
                'quest_progress': {},
                'today_meals_logged': 0,
                'today_combo': 1.0,
                'streak_days': 0,
                'last_logged_date': None
            }
    
    def save_data(self):
        """Save user gamification data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def calculate_level(self, xp):
        """Calculate level from XP"""
        return (xp // self.XP_PER_LEVEL) + 1
    
    def xp_to_next_level(self):
        """Calculate XP needed for next level"""
        current_level = self.data['level']
        xp_for_next = current_level * self.XP_PER_LEVEL
        xp_earned_in_level = self.data['total_xp'] % self.XP_PER_LEVEL
        return self.XP_PER_LEVEL - xp_earned_in_level
    
    def get_level_title(self, level):
        """Get title for level"""
        if level <= 5:
            return "Beginner Tracker"
        elif level <= 10:
            return "Consistent Logger"
        elif level <= 20:
            return "Dedicated Tracker"
        elif level <= 30:
            return "Fitness Enthusiast"
        elif level <= 50:
            return "Tracking Master"
        else:
            return "Legend"
    
    def log_meal_xp(self, under_target=False, protein_hit=False):
        """Award XP for logging a meal"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if new day
        if self.data['last_logged_date'] != today:
            self.data['today_meals_logged'] = 0
            self.data['today_combo'] = 1.0
            self.data['last_logged_date'] = today
            self.generate_daily_quests()
        
        # Base XP
        base_xp = self.XP_MEAL_LOGGED
        
        # Increment meal count
        self.data['today_meals_logged'] += 1
        
        # Calculate combo multiplier
        meals_today = self.data['today_meals_logged']
        if meals_today >= 4:
            self.data['today_combo'] = self.COMBO_4_MEALS
        elif meals_today >= 3:
            self.data['today_combo'] = self.COMBO_3_MEALS
        elif meals_today >= 2:
            self.data['today_combo'] = self.COMBO_2_MEALS
        
        # Apply combo
        xp_gained = int(base_xp * self.data['today_combo'])
        
        # Bonuses
        bonus_xp = 0
        bonuses = []
        
        if under_target:
            bonus_xp += self.XP_UNDER_TARGET
            bonuses.append('Under Target')
        
        if protein_hit:
            bonus_xp += self.XP_PROTEIN_HIT
            bonuses.append('Protein Goal')
        
        total_xp = xp_gained + bonus_xp
        
        # Add XP
        old_level = self.data['level']
        self.data['total_xp'] += total_xp
        new_level = self.calculate_level(self.data['total_xp'])
        self.data['level'] = new_level
        
        # Check quests
        self.update_quest_progress('log_meals', 1)
        
        # Check for level up
        leveled_up = new_level > old_level
        
        self.save_data()
        
        return {
            'xp_gained': xp_gained,
            'bonus_xp': bonus_xp,
            'total_xp': total_xp,
            'combo': self.data['today_combo'],
            'bonuses': bonuses,
            'leveled_up': leveled_up,
            'new_level': new_level if leveled_up else None,
            'total_xp_now': self.data['total_xp'],
            'level': self.data['level']
        }
    
    def generate_daily_quests(self):
        """Generate 3 random daily quests"""
        quest_pool = [
            {'id': 'log_3_meals', 'name': 'Log 3 meals today', 'target': 3, 'xp': 50},
            {'id': 'stay_under', 'name': 'Stay under calorie target', 'target': 1, 'xp': 30},
            {'id': 'hit_protein', 'name': 'Hit protein goal', 'target': 1, 'xp': 40},
            {'id': 'take_photo', 'name': 'Log a meal with photo', 'target': 1, 'xp': 25},
            {'id': 'log_breakfast', 'name': 'Log breakfast before 10am', 'target': 1, 'xp': 20},
            {'id': 'voice_log', 'name': 'Use voice logging', 'target': 1, 'xp': 20},
        ]
        
        # Pick 3 random quests
        self.data['daily_quests'] = random.sample(quest_pool, 3)
        self.data['quest_progress'] = {q['id']: 0 for q in self.data['daily_quests']}
        self.save_data()
    
    def update_quest_progress(self, quest_type, amount=1):
        """Update progress on a quest"""
        quest_id = f"{quest_type}"
        if quest_id in self.data['quest_progress']:
            self.data['quest_progress'][quest_id] += amount
            
            # Check if quest completed
            for quest in self.data['daily_quests']:
                if quest['id'] == quest_id:
                    if self.data['quest_progress'][quest_id] >= quest['target']:
                        # Award quest XP
                        self.data['total_xp'] += quest['xp']
                        return {'quest_completed': True, 'quest': quest, 'xp_gained': quest['xp']}
        
        return {'quest_completed': False}
    
    def get_streak_flame(self, streak_days):
        """Get flame emoji for streak"""
        if streak_days >= 100:
            return "💎🔥"
        elif streak_days >= 30:
            return "🔥🔥🔥🔥"
        elif streak_days >= 14:
            return "🔥🔥🔥"
        elif streak_days >= 7:
            return "🔥🔥"
        else:
            return "🔥"
    
    def check_achievements(self, streak_days, deficit_total, meals_logged_total):
        """Check for new achievements"""
        achievements = []
        
        # Streak achievements
        if streak_days == 7 and 'week_warrior' not in self.data['achievements']:
            achievements.append({
                'id': 'week_warrior',
                'name': 'Week Warrior',
                'description': '7-day logging streak',
                'rarity': 'bronze'
            })
            self.data['achievements'].append('week_warrior')
        
        if streak_days == 30 and 'month_master' not in self.data['achievements']:
            achievements.append({
                'id': 'month_master',
                'name': 'Month Master',
                'description': '30-day logging streak',
                'rarity': 'silver'
            })
            self.data['achievements'].append('month_master')
        
        if streak_days == 100 and 'century_club' not in self.data['achievements']:
            achievements.append({
                'id': 'century_club',
                'name': 'Century Club',
                'description': '100-day logging streak',
                'rarity': 'gold'
            })
            self.data['achievements'].append('century_club')
        
        # Deficit achievements
        if deficit_total >= 10000 and '10k_banked' not in self.data['achievements']:
            achievements.append({
                'id': '10k_banked',
                'name': '10K Banked',
                'description': '10,000 calorie deficit',
                'rarity': 'silver'
            })
            self.data['achievements'].append('10k_banked')
        
        if achievements:
            self.save_data()
        
        return achievements
    
    def get_dashboard_data(self):
        """Get all gamification data for dashboard"""
        return {
            'level': self.data['level'],
            'total_xp': self.data['total_xp'],
            'xp_to_next': self.xp_to_next_level(),
            'level_title': self.get_level_title(self.data['level']),
            'daily_quests': self.data['daily_quests'],
            'quest_progress': self.data['quest_progress'],
            'today_combo': self.data['today_combo'],
            'achievements': self.data['achievements'],
            'streak_days': self.data['streak_days'],
            'streak_flame': self.get_streak_flame(self.data['streak_days'])
        }


# Usage example
if __name__ == '__main__':
    engine = GamificationEngine()
    
    # Simulate logging a meal
    result = engine.log_meal_xp(under_target=True, protein_hit=True)
    print("Meal logged:")
    print(f"  XP gained: +{result['total_xp']} ({result['xp_gained']} base + {result['bonus_xp']} bonus)")
    print(f"  Combo: {result['combo']}x")
    if result['leveled_up']:
        print(f"  🎉 LEVEL UP! Now level {result['new_level']}")
    
    # Get dashboard data
    dashboard = engine.get_dashboard_data()
    print(f"\nDashboard:")
    print(f"  Level {dashboard['level']}: {dashboard['level_title']}")
    print(f"  XP: {dashboard['total_xp']} ({dashboard['xp_to_next']} to next level)")
    print(f"  Streak: {dashboard['streak_days']} days {dashboard['streak_flame']}")
    print(f"  Today's combo: {dashboard['today_combo']}x")
