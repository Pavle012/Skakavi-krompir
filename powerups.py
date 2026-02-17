import pygame
import json
import random
import os
import time

class Powerup:
    def __init__(self, x, y, type_data):
        self.x = x
        self.y = y
        self.type_data = type_data
        self.rect = pygame.Rect(x, y, 30, 30) # Default size 30x30
        self.color = tuple(type_data.get("color", (255, 255, 255)))
        self.width = 30
        self.height = 30
        
    def update(self, delta, scroll):
        # Update rect to screen coordinates for collision detection
        self.rect.x = int(self.x + scroll)
        
    def draw(self, screen, scroll):
        # Update rect to screen coordinates for drawing
        screen_x = int(self.x + scroll)
        draw_rect = pygame.Rect(screen_x, self.y, self.width, self.height)
        
        # Only draw if on screen
        if screen_x > -50 and screen_x < 1000: # Assuming 800 width + buffer
             pygame.draw.rect(screen, self.color, draw_rect, border_radius=15)
             center = draw_rect.center
             pygame.draw.circle(screen, (255, 255, 255), center, 5)

class PowerupManager:
    def __init__(self, assets_dir):
        self.powerups = []
        self.powerup_types = []
        self.active_effects = {}
        self.assets_dir = assets_dir
        self.load_powerups()
        
    def load_powerups(self):
        try:
            path = os.path.join(self.assets_dir, "powerups.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.powerup_types = json.load(f)
            else:
                print(f"Powerup config not found at {path}")
        except Exception as e:
            print(f"Error loading powerups: {e}")
            
    def spawn_powerup(self, x, y):
        # Weighted random choice based on rarity
        # Rarity is assumed to be a weight (higher = more frequent)
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
             # Randomize Y slightly within the gap? Or passed Y is exact?
             # For now, let's assume Y is the center of the gap.
             self.powerups.append(Powerup(x, y, selected_type))

    def update(self, delta, scroll, player_rect):
        # Update all powerups with current scroll
        for p in self.powerups:
            p.update(delta, scroll)
            
        # Check collisions
        collected_effect = None
        # Use a copy to modify list while iterating
        for p in self.powerups[:]:
            # Simple optimization: only check collision if on screen
            if -50 < p.rect.x < 1000:
                if player_rect.colliderect(p.rect):
                    self.powerups.remove(p)
                    effect = self.apply_effect(p.type_data)
                    # For now just return the last collected one if multiple (unlikely)
                    if effect:
                        collected_effect = effect
                    
        # Update active effects
        expired_effects = []
        current_time = time.time()
        for effect_id, data in self.active_effects.items():
            if current_time > data["end_time"]:
                expired_effects.append(effect_id)
                
        for effect_id in expired_effects:
            del self.active_effects[effect_id]
            
        return collected_effect, expired_effects

    def apply_effect(self, type_data):
        effect_type = type_data.get("effect")
        value = type_data.get("value")
        duration = type_data.get("duration", 0)
        
        if duration > 0:
            # Persistent effect
            self.active_effects[effect_type] = {
                "end_time": time.time() + duration,
                "value": value
            }
            return {"type": effect_type, "value": value, "duration": duration, "active": True}
        else:
            # Instant effect
            return {"type": effect_type, "value": value, "active": False}
    
    def is_effect_active(self, effect_type):
        return effect_type in self.active_effects

    def get_effect_value(self, effect_type, default=None):
        if effect_type in self.active_effects:
            return self.active_effects[effect_type].get("value", default)
        return default

    def draw(self, screen, scroll):
        for p in self.powerups:
            p.draw(screen, scroll)
            
    def reset(self):
        self.powerups = []
        self.active_effects = {}
