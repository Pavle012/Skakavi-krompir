import random
import math
from kivy.graphics import Color, Ellipse

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
        self.x += self.vx * dt * 60 
        self.y -= self.vy * dt * 60  # Y inverted in Kivy compared to pygame for up/down velocity
        self.life -= self.decay * dt
        self.size = max(0, self.size - (self.decay * 5 * dt)) 

    def draw(self):
        if self.life > 0 and self.size > 0:
            Color(self.color[0]/255.0, self.color[1]/255.0, self.color[2]/255.0, self.life)
            Ellipse(pos=(self.x - self.size, self.y - self.size), size=(self.size*2, self.size*2))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, vx, vy, color, size, decay):
        self.particles.append(Particle(x, y, vx, vy, color, size, decay))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0 and p.size > 0]

    def draw(self):
        for p in self.particles:
            p.draw()

    def create_jump_effect(self, x, y):
        amount = random.randint(5, 10)
        for _ in range(amount):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 0) # Upwards
            size = random.uniform(3, 6)
            decay = random.uniform(1.0, 2.5)
            c_val = random.randint(200, 240)
            color = (c_val, c_val, c_val)
            self.add_particle(x, y, vx, vy, color, size, decay)

    def create_collision_effect(self, x, y):
        amount = random.randint(15, 25)
        for _ in range(amount):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(4, 8)
            decay = random.uniform(1.5, 4.0)
            if random.random() < 0.3:
                color = (255, 200, 50)
            elif random.random() < 0.6:
                color = (255, 100, 50)
            else:
                color = (200, 50, 50)
            self.add_particle(x, y, vx, vy, color, size, decay)
    
    def create_pickup_effect(self, x, y):
        amount = random.randint(10, 20)
        for _ in range(amount):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 5)
            decay = random.uniform(1.0, 3.0)
            color = (255, 255, 100)
            self.add_particle(x, y, vx, vy, color, size, decay)
