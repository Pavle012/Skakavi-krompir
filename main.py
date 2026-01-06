import sys
import dependencies
from dependencies import is_compiled

if not is_compiled():
    dependencies.checkifdepend()
    dependencies.fetch_assets()
dependencies.install_configs()
dependencies.load_global_icon_pil()

import pygame
import gui
import scores
import random
import namecheck
import modloader
import datetime
import os
from typing import Optional

paused = False  # initialize before use because of type checking
x = 100         # default x (restart() will overwrite)
y = 0           # default y (restart() will overwrite)
points = 0      # default points (restart() will overwrite)
velocity = 0    # etc.
scroll = 500
speed_increase = 3

###############################################
############ Flappy Bird-like Game ############
###############################################

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y, is_top):
        self.x = x
        self.y = y
        self.is_top = is_top

    def draw(self, screen):
        if self.is_top:
            pygame.draw.rect(screen, pipeColor, (self.x, 0, 50, self.y + 300))
        else:
            pygame.draw.rect(screen, pipeColor, (self.x, self.y, 50, HEIGHT - self.y))

################################################
################### Functions ##################
################################################


def restart():
    global scrollPixelsPerFrame, jumpVelocity, velocity, x, y, maxfps, clock, paused, points, text_str, text, pipeNumber, scroll, PIPE_SPACING, pipesPos, pipeColor, image, WIDTH, HEIGHT
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
    pipeNumber = 500
    scroll = 500
    PIPE_SPACING = 300
    GAP_SIZE = 300
    pipesPos = []
    pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for i in range(pipeNumber):
        randomY = random.randint(-100, 100)
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -750 + randomY, True))
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -150 + randomY, False))
    
    # Reload the image in case it was changed
    image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
    image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
    modloader.trigger_on_restart()


def isPotatoColliding(potato_surface, potato_rect):
    global pipesPos, scroll
    # Create a mask from the rotated potato surface.
    potato_mask = pygame.mask.from_surface(potato_surface)

    # Iterate over each pipe.
    for px, py, is_top in pipesPos:
        realX = px + scroll
        
        # Optimization: Only check pipes that are roughly on screen
        if realX < -100 or realX > WIDTH + 100:
            continue

        if is_top:
            p_height = py + 300
            if p_height <= 0:
                continue
            pipe_rect = pygame.Rect(realX, 0, 50, p_height)
            # First, a simple and fast bounding box check.
            if not potato_rect.colliderect(pipe_rect):
                continue
            pipe_mask = pygame.mask.Mask((50, p_height), fill=True)
        else:
            p_height = HEIGHT - py
            if p_height <= 0:
                continue
            pipe_rect = pygame.Rect(realX, py, 50, p_height)
            # First, a simple and fast bounding box check.
            if not potato_rect.colliderect(pipe_rect):
                continue
            pipe_mask = pygame.mask.Mask((50, p_height), fill=True)

        # Calculate the offset between the potato and the pipe.
        offset = (pipe_rect.x - potato_rect.x, pipe_rect.y - potato_rect.y)

        # Check for overlap between the masks.
        if potato_mask.overlap(pipe_mask, offset):
            return True # Collision detected

    return False # No collision


def spawnPipe():
    global pipesPos, scroll, pipeColor, screen
    for px, py, is_top in pipesPos:
        realX = px + scroll
        pipe(realX, py, is_top).draw(screen)

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
    global scrollPixelsPerFrame, jumpVelocity, font, maxfps, speed_increase
    def _get_int_setting(key: str, default: int) -> int:
        val = getSettings(key)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"Invalid integer for {key}: {val}. Using default {default}.", flush=True)
            return default

    def _get_float_setting(key: str, default: float) -> float:
        val = getSettings(key)
        if val is None:
            return default
        try:
            return float(val)
        except ValueError:
            print(f"Invalid float for {key}: {val}. Using default {default}.", flush=True)
            return default

    scrollPixelsPerFrame = _get_int_setting("scrollPixelsPerFrame", 2)
    jumpVelocity = _get_int_setting("jumpVelocity", 12)
    maxfps = _get_int_setting("maxFps", 60)
    font = pygame.font.Font(dependencies.get_font_path(), 36)
    rememberName = getSettings("rememberName") == "True"
    speed_increase = _get_float_setting("speed_increase", 3.0)
    

