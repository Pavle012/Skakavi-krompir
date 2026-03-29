import json
import random
import os

from kivy.graphics import Color, RoundedRectangle, Ellipse

class Powerup:
    def __init__(self, x, y, type_data):
        self.x = x
        self.y = y
        self.type_data = type_data
        
        # rect structure purely for math (x, y, w, h)
        self.rect = [x, y, 30, 30] 
        self.color = tuple(type_data.get("color", (255, 255, 255)))
        self.width = 30
        self.height = 30
        
    def update(self, delta, scroll):
        self.rect[0] = self.x + scroll
        self.rect[1] = self.y
        
    def draw(self):
        screen_x = self.x + self.rect[0] - self.x # Which is just self.rect[0]!
        
        if -50 < screen_x < 1000:
            Color(self.color[0]/255.0, self.color[1]/255.0, self.color[2]/255.0, 1)
            RoundedRectangle(pos=(screen_x, self.y), size=(self.width, self.height), radius=[15])
            Color(1, 1, 1, 1)
            Ellipse(pos=(screen_x + self.width/2 - 5, self.y + self.height/2 - 5), size=(10, 10))

class PowerupManager:
    def __init__(self, assets_dir):
        self.powerups = []
        self.powerup_types = []
        self.active_effects = {}
        self.assets_dir = assets_dir
        self.simulated_time = 0.0
        self.load_powerups()
        
    def load_powerups(self):
        try:
            path = os.path.join(self.assets_dir, "powerups.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.powerup_types = json.load(f)
        except Exception as e:
            print(f"Error loading powerups: {e}")
            
    def spawn_powerup(self, x, y):
        if not self.powerup_types:
            return

        total_weight = sum(p.get("rarity", 10) for p in self.powerup_types)
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        selected_type = None
        for p_type in self.powerup_types:
            current_weight += p_type.get("rarity", 10)
            if r <= current_weight:
                selected_type = p_type
                break
        
        if selected_type:
            self.powerups.append(Powerup(x, y, selected_type))

    def _collides(self, r1, r2):
        # r = [x, y, w, h]
        return not (r1[0] > r2[0] + r2[2] or 
                    r1[0] + r1[2] < r2[0] or 
                    r1[1] > r2[1] + r2[3] or 
                    r1[1] + r1[3] < r2[1])

    def update(self, delta, scroll, player_rect):
        self.simulated_time += delta
        for p in self.powerups:
            p.update(delta, scroll)
            
        collected_effect = None
        for p in self.powerups[:]:
            if -50 < p.rect[0] < 1000:
                if self._collides(player_rect, p.rect):
                    self.powerups.remove(p)
                    effect = self.apply_effect(p.type_data)
                    if effect:
                        collected_effect = effect
                    
        expired_effects = []
        for effect_id, data in self.active_effects.items():
            if self.simulated_time > data["end_time"]:
                expired_effects.append(effect_id)
                
        for effect_id in expired_effects:
            del self.active_effects[effect_id]
            
        return collected_effect, expired_effects

    def apply_effect(self, type_data):
        effect_type = type_data.get("effect")
        value = type_data.get("value")
        duration = type_data.get("duration", 0)
        
        if duration > 0:
            self.active_effects[effect_type] = {
                "end_time": self.simulated_time + duration,
                "value": value
            }
            return {"type": effect_type, "value": value, "duration": duration, "active": True}
        else:
            return {"type": effect_type, "value": value, "active": False}
    
    def is_effect_active(self, effect_type):
        return effect_type in self.active_effects

    def get_effect_value(self, effect_type, default=None):
        if effect_type in self.active_effects:
            return self.active_effects[effect_type].get("value", default)
        return default

    def draw(self):
        for p in self.powerups:
            p.draw()
            
    def reset(self):
        self.powerups = []
        self.active_effects = {}
        self.simulated_time = 0.0
