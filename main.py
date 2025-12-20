import sys
import dependencies

if not getattr(sys, "frozen", False):  # not running as PyInstaller exe
    dependencies.checkifdepend()
    dependencies.fetch_assets()
dependencies.install_configs()

import pygame
import gui
import random
import namecheck
import datetime
import os
from typing import Optional

paused = False  # initialize before use because of type checking
x = 100         # default x (restart() will overwrite)
y = 0           # default y (restart() will overwrite)
points = 0      # default points (restart() will overwrite)
velocity = 0    # etc.
scroll = 500

###############################################
############ Flappy Bird-like Game ############
###############################################

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


def restart():
    global scrollPixelsPerFrame, jumpVelocity, velocity, x, y, maxfps, clock, paused, points, text_str, text, pipeNumber, scroll, PIPE_SPACING, pipesPos, pipeColor
    reloadSettings()
    velocity = 0
    x = 100
    y = (HEIGHT // 2)
    maxfps = 60
    clock = pygame.time.Clock()
    paused = False
    points = 0
    text_str = f"Points: {points}"
    text = font.render(text_str, True, (255, 255, 255))
    pipeNumber = 100
    scroll = 500
    PIPE_SPACING = 300
    pipesPos = []
    pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for i in range(pipeNumber):
        randomY = random.randint(-100, 100)
        pipesPos.append((100 + (i * PIPE_SPACING), 0 + randomY))
        pipesPos.append((100 + (i * PIPE_SPACING), 600 + randomY))


def isPotatoColliding():
    global x, y, pipesPos, scroll
    potatoRect = pygame.Rect(x, y, 2360 // 30, 1745 // 30)
    for px, py in pipesPos:
        realX = px + scroll
        pipeRect = pygame.Rect(realX, py, 50, 300)
        if potatoRect.colliderect(pipeRect):
            return True
    return False


def spawnPipe():
    global pipesPos, scroll, pipeColor, screen
    for px, py in pipesPos:
        realX = px + scroll
        pipe(realX, py).draw(screen)

def getSettings(key: str) -> Optional[str]:
    settings = {}
    settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
    with open(settings_path) as f:
        for line in f:
            if "=" in line:
                k, value = line.strip().split("=", 1)
                settings[k] = value
    return settings.get(key)

def reloadSettings():
    global scrollPixelsPerFrame, jumpVelocity, font, maxfps
    def _get_int_setting(key: str, default: int) -> int:
        val = getSettings(key)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"Invalid integer for {key}: {val}. Using default {default}.", flush=True)
            return default

    scrollPixelsPerFrame = _get_int_setting("scrollPixelsPerFrame", 2)
    jumpVelocity = _get_int_setting("jumpVelocity", 12)
    maxfps = _get_int_setting("maxFps", 60)
    font = pygame.font.Font(dependencies.resource_path("assets/font.ttf"), 36)
    rememberName = getSettings("rememberName") == "True"
    

def appendScore(score):
    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    with open(scores_path, "a") as f:
        f.write(f"{score}\n")

################################################
##################### Init #####################
################################################

rememberName = getSettings("rememberName") == "True"

if rememberName:
    name = getSettings("name")###########################################################################################################  
else:
    name = namecheck.getname()
HEIGHT = 800
WIDTH = 1200
pygame.init()
font = pygame.font.Font(dependencies.resource_path("assets/font.ttf"), 36)
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load(dependencies.resource_path("assets/potato.png"))
image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
pygame.display.set_icon(image)

################################################
################### Main Loop ##################
################################################

restart()
running = True
just_resumed = False

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
                    # If potato is in a losing state, show lose screen immediately
                    if y > HEIGHT or y < 0 or isPotatoColliding():
                        appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                        reloadSettings()
                        afterpause2 = gui.lose_screen()
                        if afterpause2 == "exit":
                            running = False
                        elif afterpause2 == "restart":
                            restart()
                            paused = False
                    else:
                        velocity = 0
                        clock.tick(maxfps)  # Reset clock to avoid large delta
                        just_resumed = True
                        paused = False
        if event.type == pygame.MOUSEBUTTONDOWN and not paused:
            velocity = -jumpVelocity

    if not paused:
        screen.fill((66, 183, 237))

        spawnPipe()
        if (-scroll // PIPE_SPACING) < 0:
            points = 0
        else:
            points = int(-scroll // PIPE_SPACING + 1)
        text_str = f"Points: {points}"
        text = font.render(text_str, True, (255, 255, 255))

        if just_resumed:
            clock.tick(maxfps)
            just_resumed = False
        else:
            delta = clock.get_time() / 1000
            velocity += 0.5 * delta * 60
            scroll -= scrollPixelsPerFrame * delta * 60
            y += velocity * delta * 60
            clock.tick(maxfps)

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
                restart()
                paused = False
        pygame.display.update()

pygame.quit()