def appendScore(score):
    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    with open(scores_path, "a") as f:
        f.write(f"{score}\n")

################################################
##################### Init #####################
################################################

import customtkinter as ctk

# Create a hidden root window
root = ctk.CTk()
root.withdraw()

rememberName = getSettings("rememberName") == "True"

if rememberName:
    name = getSettings("name")
else:
    name = namecheck.getname(root)

if gui.main_menu(root) == "exit":
    sys.exit()
    
HEIGHT = 400
WIDTH = 800
pygame.init()
modloader.load_mods()
font = pygame.font.Font(dependencies.get_font_path(), 36)
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
pygame.display.set_icon(image)

################################################
################### Main Loop ##################
################################################

restart()
running = True
just_resumed = False

while running:
    try:
        root.update()
        root.update_idletasks()
    except:
        pass
    for event in pygame.event.get():
        modloader.trigger_on_event(event)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN and not paused:
            if event.key == pygame.K_SPACE:
                velocity = -jumpVelocity
            if event.key == pygame.K_ESCAPE:
                paused = True
                afterpause = gui.pause_screen(root)
                if afterpause == "exit":
                    running = False
                elif afterpause == "resume":
                    # If potato is in a losing state, show lose screen immediately
                    angle = max(min(velocity * -2.5, 30), -90)
                    rotated_image_on_resume = pygame.transform.rotate(image, angle)
                    rotated_rect_on_resume = rotated_image_on_resume.get_rect(center=image.get_rect(topleft=(x, y)).center)
                    if y > HEIGHT or y < 0 or isPotatoColliding(rotated_image_on_resume, rotated_rect_on_resume):
                        appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                        scores.submit_score(name, points)
                        reloadSettings()
                        afterpause2 = gui.lose_screen(root)
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
            delta = clock.tick(maxfps) / 1000
            just_resumed = False
        else:
            delta = clock.get_time() / 1000
            velocity += 0.5 * delta * 60
            scroll -= scrollPixelsPerFrame * delta * 60
            y += velocity * delta * 60
            clock.tick(maxfps)

        # make the speed go faster over time
        if points % 10 == 0 and points != 0:
            scrollPixelsPerFrame += speed_increase * 0.01 * delta * 60
        
        # --- Rotation and Drawing ---
        # Calculate rotation angle based on vertical velocity.
        angle = max(min(velocity * -2.5, 30), -90)
        # Rotate the master image.
        rotated_image = pygame.transform.rotate(image, angle)
        # Create a new rect for the rotated image, ensuring its center matches the player's logical position.
        rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)

        # Update mod-accessible game state
        game_state_for_mods = {
            "player_pos": (x, y),
            "player_velocity": velocity,
            "player_rect": rotated_rect,
            "player_surface": rotated_image,
            "pipes": pipesPos,
            "scroll": scroll,
            "width": WIDTH,
            "height": HEIGHT,
            "points": points,
            "pipe_spacing": PIPE_SPACING,
            "pipe_color": pipeColor
        }
        modloader.update_game_state(game_state_for_mods)

        # Trigger mod hooks
        modloader.trigger_on_update(delta)

        screen.blit(rotated_image, rotated_rect.topleft)
        screen.blit(text, (WIDTH - text.get_width() - 10, 10))
        
        modloader.trigger_on_draw(screen)

        # --- Collision Check ---
        if y > HEIGHT or y < 0 or isPotatoColliding(rotated_image, rotated_rect):
            paused = True
            appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
            scores.submit_score(name, points)
            reloadSettings()
            afterpause = gui.lose_screen(root)
            if afterpause == "exit":
                running = False
            elif afterpause == "restart":
                restart()
                paused = False
        pygame.display.update()

pygame.quit()
