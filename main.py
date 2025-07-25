import pygame
import gui
import random
###############################################
########### Flappy Bird-like Game #############
###############################################

HEIGHT = 800
WIDTH = 1200
pygame.init()
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load("assets/potato.png")
velocity = 0
x = 100
y = (HEIGHT // 2) - 200
fps = 60
clock = pygame.time.Clock()
paused = False
scroll = 0

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 200, 0), (self.x, self.y, 50, 300))

################################################
################### Functions ##################
################################################
def isPotatoColliding():
    global y
    if y < 0 or y > HEIGHT - 100:
        return True
    for i in range(100):
        if (300 + scroll) <= x <= (350 + scroll) and (y <= 300 or y >= 500):
            return True
    return False

def spawnPipe():
    global scroll
    randomY = random.randint(-200, 200)
    pipe(300 + scroll, 0 + randomY).draw(screen)
    pipe(300 + scroll, 900 + randomY).draw(screen)

################################################
################### Main Loop ##################
################################################
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not paused:
            if event.key == pygame.K_SPACE:
                velocity = -10
            if event.key == pygame.K_ESCAPE:
                paused = True
                afterpause = gui.pause_screen()
                if afterpause == "exit":
                    running = False
                elif afterpause == "resume":
                    paused = False


    if not paused:
        if y > HEIGHT or isPotatoColliding():
            afterpause = gui.lose_screen()
            if afterpause == "exit":
                running = False
            elif afterpause == "restart":
                y = (HEIGHT // 2) - 200
                velocity = 0
                paused = False
        screen.fill((0, 0, 0))
        for i in range(100):
            spawnPipe()
        velocity += 0.5
        scroll -= 2
        y += velocity
        image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
        clock.tick(fps)
        screen.blit(image, (x, y))
        pygame.display.update()