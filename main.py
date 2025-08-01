import pygame
import gui
import random
import namecheck
import datetime

###############################################
############ Flappy Bird-like Game ############
###############################################

name = namecheck.getname()
HEIGHT = 800
WIDTH = 1200
pygame.init()
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load("assets/potato.png")
velocity = 0
x = 100
y = (HEIGHT // 2)
fps = 60
clock = pygame.time.Clock()
paused = False
points = 0
font = pygame.font.Font("assets/font.ttf", 36)
text_str = f"Points: {points}"
text = font.render(text_str, True, (255, 255, 255))

scroll = 500
PIPE_SPACING = 300
pipesPos = []
pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
for i in range(200):
    randomY = random.randint(-100, 100)
    pipesPos.append((100 + (i * PIPE_SPACING), 0 + randomY))
    pipesPos.append((100 + (i * PIPE_SPACING), 600 + randomY))

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, pipeColor, (self.x, self.y, 50, 300))

################################################
################### Functions ##################
################################################
def isPotatoColliding():
    potatoRect = pygame.Rect(x, y, 2360 // 30, 1745 // 30)
    for px, py in pipesPos:
        realX = px + scroll
        pipeRect = pygame.Rect(realX, py, 50, 300)
        if potatoRect.colliderect(pipeRect):
            return True
    return False


def spawnPipe():
    for px, py in pipesPos:
        realX = px + scroll
        pipe(realX, py).draw(screen)

def getSettings(key):
    settings = {}
    with open("settings.txt") as f:
        for line in f:
            if "=" in line:
                k, value = line.strip().split("=", 1)
                settings[k] = value
    return settings.get(key)

def reloadSettings():
    global scrollPixelsPerFrame, jumpVelocity
    scrollPixelsPerFrame = int(getSettings("scrollPixelsPerFrame")) if getSettings("scrollPixelsPerFrame") else 2
    jumpVelocity = int(getSettings("jumpVelocity")) if getSettings("jumpVelocity") else 12

def appendScore(score):
    with open("scores.txt", "a") as f:
        f.write(f"{score}\n")


################################################
################### Main Loop ##################
################################################

reloadSettings()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not paused:
            if event.key == pygame.K_SPACE:
                velocity = -jumpVelocity
            if event.key == pygame.K_ESCAPE:
                paused = True
                afterpause = gui.pause_screen()
                if afterpause == "exit":
                    running = False
                elif afterpause == "resume":
                    paused = False
        if event.type == pygame.MOUSEBUTTONDOWN and not paused:
            velocity = -jumpVelocity

    if not paused:
        screen.fill((66, 183, 237))

        spawnPipe()
        if (-scroll // PIPE_SPACING) < 0:
            points = 0
        else:
            points = -scroll // PIPE_SPACING + 1
        text_str = f"Points: {points}"
        text = font.render(text_str, True, (255, 255, 255))

        velocity += 0.5
        scroll -= scrollPixelsPerFrame
        y += velocity
        image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
        clock.tick(fps)
        screen.blit(image, (x, y))
        screen.blit(text, (WIDTH - text.get_width() - 10, 10))
        if y > HEIGHT or y < 0 or isPotatoColliding():
            paused = True
            appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
            reloadSettings()
            afterpause = gui.lose_screen()
            if afterpause == "exit":
                running = False
            elif afterpause == "restart":
                pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                x = 100
                y = (HEIGHT // 2)
                velocity = 0
                scroll = 500
                pipesPos = []
                for i in range(100):
                    randomY = random.randint(-100, 100)
                    pipesPos.append((100 + (i * PIPE_SPACING), 0 + randomY))
                    pipesPos.append((100 + (i * PIPE_SPACING), 600 + randomY))
                paused = False
        pygame.display.update()

pygame.quit()
