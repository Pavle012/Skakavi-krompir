import pygame
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color, size, decay):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.decay = decay
        self.life = 1.0

    def update(self, dt):
        """Update particle state. dt is time delta in seconds."""
        self.x += self.vx * dt * 60  # Scale by 60 to match game's frame-based physics feel
        self.y += self.vy * dt * 60
        self.life -= self.decay * dt
        # Shrink over time
        self.size = max(0, self.size - (self.decay * 5 * dt)) 

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            # Simple circle drawing
            # Ensure coordinates are integers
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, vx, vy, color, size, decay):
        self.particles.append(Particle(x, y, vx, vy, color, size, decay))

    def update(self, dt):
        """Update all particles."""
        for p in self.particles:
            p.update(dt)
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0 and p.size > 0]

    def draw(self, surface):
        """Draw all particles."""
        for p in self.particles:
            p.draw(surface)

    def create_jump_effect(self, x, y):
        """Create a dust cloud effect at the given position."""
        amount = random.randint(5, 10)
        for _ in range(amount):
            vx = random.uniform(-2, 2)
            vy = random.uniform(0, 2) 
            size = random.uniform(3, 6)
            decay = random.uniform(1.0, 2.5)
            # Grayish white
            c_val = random.randint(200, 240)
            color = (c_val, c_val, c_val)
            self.add_particle(x, y, vx, vy, color, size, decay)

    def create_collision_effect(self, x, y):
        """Create an explosion effect at the given position."""
        amount = random.randint(15, 25)
        for _ in range(amount):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(4, 8)
            decay = random.uniform(1.5, 4.0)
            # Orange/Red/Yellow mix
            if random.random() < 0.3:
                color = (255, 200, 50) # Yellow
            elif random.random() < 0.6:
                color = (255, 100, 50) # Orange
            else:
                color = (200, 50, 50) # Red
                
            self.add_particle(x, y, vx, vy, color, size, decay)
    
    def create_pickup_effect(self, x, y):
        """Create a sparkle effect (for future powerups)."""
        amount = random.randint(10, 20)
        for _ in range(amount):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 5)
            decay = random.uniform(1.0, 3.0)
            color = (255, 255, 100) # Gold/Yellow
            self.add_particle(x, y, vx, vy, color, size, decay)
